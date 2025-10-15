"""Core flow execution logic."""

from __future__ import annotations

import asyncio
import json
import os
import random
import threading
import time
import uuid
from collections import deque
from contextlib import ExitStack, contextmanager
from dataclasses import asdict, dataclass, is_dataclass
from datetime import UTC, datetime
from pathlib import Path
from queue import SimpleQueue
from typing import Callable, Dict, List, Optional, Set

import yaml
from jsonschema import Draft202012Validator
from mcp_router import MCPRouter
from mcp_router.redaction import mask_sensitive

from flow_runner.models import (
    AgentStepSpec,
    FlowDefinition,
    McpStepSpec,
    RunEvent,
    RunSummary,
    ShellStepSpec,
    StepFailure,
    StepSummary,
    compute_percentile,
)
from flow_runner.steps.agent import AgentStep
from flow_runner.steps.base import BaseStep, ExecutionContext, StepExecutionError
from flow_runner.steps.mcp import McpStep
from flow_runner.steps.shell import ShellStep

DEFAULT_BACKOFF_BASE = 0.5


class PerfTracer:
    """Collects coarse timing information for major runner stages."""

    def __init__(self, enabled: bool = False) -> None:
        self._enabled = enabled
        self._entries: List[Dict[str, float]] = []

    def enabled(self) -> bool:
        return self._enabled

    @contextmanager
    def span(self, name: str):
        if not self._enabled:
            yield
            return
        start = time.perf_counter()
        try:
            yield
        finally:
            duration = (time.perf_counter() - start) * 1000
            self._entries.append({"stage": name, "ms": round(duration, 2)})

    def export(self) -> List[Dict[str, float]]:
        return list(self._entries)


@dataclass
class StepOutcome:
    """Result of executing a single step."""

    step_id: str
    success: bool
    latency_ms: Optional[float]
    error: Optional[Exception]
    extra: Dict[str, object]
    fatal: bool


@dataclass
class ExecutionResult:
    """Aggregate information produced by running the flow."""

    failed: List[StepOutcome]
    completed_steps: Set[str]

    @property
    def fatal_failures(self) -> List[StepOutcome]:
        return [outcome for outcome in self.failed if outcome.fatal]

    @property
    def success(self) -> bool:
        return not self.fatal_failures


@dataclass
class StepAccumulator:
    """Mutable statistics tracked per step."""

    ok: int = 0
    fail: int = 0
    latencies: Optional[List[float]] = None

    def __post_init__(self) -> None:
        if self.latencies is None:
            self.latencies = []


def load_flow(path: Path, *, skip_schema_validation: bool = False) -> FlowDefinition:
    """Load and validate a flow definition from YAML or JSON."""

    with path.open("r", encoding="utf-8") as handle:
        if path.suffix.lower() in {".yaml", ".yml"}:
            data = yaml.safe_load(handle)
        else:
            data = json.load(handle)
    schema_ref = data.get("$schema")
    if schema_ref and not skip_schema_validation:
        schema_path = Path(schema_ref)
        if not schema_path.is_absolute():
            schema_path = (path.parent / schema_path).resolve()
        if not schema_path.exists():
            raise FileNotFoundError(f"flow schema not found: {schema_path}")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        Draft202012Validator(schema).validate(data)
    return FlowDefinition.model_validate(data)


