"""Shared Codex MCP session management utilities with queue-based workers."""

from __future__ import annotations

import asyncio
import json
import logging
import os
import shutil
import threading
from concurrent.futures import TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from typing import Any, Optional

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from agents.shared.tooling.token_utils import TokenUsage, ensure_within_limit
from automation.workflows.lib import default_gateway_args, resolve_gateway_spec

_LOG = logging.getLogger(__name__)


class _CodexNotificationFilter(logging.Filter):
    """Suppress verbose Codex MCP validation warnings emitted by the SDK."""

    _SUPPRESS_TOKEN = "Failed to validate notification"

    def filter(self, record: logging.LogRecord) -> bool:  # pragma: no cover - logging behaviour
        message = record.getMessage()
        if self._SUPPRESS_TOKEN in message and "codex/event" in message:
            return False
        return True


def _filter_gateway_args(args: list[str]) -> list[str]:
    """Return gateway argument list without duplicate server flags."""

    filtered: list[str] = []
    previous = None
    for token in args:
        if token == previous:
            continue
        filtered.append(token)
        previous = token
    return filtered


@dataclass(slots=True)
class CodexMCPCallResult:
    """Normalised response returned by Codex MCP."""

    prompt: str
    text: str
    content: list[dict[str, Any]]
    meta: dict[str, Any]
    token_usage: TokenUsage | None = None
    model: str | None = None


def codex_usage_as_dict(result: CodexMCPCallResult) -> dict[str, Any] | None:
    """Return token usage information as a serialisable dict."""

    usage = result.token_usage
    if usage is None:
        return None
    return {
        "model": result.model,
        "tokens": usage.tokens,
        "limit": usage.limit,
        "buffer": usage.buffer,
        "remaining": usage.remaining,
        "effective_limit": usage.effective_limit,
    }


@dataclass(slots=True)
class _QueueItem:
    payload: dict[str, Any] | None
    future: asyncio.Future | None


class CodexMCPTimeoutError(RuntimeError):
    """Raised when a Codex MCP call does not return within the allowed time."""


