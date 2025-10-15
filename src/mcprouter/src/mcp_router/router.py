"""MCPRouter implementation with a synchronous surface area."""

from __future__ import annotations

import asyncio
import json
import os
import random
import threading
import time
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from queue import SimpleQueue
from typing import Optional

from .providers.base import BaseProvider, ProviderError
from .providers.dummy_provider import DummyProvider
from .providers.openai_provider import OpenAIProvider
from .redaction import mask_sensitive
from .schemas import AuditRecord, ProviderRequest, ProviderResponse, QueueItem, Result

_DEFAULT_TIMEOUT = 30.0
_DEFAULT_RETRIES = 1
_DEFAULT_BACKOFF = 0.5


@dataclass
class _QueueEntry:
    item: QueueItem
    future: asyncio.Future[ProviderResponse]


class PromptLimitExceeded(RuntimeError):
    """Raised when the prompt would exceed the available budget."""


class MCPRouter(AbstractContextManager["MCPRouter"]):
    """Synchronous facade that proxies requests to an async worker pool."""

    def __init__(
        self,
        provider: BaseProvider,
        *,
        max_sessions: int = 1,
        request_timeout: float = _DEFAULT_TIMEOUT,
        max_retries: int = _DEFAULT_RETRIES,
        backoff_base: float = _DEFAULT_BACKOFF,
        log_dir: Optional[Path] = None,
        log_flush_every: int = 1,
    ) -> None:
        if max_sessions < 1:
            raise ValueError("max_sessions must be at least 1")
        self._provider = provider
        self._max_sessions = max_sessions
        self._request_timeout = request_timeout
        self._max_retries = max_retries
        self._backoff_base = backoff_base
        self._log_dir = (log_dir or Path.cwd()).resolve()
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._queue: asyncio.Queue[_QueueEntry | None] = asyncio.Queue()
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._workers: list[asyncio.Task[None]] = []
        self._closing = threading.Event()
        self._log_path = self._log_dir / "mcp_calls.jsonl"
        self._started = False
        self._audit_writer = _AsyncLineWriter(self._log_path, flush_every=log_flush_every)
        self._audit_writer.start()

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_env(
        cls,
        *,
        log_dir: Optional[Path] = None,
        log_flush_every: Optional[int] = None,
    ) -> "MCPRouter":
        """Create an instance using environment defaults."""

        max_sessions_str = os.getenv("MCP_MAX_SESSIONS")
        try:
            max_sessions = max(1, int(max_sessions_str)) if max_sessions_str else 5
        except (TypeError, ValueError):
            max_sessions = 5
        timeout = float(os.getenv("MCP_REQUEST_TIMEOUT_SEC", str(_DEFAULT_TIMEOUT)))
        retries = int(os.getenv("MCP_MAX_RETRIES", str(_DEFAULT_RETRIES)))
        backoff = float(os.getenv("MCP_BACKOFF_BASE_SEC", str(_DEFAULT_BACKOFF)))
        flush_env = os.getenv("MCP_LOG_FLUSH_EVERY")
        if flush_env is not None:
            try:
                parsed_flush = max(1, int(flush_env))
            except (TypeError, ValueError):
                parsed_flush = 50
        elif log_flush_every is not None:
            parsed_flush = max(1, log_flush_every)
        else:
            parsed_flush = 50
        api_key = os.getenv("OPENAI_API_KEY", "")
        env = os.getenv("ENV", "").lower()
        if api_key:
            provider: BaseProvider = OpenAIProvider(api_key)
        else:
            if env == "production":
                raise ValueError("OPENAI_API_KEY is required when ENV=production")
            provider = DummyProvider()
        return cls(
            provider,
            max_sessions=max_sessions,
            request_timeout=timeout,
            max_retries=retries,
            backoff_base=backoff,
            log_dir=log_dir,
            log_flush_every=parsed_flush,
        )

    # ------------------------------------------------------------------
    # Context manager protocol
    # ------------------------------------------------------------------
    def __enter__(self) -> "MCPRouter":
        self._ensure_started()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def generate(
        self,
        *,
        prompt: str,
        model: str,
        prompt_limit: int,
        prompt_buffer: int,
        sandbox: str,
        approval_policy: str,
        config: Optional[dict] = None,
        timeout_sec: Optional[float] = None,
        retries: Optional[int] = None,
    ) -> Result:
        """Queue a request and block until the result is available."""

        if not self._started:
            self._ensure_started()
        config = dict(config or {})
        timeout = timeout_sec or self._request_timeout
        retry_budget = retries if retries is not None else self._max_retries
        prompt_chars = len(prompt)
        token_estimate = BaseProvider.approx_token_usage(prompt)
        approx_tokens = token_estimate["tokens"]
        if approx_tokens + prompt_buffer > prompt_limit:
            self._log_audit(
                AuditRecord(
                    ts=datetime.now(UTC),
                    model=model,
                    latency_ms=0.0,
                    prompt_chars=prompt_chars,
                    token_usage=token_estimate,
                    status="prompt_limit_exceeded",
                    error="prompt limit exceeded before dispatch",
                )
            )
            deficit = prompt_limit - prompt_buffer
            message = (
                f"prompt requires {approx_tokens} tokens but limit minus buffer is {deficit}"
            )
            raise PromptLimitExceeded(message)

        request = ProviderRequest(
            prompt=prompt,
            model=model,
            sandbox=sandbox,
            approval_policy=approval_policy,
            config=config,
            timeout_sec=timeout,
        )
        queue_item = QueueItem(
            request=request,
            prompt_limit=prompt_limit,
            prompt_buffer=prompt_buffer,
            retries=retry_budget,
            prompt_chars=prompt_chars,
            token_estimate=token_estimate,
        )

        future = asyncio.run_coroutine_threadsafe(self._enqueue(queue_item), self._loop)
        provider_response = future.result()
        meta = dict(provider_response.meta)
        meta.setdefault("provider", self._provider.name)
        meta.setdefault("retries", retry_budget)
        meta.setdefault("token_usage", provider_response.token_usage or token_estimate)
        meta.setdefault("latency_ms", provider_response.latency_ms)
        safe_meta = mask_sensitive(meta)
        return Result(
            text=provider_response.text,
            content=provider_response.content,
            meta=safe_meta,
        )

    def close(self) -> None:
        """Signal the background loop to stop."""

        if not self._started:
            return
        self._closing.set()
        if self._loop and self._loop.is_running():
            for _ in range(len(self._workers)):
                asyncio.run_coroutine_threadsafe(self._queue.put(None), self._loop)
            asyncio.run_coroutine_threadsafe(self._shutdown_workers(), self._loop).result()
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=5)
        closer = getattr(self._provider, "aclose", None)
        if closer is not None:
            try:
                if asyncio.iscoroutinefunction(closer):
                    asyncio.run(closer())
                else:
                    closer()
            except RuntimeError:
                if self._loop and asyncio.iscoroutinefunction(closer):
                    asyncio.run_coroutine_threadsafe(closer(), self._loop).result()
        self._started = False
        self._audit_writer.close()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _ensure_started(self) -> None:
        if self._started:
            return
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop_runner, daemon=True)
        self._thread.start()
        asyncio.run_coroutine_threadsafe(self._start_workers(), self._loop).result()
        self._started = True

    def _loop_runner(self) -> None:
        assert self._loop is not None
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()
        pending = asyncio.all_tasks(self._loop)
        for task in pending:
            task.cancel()
        try:
            self._loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        finally:
            self._loop.close()

    async def _start_workers(self) -> None:
        for index in range(self._max_sessions):
            task = asyncio.create_task(self._worker(index), name=f"mcp-worker-{index}")
            self._workers.append(task)

    async def _shutdown_workers(self) -> None:
        await self._queue.join()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

    async def _enqueue(self, item: QueueItem) -> ProviderResponse:
        assert self._loop is not None
        future: asyncio.Future[ProviderResponse] = self._loop.create_future()
        await self._queue.put(_QueueEntry(item=item, future=future))
        return await future

    async def _worker(self, index: int) -> None:
        worker_name = f"worker-{index}"
        while True:
            entry = await self._queue.get()
            if entry is None:
                self._queue.task_done()
                break
            assert isinstance(entry, _QueueEntry)
            try:
                response = await self._execute(worker_name, entry.item)
            except Exception as exc:  # pylint: disable=broad-except
                entry.future.set_exception(exc)
            else:
                entry.future.set_result(response)
            finally:
                self._queue.task_done()

    async def _execute(self, worker_name: str, queue_item: QueueItem) -> ProviderResponse:
        attempts = queue_item.retries + 1
        last_error: Optional[Exception] = None
        for attempt in range(attempts):
            attempt_start = time.perf_counter()
            try:
                response = await self._provider.agenerate(queue_item.request)
            except ProviderError as exc:
                last_error = exc
                should_retry = exc.retriable and attempt < attempts - 1
            except Exception as exc:  # pylint: disable=broad-except
                last_error = exc
                should_retry = attempt < attempts - 1
            else:
                latency_ms = (time.perf_counter() - attempt_start) * 1000
                if response.latency_ms is None:
                    response.latency_ms = latency_ms
                self._log_audit(
                    AuditRecord(
                        ts=datetime.now(UTC),
                        model=queue_item.request.model,
                        worker=worker_name,
                        latency_ms=latency_ms,
                        prompt_chars=queue_item.prompt_chars,
                        token_usage=response.token_usage or queue_item.token_estimate,
                        status="ok",
                    )
                )
                return response
            latency_ms = (time.perf_counter() - attempt_start) * 1000
            self._log_audit(
                AuditRecord(
                    ts=datetime.now(UTC),
                    model=queue_item.request.model,
                    worker=worker_name,
                    latency_ms=latency_ms,
                    prompt_chars=queue_item.prompt_chars,
                    token_usage=queue_item.token_estimate,
                    status="error",
                    error=str(last_error),
                )
            )
            if not should_retry:
                raise last_error  # type: ignore[misc]
            jitter = random.uniform(0.8, 1.2)
            backoff = self._backoff_base * (2 ** attempt) * jitter
            await asyncio.sleep(backoff)
        raise AssertionError("unreachable: all retry attempts exhausted")

    def _log_audit(self, record: AuditRecord) -> None:
        payload = mask_sensitive(record.model_dump())
        payload["ts"] = record.ts.isoformat().replace("+00:00", "Z")
        line = json.dumps(payload, ensure_ascii=False)
        self._audit_writer.write(line)


class _AsyncLineWriter:
    """Buffered JSONL writer running on a background thread."""

    def __init__(self, path: Path, *, flush_every: int = 1) -> None:
        self._path = path
        self._queue: SimpleQueue[Optional[str]] = SimpleQueue()
        self._thread: Optional[threading.Thread] = None
        self._flush_every = max(1, flush_every)
        self._write_count = 0

    def start(self) -> None:
        if self._thread is not None:
            return
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._thread = threading.Thread(target=self._run, name="mcp-log-writer", daemon=True)
        self._thread.start()

    def write(self, line: str) -> None:
        if self._thread is None:
            raise RuntimeError("writer not started")
        self._queue.put(line)

    def close(self) -> None:
        if self._thread is None:
            return
        self._queue.put(None)
        self._thread.join()
        self._thread = None

    def _run(self) -> None:
        with self._path.open("a", encoding="utf-8") as handle:
            while True:
                item = self._queue.get()
                if item is None:
                    handle.flush()
                    break
                handle.write(item)
                handle.write("\n")
                self._write_count += 1
                if self._write_count % self._flush_every == 0:
                    handle.flush()