class FlowRunner:
    """Executes a FlowDefinition and produces artifacts."""

    def __init__(
        self,
        flow: FlowDefinition,
        *,
        flow_path: Path,
        run_id: Optional[str] = None,
        output_dir: Optional[Path] = None,
        workspace_dir: Optional[Path] = None,
        only: Optional[Set[str]] = None,
        continue_from: Optional[str] = None,
        dev_fast: bool = False,
        perf_tracer: Optional[PerfTracer] = None,
        event_handler: Optional[Callable[[RunEvent], None]] = None,
    ) -> None:
        self.flow = flow
        self.flow_path = flow_path.resolve()
        self.flow_dir = self.flow_path.parent
        self.workspace_dir = (workspace_dir or Path.cwd()).resolve()
        self.run_id = run_id or uuid.uuid4().hex
        self._output_override = output_dir
        self.run_dir = self._resolve_run_dir()
        self.artifacts_dir = self.run_dir / "artifacts"
        self.mcp_log_dir = self.run_dir
        self.runs_log_path = self.run_dir / "runs.jsonl"
        self.summary_path = self.run_dir / "summary.json"
        self._dev_fast = dev_fast
        self._perf_tracer = perf_tracer or PerfTracer(enabled=False)
        self._log_flush_every = self._resolve_flush_frequency(self._dev_fast)
        self._event_handler = event_handler
        self.agent_paths = self._resolve_agent_paths(flow.agent_paths)
        raw_steps = [self._instantiate_step(spec) for spec in flow.steps.root]
        self._steps_by_id = {step.id: step for step in raw_steps}
        allowed_ids = self._resolve_allowed_ids(set(only) if only else None)
        self._precompleted = self._resolve_precompleted(raw_steps, allowed_ids, continue_from)
        self._steps: List[BaseStep] = [
            step
            for step in raw_steps
            if step.id in allowed_ids and step.id not in self._precompleted
        ]
        self._stats: Dict[str, StepAccumulator] = {
            step.id: StepAccumulator() for step in self._steps
        }
        self._events: List[RunEvent] = []
        self._agent_path_tokens: List[str] = []
        self._log_writer: Optional["_AsyncLineWriter"] = None

    # ------------------------------------------------------------------
    def run(self) -> str:
        """Execute the flow and return the run identifier."""

        execution_result: Optional[ExecutionResult] = None
        with self._perf_tracer.span("init.setup"):
            self.run_dir.mkdir(parents=True, exist_ok=True)
            self.artifacts_dir.mkdir(parents=True, exist_ok=True)
            started_at = datetime.now(UTC)
            self._push_agent_paths()
            self._log_writer = _AsyncLineWriter(
                self.runs_log_path, flush_every=self._log_flush_every
            )
            self._log_writer.start()
        try:
            with ExitStack() as exit_stack:
                with self._perf_tracer.span("init.router"):
                    router = exit_stack.enter_context(
                        MCPRouter.from_env(
                            log_dir=self.mcp_log_dir,
                            log_flush_every=self._log_flush_every,
                        )
                    )
                context = ExecutionContext(
                    run_id=self.run_id,
                    run_dir=self.run_dir,
                    artifacts_dir=self.artifacts_dir,
                    workspace_dir=self.workspace_dir,
                    flow_dir=self.flow_dir,
                    mcp_log_dir=self.mcp_log_dir,
                    mcp_router=router,
                )
                with self._perf_tracer.span("execute"):
                    execution_result = self._run_execution(context)
        finally:
            with self._perf_tracer.span("cleanup"):
                if self._log_writer is not None:
                    self._log_writer.close()
                    self._log_writer = None
                self._pop_agent_paths()
        finished_at = datetime.now(UTC)
        if execution_result is None:
            raise StepExecutionError("flow execution aborted before producing a result")
        with self._perf_tracer.span("summary.write"):
            self._write_summary(started_at, finished_at, execution_result)
        if not execution_result.success:
            raise StepExecutionError(self._format_failure_message(execution_result))
        return self.run_id

    # ------------------------------------------------------------------
    def plan(self) -> List[str]:
        """Return the step execution order without running anything."""

        pending: Dict[str, BaseStep] = {step.id: step for step in self._steps}
        completed: set[str] = set(self._precompleted)
        plan: List[str] = []
        while pending:
            ready = [
                step
                for step in pending.values()
                if set(step.dependencies).issubset(completed)
            ]
            if not ready:
                missing = ", ".join(sorted(pending.keys()))
                raise StepExecutionError(f"cyclic or missing dependencies detected: {missing}")
            for step in ready:
                plan.append(step.id)
                completed.add(step.id)
                pending.pop(step.id, None)
        return plan

    # ------------------------------------------------------------------
    async def _execute(self, context: ExecutionContext) -> ExecutionResult:
        pending_steps: Dict[str, BaseStep] = {step.id: step for step in self._steps}
        completed: Set[str] = set(self._precompleted)
        failed_fatal = False
        failed_outcomes: List[StepOutcome] = []

        dependents: Dict[str, List[str]] = {step_id: [] for step_id in self._steps_by_id}
        for step in self._steps_by_id.values():
            for dependency in step.dependencies:
                dependents.setdefault(dependency, []).append(step.id)

        remaining_deps: Dict[str, int] = {}
        for step in self._steps:
            remaining = sum(1 for dep in step.dependencies if dep not in completed)
            remaining_deps[step.id] = remaining

        ready: deque[BaseStep] = deque()

        for step_id, step in list(pending_steps.items()):
            if remaining_deps.get(step_id, 0) == 0:
                ready.append(step)
                pending_steps.pop(step_id, None)

        if not ready and pending_steps:
            missing = ", ".join(sorted(pending_steps.keys()))
            raise StepExecutionError(f"cyclic or missing dependencies detected: {missing}")

        running: Dict[asyncio.Task[StepOutcome], BaseStep] = {}

        def mark_completed(step_id: str) -> None:
            for dependent_id in dependents.get(step_id, []):
                if dependent_id not in remaining_deps:
                    continue
                remaining_deps[dependent_id] -= 1
                if remaining_deps[dependent_id] == 0:
                    dependent = pending_steps.pop(dependent_id, None)
                    if dependent is not None:
                        ready.append(dependent)

        while ready or running:
            while ready and not failed_fatal:
                step = ready.popleft()
                task = asyncio.create_task(self._run_step(step, context))
                running[task] = step

            if not running:
                missing = ", ".join(sorted(pending_steps.keys()))
                raise StepExecutionError(f"cyclic or missing dependencies detected: {missing}")

            done, _ = await asyncio.wait(
                running.keys(),
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in done:
                step = running.pop(task)
                try:
                    outcome = task.result()
                except Exception as exc:  # pragma: no cover - defensive
                    outcome = StepOutcome(
                        step_id=step.id,
                        success=False,
                        latency_ms=None,
                        error=exc,
                        extra={},
                        fatal=not step.continue_on_error,
                    )
                if outcome.success:
                    completed.add(step.id)
                    mark_completed(step.id)
                else:
                    failed_outcomes.append(outcome)
                    self._stats[step.id].fail += 1
                    if step.continue_on_error:
                        completed.add(step.id)
                        mark_completed(step.id)
                    else:
                        failed_fatal = True
                if failed_fatal:
                    break

            if failed_fatal:
                remaining_tasks = list(running.keys())
                for remaining_task in remaining_tasks:
                    remaining_task.cancel()
                await asyncio.gather(*remaining_tasks, return_exceptions=True)
                running.clear()
                break

        if pending_steps and not failed_fatal:
            missing = ", ".join(sorted(pending_steps.keys()))
            raise StepExecutionError(f"cyclic or missing dependencies detected: {missing}")

        return ExecutionResult(failed=failed_outcomes, completed_steps=completed)

    async def _run_step(self, step: BaseStep, context: ExecutionContext) -> StepOutcome:
        retries = step.retries
        attempt = 0
        last_error: Optional[Exception] = None
        while attempt <= retries:
            attempt += 1
            start = time.perf_counter()
            self._log_event(
                RunEvent(
                    ts=datetime.now(UTC),
                    run_id=context.run_id,
                    step=step.id,
                    event="start",
                    status="ok",
                    latency_ms=None,
                    retries=retries,
                    attempt=attempt,
                    extra={"type": step.spec.uses},
                )
            )
            try:
                result = await asyncio.wait_for(step.run(context), timeout=step.timeout)
            except asyncio.TimeoutError as exc:
                latency = (time.perf_counter() - start) * 1000
                last_error = exc
                self._log_event(
                    RunEvent(
                        ts=datetime.now(UTC),
                        run_id=context.run_id,
                        step=step.id,
                        event="error",
                        status="fail",
                        latency_ms=latency,
                        retries=retries,
                        attempt=attempt,
                        extra={"error": "timeout", "type": step.spec.uses},
                    )
                )
            except Exception as exc:  # pylint: disable=broad-except
                latency = (time.perf_counter() - start) * 1000
                last_error = exc
                self._log_event(
                    RunEvent(
                        ts=datetime.now(UTC),
                        run_id=context.run_id,
                        step=step.id,
                        event="error",
                        status="fail",
                        latency_ms=latency,
                        retries=retries,
                        attempt=attempt,
                        extra={"error": str(exc), "type": step.spec.uses},
                    )
                )
            else:
                latency = (time.perf_counter() - start) * 1000
                self._stats[step.id].ok += 1
                self._stats[step.id].latencies.append(latency)
                self._log_event(
                    RunEvent(
                        ts=datetime.now(UTC),
                        run_id=context.run_id,
                        step=step.id,
                        event="end",
                        status="ok",
                        latency_ms=latency,
                        retries=retries,
                        attempt=attempt,
                        extra={"result": result, "type": step.spec.uses},
                    )
                )
                return StepOutcome(
                    step_id=step.id,
                    success=True,
                    latency_ms=latency,
                    error=None,
                    extra=result,
                    fatal=False,
                )
            if attempt <= retries:
                jitter = random.uniform(0.8, 1.2)
                backoff = DEFAULT_BACKOFF_BASE * (2 ** (attempt - 1)) * jitter
                await asyncio.sleep(min(60.0, backoff))
        assert last_error is not None
        return StepOutcome(
            step_id=step.id,
            success=False,
            latency_ms=None,
            error=last_error,
            extra={},
            fatal=not step.continue_on_error,
        )

    def _log_event(self, event: RunEvent) -> None:
        payload = mask_sensitive(event.model_dump())
        payload["ts"] = event.ts.isoformat().replace("+00:00", "Z")
        serialized = json.dumps(payload, ensure_ascii=False, default=self._json_default)
        if self._log_writer is None:
            raise StepExecutionError("log writer is not initialized")
        self._log_writer.write(serialized)
        if self._event_handler is not None:
            try:
                self._event_handler(event)
            except Exception:  # pragma: no cover - defensive
                pass

    def _format_failure_message(self, result: ExecutionResult) -> str:
        lines = ["fatal step failure(s) detected:"]
        for outcome in result.fatal_failures:
            error_text = str(outcome.error) if outcome.error else "unknown error"
            flattened = " ".join(error_text.splitlines()).strip()
            lines.append(f"- {outcome.step_id}: {flattened or 'no error message provided'}")
        non_fatal = [outcome for outcome in result.failed if not outcome.fatal]
        if non_fatal:
            lines.append("non-fatal step failures:")
            for outcome in non_fatal:
                error_text = str(outcome.error) if outcome.error else "unknown error"
                flattened = " ".join(error_text.splitlines()).strip()
                lines.append(f"- {outcome.step_id}: {flattened or 'no error message provided'}")
        return "\n".join(lines)

    def _write_summary(
        self,
        started_at: datetime,
        finished_at: datetime,
        execution_result: ExecutionResult,
    ) -> None:
        step_summaries: Dict[str, StepSummary] = {}
        for step_id, data in self._stats.items():
            latencies = list(data.latencies)
            step_summaries[step_id] = StepSummary(
                ok=data.ok,
                fail=data.fail,
                p50_ms=compute_percentile(latencies, 50),
                p95_ms=compute_percentile(latencies, 95),
            )
        failures: Dict[str, StepFailure] = {}
        for outcome in execution_result.failed:
            error_text = str(outcome.error) if outcome.error else ""
            failures[outcome.step_id] = StepFailure(error=error_text, fatal=outcome.fatal)
        summary = RunSummary(
            run_id=self.run_id,
            steps=step_summaries,
            started_at=started_at,
            finished_at=finished_at,
            failures=failures,
        )
        with self.summary_path.open("w", encoding="utf-8") as handle:
            json.dump(summary.model_dump(mode="json"), handle, ensure_ascii=False, indent=2)

    def _instantiate_step(self, spec: ShellStepSpec | McpStepSpec | AgentStepSpec) -> BaseStep:
        if isinstance(spec, ShellStepSpec):
            return ShellStep(spec)
        if isinstance(spec, McpStepSpec):
            return McpStep(spec)
        if isinstance(spec, AgentStepSpec):
            return AgentStep(spec)
        raise ValueError(f"unsupported step type: {spec.uses}")

    def _resolve_run_dir(self) -> Path:
        if self._output_override is not None:
            base = self._output_override.expanduser()
        else:
            template = self.flow.run.output_dir
            base_dir_env = os.getenv("FLOWCTL_BASE_OUTPUT_DIR")
            if template.startswith("./") and base_dir_env:
                template = os.path.join(base_dir_env, template[2:])
            template = template.replace("${RUN_ID}", self.run_id)
            base = Path(template).expanduser()
        if not base.is_absolute():
            base = (self.workspace_dir / base).resolve()
        return base

    def _resolve_agent_paths(self, raw_paths: List[str]) -> List[str]:
        resolved: List[str] = []
        seen: set[str] = set()
        for raw in raw_paths:
            candidate = Path(raw).expanduser()
            if candidate.is_absolute():
                candidates = [candidate]
            else:
                candidates = [
                    (self.flow_dir / candidate).resolve(),
                    (self.workspace_dir / candidate).resolve(),
                ]
            for option in candidates:
                option_str = str(option)
                if option.exists() and option_str not in seen:
                    resolved.append(option_str)
                    seen.add(option_str)
        return resolved

    def _push_agent_paths(self) -> None:
        import sys

        for path in self.agent_paths:
            if path not in sys.path:
                sys.path.insert(0, path)
                self._agent_path_tokens.append(path)

    def _pop_agent_paths(self) -> None:
        import sys

        while self._agent_path_tokens:
            path = self._agent_path_tokens.pop()
            try:
                sys.path.remove(path)
            except ValueError:
                continue

    def _resolve_allowed_ids(self, only: Optional[Set[str]]) -> Set[str]:
        if not only:
            return set(self._steps_by_id)
        allowed: Set[str] = set()
        stack = list(only)
        while stack:
            step_id = stack.pop()
            if step_id not in self._steps_by_id:
                raise StepExecutionError(f"unknown step id referenced in --only: {step_id}")
            if step_id in allowed:
                continue
            allowed.add(step_id)
            stack.extend(self._steps_by_id[step_id].dependencies)
        return allowed

    def _resolve_precompleted(
        self,
        raw_steps: List[BaseStep],
        allowed_ids: Set[str],
        continue_from: Optional[str],
    ) -> Set[str]:
        precompleted: Set[str] = set()
        if continue_from is None:
            return precompleted
        if continue_from not in self._steps_by_id:
            raise StepExecutionError(f"--continue-from references unknown step: {continue_from}")
        seen = False
        for step in raw_steps:
            if step.id == continue_from:
                seen = True
                break
            if step.id in allowed_ids:
                precompleted.add(step.id)
        if not seen:
            raise StepExecutionError(f"--continue-from step not found: {continue_from}")
        # Ensure the continued step itself is part of the allowed set
        allowed_ids.add(continue_from)
        return precompleted

    def _run_execution(self, context: ExecutionContext) -> ExecutionResult:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self._execute(context))
        return self._run_execution_in_thread(context)

    def _run_execution_in_thread(self, context: ExecutionContext) -> ExecutionResult:
        result: Dict[str, ExecutionResult] = {}
        error: List[BaseException] = []

        def runner() -> None:
            try:
                result["value"] = asyncio.run(self._execute(context))
            except BaseException as exc:  # pragma: no cover - defensive
                error.append(exc)

        thread = threading.Thread(target=runner, name=f"flow-runner-{self.run_id}", daemon=True)
        thread.start()
        thread.join()
        if error:
            raise error[0]
        if "value" not in result:
            raise StepExecutionError("flow execution thread terminated without result")
        return result["value"]

    @property
    def perf_metrics(self) -> List[Dict[str, float]]:
        return self._perf_tracer.export()

    @staticmethod
    def _resolve_flush_frequency(dev_fast: bool) -> int:
        if dev_fast:
            return 1
        env_value = os.getenv("FLOWCTL_LOG_FLUSH_EVERY")
        if env_value:
            try:
                parsed = int(env_value)
                if parsed >= 1:
                    return parsed
            except ValueError:
                pass
        return 1 if dev_fast else 50

    @staticmethod
    def _json_default(value: object) -> object:
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, set):
            return list(value)
        if isinstance(value, bytes):
            return value.decode(errors="replace")
        if is_dataclass(value):
            return asdict(value)
        model_dump = getattr(value, "model_dump", None)
        if callable(model_dump):
            try:
                return model_dump()
            except Exception:  # pragma: no cover - fallback
                return str(value)
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return str(value)


class _AsyncLineWriter:
    """Threaded line writer to keep logging off the event loop."""

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
        self._thread = threading.Thread(target=self._run, name="flowrunner-log-writer", daemon=True)
        self._thread.start()

    def write(self, line: str) -> None:
        if self._thread is None:
            raise StepExecutionError("log writer not started")
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


def load_flow_from_path(path: Path, *, skip_schema_validation: bool = False) -> FlowDefinition:
    """Public helper used by the CLI."""

    return load_flow(path, skip_schema_validation=skip_schema_validation)