class CodexMCPManager:
    """Manages one or more Codex MCP sessions behind a request queue."""

    def __init__(
        self,
        *,
        command: str = "codex",
        args: list[str] | None = None,
        max_concurrent_sessions: int = 1,
    ) -> None:
        self._command = command
        self._args = list(args or ["mcp-server"])
        if not args:
            spec = resolve_gateway_spec()
            gateway_command = spec.command or "mcp"
            resolved_command = shutil.which(gateway_command) or gateway_command
            command_config = json.dumps(resolved_command)
            self._args.extend(["-c", "mcp_servers={}", "-c", f"gateway.command={command_config}"])

            gateway_args = list(spec.args) or default_gateway_args()
            if gateway_args:
                filtered_args = _filter_gateway_args(list(gateway_args))
                config_value = json.dumps(filtered_args, separators=(",", ":"))
                self._args.extend(["-c", f"gateway.args={config_value}"])

            if spec.env:
                env_config = json.dumps(spec.env, separators=(",", ":"))
                self._args.extend(["-c", f"gateway.env={env_config}"])
            if spec.cwd:
                cwd_config = json.dumps(spec.cwd)
                self._args.extend(["-c", f"gateway.cwd={cwd_config}"])

        max_sessions_env = os.environ.get("MAG_CODEX_MCP_MAX_SESSIONS")
        if max_sessions_env is not None:
            try:
                max_concurrent_sessions = int(max_sessions_env)
            except ValueError:  # pragma: no cover - defensive branch
                _LOG.warning(
                    "Invalid MAG_CODEX_MCP_MAX_SESSIONS value '%s'; defaulting to %s",
                    max_sessions_env,
                    max_concurrent_sessions,
                )
        self._max_concurrent_sessions = max(1, max_concurrent_sessions)

        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

        self._request_queue: asyncio.Queue[_QueueItem] | None = None
        self._workers: list[asyncio.Task[Any]] = []
        self._stop_event: asyncio.Event | None = None
        self._ready_event: asyncio.Event | None = None
        self._startup_error: Exception | None = None

        self._filter = _CodexNotificationFilter()
        logging.getLogger().addFilter(self._filter)

        init_future = asyncio.run_coroutine_threadsafe(self._bootstrap(), self._loop)
        try:
            init_future.result()
        except Exception:
            self.close()
            raise

    def _run_loop(self) -> None:  # pragma: no cover - background thread
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _bootstrap(self) -> None:
        self._stop_event = asyncio.Event()
        self._ready_event = asyncio.Event()
        self._request_queue = asyncio.Queue()

        for worker_id in range(self._max_concurrent_sessions):
            task = asyncio.create_task(self._worker(worker_id))
            self._workers.append(task)

        await self._ready_event.wait()
        if self._startup_error is not None:
            raise RuntimeError("Codex MCP worker failed to initialise") from self._startup_error

    async def _worker(self, worker_id: int) -> None:
        params = StdioServerParameters(command=self._command, args=list(self._args))
        try:
            async with stdio_client(params) as (read_stream, write_stream):
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    _LOG.debug(
                        "Codex MCP worker %s initialised (command=%s args=%s)",
                        worker_id,
                        self._command,
                        self._args,
                    )
                    if self._ready_event and not self._ready_event.is_set():
                        self._ready_event.set()

                    while True:
                        assert self._request_queue is not None
                        item = await self._request_queue.get()
                        if item.payload is None:
                            self._request_queue.task_done()
                            break
                        try:
                            result = await session.call_tool("codex", item.payload)
                            processed = self._normalise_result(item.payload, result)
                            assert item.future is not None
                            item.future.set_result(processed)
                        except Exception as exc:  # pragma: no cover - defensive
                            if item.future is not None and not item.future.done():
                                item.future.set_exception(exc)
                            _LOG.exception("Codex MCP worker %s failed: %s", worker_id, exc)
                        finally:
                            self._request_queue.task_done()
        except Exception as exc:  # pragma: no cover - defensive
            _LOG.exception("Codex MCP worker %s crashed: %s", worker_id, exc)
            if self._startup_error is None:
                self._startup_error = exc
            if self._ready_event and not self._ready_event.is_set():
                self._ready_event.set()
        finally:
            _LOG.debug("Codex MCP worker %s stopped", worker_id)

    @staticmethod
    def _normalise_result(payload: dict[str, Any], result: Any) -> CodexMCPCallResult:
        text_chunks: list[str] = []
        content_dump: list[dict[str, Any]] = []
        for item in result.content or []:
            model = item.model_dump()
            content_dump.append(model)
            text = model.get("text")
            if text:
                text_chunks.append(str(text))
        text_output = "\n".join(text_chunks).strip()
        meta_dump = result.meta.model_dump() if result.meta is not None else {}
        return CodexMCPCallResult(
            prompt=str(payload.get("prompt", "")),
            text=text_output,
            content=content_dump,
            meta=meta_dump,
        )

    async def _submit(self, payload: dict[str, Any]) -> CodexMCPCallResult:
        if self._request_queue is None:
            raise RuntimeError("Codex MCP manager is not initialised")
        future: asyncio.Future = self._loop.create_future()
        await self._request_queue.put(_QueueItem(payload=payload, future=future))
        return await future

    def generate(
        self,
        prompt: str,
        *,
        sandbox: str = "read-only",
        approval_policy: str = "never",
        base_instructions: str | None = None,
        config: dict[str, Any] | None = None,
        include_plan_tool: bool | None = None,
        model: str | None = None,
        token_limit: int | None = None,
        token_buffer: int = 0,
        timeout: Optional[float] = None,
    ) -> CodexMCPCallResult:
        """Invoke Codex MCP with the given prompt and configuration."""

        target_model = model or os.environ.get("MAG_CODEX_MODEL", "gpt-5-codex-medium")
        token_usage: TokenUsage | None = None
        if token_limit is not None:
            token_usage = ensure_within_limit(
                prompt,
                model=target_model,
                limit=token_limit,
                buffer=max(token_buffer, 0),
            )
            if token_usage.exceeded:
                raise ValueError(
                    "Codex prompt exceeds token budget: "
                    f"tokens={token_usage.tokens} effective_limit={token_usage.effective_limit} "
                    f"(limit={token_usage.limit}, buffer={token_usage.buffer})"
                )

        payload: dict[str, Any] = {
            "prompt": prompt,
            "sandbox": sandbox,
            "approval-policy": approval_policy,
        }
        if base_instructions:
            payload["base-instructions"] = base_instructions
        if config:
            payload["config"] = config
        if include_plan_tool is not None:
            payload["include-plan-tool"] = include_plan_tool

        timeout_value: Optional[float] = timeout
        if timeout_value is None:
            timeout_env = os.environ.get("MAG_CODEX_MCP_TIMEOUT")
            if timeout_env:
                try:
                    parsed_timeout = float(timeout_env)
                    if parsed_timeout > 0:
                        timeout_value = parsed_timeout
                except ValueError:
                    _LOG.warning("Invalid MAG_CODEX_MCP_TIMEOUT value '%s'; ignoring", timeout_env)

        future = asyncio.run_coroutine_threadsafe(self._submit(payload), self._loop)
        try:
            result = future.result(timeout=timeout_value)
        except FutureTimeoutError as exc:
            future.cancel()
            _LOG.error(
                "Codex MCP call timed out after %s seconds (model=%s, prompt_chars=%s)",
                timeout_value,
                target_model,
                len(prompt),
            )
            raise CodexMCPTimeoutError(
                f"Codex MCP call exceeded timeout ({timeout_value} seconds)"
            ) from exc
        result.token_usage = token_usage
        result.model = target_model
        if token_usage is not None:
            result.meta = dict(result.meta)
            result.meta.setdefault(
                "token_usage",
                {
                    "model": target_model,
                    "tokens": token_usage.tokens,
                    "limit": token_usage.limit,
                    "buffer": token_usage.buffer,
                },
            )
        return result

    def close(self) -> None:
        """Close all Codex MCP workers and stop the event loop."""

        if not self._loop.is_running():
            return

        async def _shutdown() -> None:
            if self._stop_event is not None and not self._stop_event.is_set():
                self._stop_event.set()
            if self._request_queue is not None:
                for _ in self._workers:
                    await self._request_queue.put(_QueueItem(payload=None, future=None))
            if self._workers:
                await asyncio.gather(*self._workers, return_exceptions=True)
                self._workers.clear()

        future = asyncio.run_coroutine_threadsafe(_shutdown(), self._loop)
        future.result()
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)
        logging.getLogger().removeFilter(self._filter)
        _LOG.debug("Codex MCP manager closed")

    @property
    def max_concurrent_sessions(self) -> int:
        """Return the configured maximum number of concurrent sessions."""

        return self._max_concurrent_sessions

    def __del__(self) -> None:  # pragma: no cover - best effort cleanup
        try:
            self.close()
        except Exception:  # pylint: disable=broad-except
            pass


_default_manager: CodexMCPManager | None = None


def _create_manager(max_sessions: int | None = None) -> CodexMCPManager:
    if max_sessions is not None:
        return CodexMCPManager(max_concurrent_sessions=max_sessions)
    return CodexMCPManager()


def get_codex_manager(*, max_sessions: int | None = None) -> CodexMCPManager:
    """Return a process-wide Codex MCP manager instance."""

    global _default_manager
    if _default_manager is None:
        _default_manager = _create_manager(max_sessions)
        return _default_manager

    if (
        max_sessions is not None
        and max_sessions > 0
        and _default_manager.max_concurrent_sessions != max_sessions
    ):
        _LOG.info(
            "Reinitialising Codex MCP manager with max_sessions=%s (was %s)",
            max_sessions,
            _default_manager.max_concurrent_sessions,
        )
        _default_manager.close()
        _default_manager = _create_manager(max_sessions)

    return _default_manager


def shutdown_codex_manager() -> None:
    """Clean up the shared Codex MCP manager."""

    global _default_manager
    if _default_manager is not None:
        _default_manager.close()
        _default_manager = None


import atexit  # noqa: E402

atexit.register(shutdown_codex_manager)
