"""Typer CLI for flowrunner."""

from __future__ import annotations

import json
import math
import os
import shutil
import statistics
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

import typer
import yaml
from dotenv import load_dotenv
from jsonschema import ValidationError as JsonSchemaValidationError
from jsonschema import validate as jsonschema_validate
from rich.console import Console
from rich.live import Live
from rich.table import Table

from flow_runner.models import RunEvent
from flow_runner.runner import FlowRunner, PerfTracer, load_flow_from_path
from flow_runner.steps.base import StepExecutionError

PROJECT_ROOT = Path(__file__).resolve().parents[4]


@dataclass
class MetricAggregate:
    ok: int = 0
    fail: int = 0
    latencies: List[float] = field(default_factory=list)
    retries: int = 0
    token_in: int = 0
    token_out: int = 0


@dataclass
class DiffEntry:
    severity: str
    step: str
    field: str
    message: str
    base: Any = None
    target: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "step": self.step,
            "field": self.field,
            "message": self.message,
            "base": self.base,
            "target": self.target,
        }


SEVERITY_ORDER = {"BREAKING": 0, "WARNING": 1, "INFO": 2}
TOKEN_FIELD_ALIASES = {
    "input": ["input_tokens", "prompt", "prompt_tokens", "tokens_in", "in"],
    "output": ["output_tokens", "completion", "completion_tokens", "tokens_out", "out"],
}


app = typer.Typer(help="Flow Runner orchestrator CLI")
console = Console()

FLOW_FILE_ARGUMENT = typer.Argument(
    ...,
    exists=True,
    readable=True,
    help="Path to a flow YAML/JSON file",
)
RUN_ID_OPTION = typer.Option(None, help="Optional run identifier")
OUTPUT_DIR_OPTION = typer.Option(
    None,
    help="Override output directory for this run",
)
ONLY_OPTION = typer.Option(
    None,
    "--only",
    "-o",
    help="Run only the selected step IDs; dependencies are included automatically.",
)
CONTINUE_FROM_OPTION = typer.Option(
    None,
    help="Treat all steps before the specified step as already completed.",
)
RUN_DRY_RUN_OPTION = typer.Option(
    False,
    help="Preview the execution plan without running.",
)
DEV_FAST_OPTION = typer.Option(
    False,
    "--dev-fast",
    help="Development mode: skip schema validation and flush logs immediately for debugging.",
)
TRACE_PERF_OPTION = typer.Option(
    False,
    "--trace-perf",
    help="Emit coarse timing metrics for major execution stages (JSON to stderr).",
)
PROGRESS_OPTION = typer.Option(
    False,
    "--progress",
    help="Show live step status updates during execution.",
)
GC_BASE_DIR_OPTION = typer.Option(
    None,
    help="Directory containing run outputs; defaults to FLOWCTL_BASE_OUTPUT_DIR or .runs.",
)
GC_KEEP_OPTION = typer.Option(
    100,
    min=0,
    help="Number of most recent runs to retain.",
)
GC_DRY_RUN_OPTION = typer.Option(
    False,
    help="Show which runs would be removed without deleting.",
)
LOGS_RUN_ID_ARGUMENT = typer.Argument(..., help="Existing run identifier")
LOGS_OUTPUT_DIR_OPTION = typer.Option(
    None,
    help="Override the base output directory",
)
LOGS_JSON_OPTION = typer.Option(
    False,
    "--json",
    help="Emit machine-readable summary output.",
)
STATS_RUNS_DIR_OPTION = typer.Option(
    Path(".runs"),
    "--runs-dir",
    help="Directory containing run outputs.",
)
STATS_LAST_OPTION = typer.Option(
    None,
    "--last",
    help="Only include the most recent N runs.",
)
STATS_GROUP_OPTION = typer.Option(
    "step",
    "--group-by",
    "-g",
    help="Group metrics by 'step' or 'model'.",
)
STATS_JSON_OPTION = typer.Option(
    False,
    "--json",
    help="Emit JSON instead of a table.",
)
VALIDATE_FLOW_PATH_ARGUMENT = typer.Argument(..., help="Flow definition to validate.")
DIFF_BASE_FLOW_ARGUMENT = typer.Argument(..., help="Reference flow definition.")
DIFF_TARGET_FLOW_ARGUMENT = typer.Argument(..., help="Flow definition to compare.")
DIFF_JSON_OPTION = typer.Option(
    False,
    "--json",
    help="Emit machine-readable diff.",
)

def _resolve_workspace_path(path: Path) -> Path:
    expanded = path.expanduser()
    if expanded.is_absolute():
        return expanded
    cwd_candidate = (Path.cwd() / expanded).resolve()
    project_candidate = (PROJECT_ROOT / expanded).resolve()
    if cwd_candidate.exists() or not project_candidate.exists():
        return cwd_candidate
    return project_candidate


def _read_json_lines(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            try:
                parsed = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                yield parsed


def _extract_tokens(token_usage: Any, field: str) -> int:
    value = _find_token_value(token_usage, field)
    return int(value) if value is not None else 0


def _find_token_value(token_usage: Any, field: str) -> Optional[int]:
    if isinstance(token_usage, (int, float)):
        return int(token_usage)
    if isinstance(token_usage, str):
        if token_usage.isdigit():
            return int(token_usage)
        try:
            numeric = float(token_usage)
        except ValueError:
            return None
        return int(numeric)
    if isinstance(token_usage, dict):
        candidates = [field, *TOKEN_FIELD_ALIASES.get(field, [])]
        for candidate in candidates:
            if candidate in token_usage:
                raw_value = token_usage[candidate]
                result = _find_token_value(raw_value, field)
                if result is not None:
                    return result
        for value in token_usage.values():
            if isinstance(value, (dict, list)):
                result = _find_token_value(value, field)
                if result is not None:
                    return result
    if isinstance(token_usage, list):
        for item in token_usage:
            result = _find_token_value(item, field)
            if result is not None:
                return result
    return None


def _compute_percentile(values: Sequence[float], percentile: float) -> Optional[float]:
    if not values:
        return None
    ordered = sorted(values)
    if percentile == 50:
        return float(statistics.median(ordered))
    if len(ordered) == 1:
        return float(ordered[0])
    rank = (len(ordered) - 1) * (percentile / 100)
    lower_index = math.floor(rank)
    upper_index = math.ceil(rank)
    if lower_index == upper_index:
        return float(ordered[lower_index])
    lower_value = ordered[lower_index]
    upper_value = ordered[upper_index]
    return float(lower_value + (upper_value - lower_value) * (rank - lower_index))


def _aggregate_step_metrics(path: Path, aggregates: Dict[str, MetricAggregate]) -> bool:
    seen = False
    max_attempt_per_step: Dict[str, int] = {}
    for record in _read_json_lines(path) or []:
        seen = True
        step_id = str(record.get("step") or "unknown")
        group = aggregates.setdefault(step_id, MetricAggregate())
        status = str(record.get("status", "")).lower()
        event = str(record.get("event", "")).lower()
        if status == "ok" and event == "end":
            group.ok += 1
        elif status == "fail" and event == "error":
            group.fail += 1
        latency = record.get("latency_ms")
        if isinstance(latency, (int, float)):
            group.latencies.append(float(latency))
        attempt = record.get("attempt")
        if isinstance(attempt, int):
            previous = max_attempt_per_step.get(step_id, 0)
            if attempt > previous:
                max_attempt_per_step[step_id] = attempt
        if event == "end":
            extra = record.get("extra")
            if isinstance(extra, dict):
                result = extra.get("result")
                if isinstance(result, dict):
                    token_usage = result.get("token_usage")
                    group.token_in += _extract_tokens(token_usage, "input")
                    group.token_out += _extract_tokens(token_usage, "output")
    for step_id, max_attempt in max_attempt_per_step.items():
        group = aggregates.setdefault(step_id, MetricAggregate())
        group.retries += max(0, max_attempt - 1)
    return seen


def _aggregate_model_metrics(path: Path, aggregates: Dict[str, MetricAggregate]) -> bool:
    seen = False
    for record in _read_json_lines(path) or []:
        seen = True
        model_name = str(record.get("model") or "unknown")
        group = aggregates.setdefault(model_name, MetricAggregate())
        status = str(record.get("status", "")).lower()
        if status == "ok":
            group.ok += 1
        elif status:
            group.fail += 1
        latency = record.get("latency_ms")
        if isinstance(latency, (int, float)):
            group.latencies.append(float(latency))
        group.token_in += _extract_tokens(record.get("token_usage"), "input")
        group.token_out += _extract_tokens(record.get("token_usage"), "output")
    return seen


def _format_latency(value: Optional[float]) -> str:
    if value is None:
        return "-"
    return f"{value:.1f}"


def _build_metrics_rows(aggregates: Dict[str, MetricAggregate]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for key, value in sorted(aggregates.items(), key=lambda item: item[0]):
        rows.append(
            {
                "group": key,
                "ok": value.ok,
                "fail": value.fail,
                "p50_latency_ms": _compute_percentile(value.latencies, 50),
                "p95_latency_ms": _compute_percentile(value.latencies, 95),
                "retries": value.retries,
                "token_in": value.token_in,
                "token_out": value.token_out,
            }
        )
    return rows


def _render_metrics_table(
    rows: Sequence[Dict[str, Any]],
    group_label: str,
    processed_runs: int,
) -> None:
    title = f"Stats by {group_label.capitalize()}"
    table = Table(title=title)
    table.add_column(group_label.capitalize(), justify="left")
    table.add_column("OK", justify="right")
    table.add_column("Fail", justify="right")
    table.add_column("p50 (ms)", justify="right")
    table.add_column("p95 (ms)", justify="right")
    table.add_column("Retries", justify="right")
    table.add_column("Token In", justify="right")
    table.add_column("Token Out", justify="right")
    for row in rows:
        table.add_row(
            row["group"],
            str(row["ok"]),
            str(row["fail"]),
            _format_latency(row["p50_latency_ms"]),
            _format_latency(row["p95_latency_ms"]),
            str(row["retries"]),
            str(row["token_in"]),
            str(row["token_out"]),
        )
    console.print(table)
    console.print(f"Processed runs: {processed_runs}")


def _load_flow_document(flow_path: Path) -> Dict[str, Any]:
    raw = flow_path.read_text(encoding="utf-8")
    document = yaml.safe_load(raw)
    if document is None:
        return {}
    if not isinstance(document, dict):
        raise ValueError("Flow definition must be a mapping.")
    return document


def _extract_required_fields(step: Dict[str, Any]) -> set[str]:
    input_block = step.get("input")
    if not isinstance(input_block, dict):
        return set()
    required = input_block.get("required")
    if isinstance(required, list):
        return {str(item) for item in required}
    return set()


def _compute_flow_diff(
    base_flow: Dict[str, Any],
    target_flow: Dict[str, Any],
) -> List[DiffEntry]:
    entries: List[DiffEntry] = []
    base_steps = {
        step.get("id"): step
        for step in base_flow.get("steps", [])
        if isinstance(step, dict) and step.get("id")
    }
    target_steps = {
        step.get("id"): step
        for step in target_flow.get("steps", [])
        if isinstance(step, dict) and step.get("id")
    }

    base_ids = set(base_steps)
    target_ids = set(target_steps)

    for removed_id in sorted(base_ids - target_ids):
        entries.append(
            DiffEntry(
                severity="BREAKING",
                step=str(removed_id),
                field="step",
                message="Step removed",
                base=base_steps[removed_id],
                target=None,
            )
        )

    for added_id in sorted(target_ids - base_ids):
        entries.append(
            DiffEntry(
                severity="INFO",
                step=str(added_id),
                field="step",
                message="Step added",
                base=None,
                target=target_steps[added_id],
            )
        )

    tracked_fields = {
        "id",
        "uses",
        "timeout_sec",
        "retries",
        "continue_on_error",
        "policy",
        "config",
        "input",
    }

    for step_id in sorted(base_ids & target_ids):
        base_step = base_steps[step_id]
        target_step = target_steps[step_id]

        if base_step.get("uses") != target_step.get("uses"):
            entries.append(
                DiffEntry(
                    severity="BREAKING",
                    step=str(step_id),
                    field="uses",
                    message="Uses changed",
                    base=base_step.get("uses"),
                    target=target_step.get("uses"),
                )
            )

        base_timeout = base_step.get("timeout_sec")
        target_timeout = target_step.get("timeout_sec")
        if isinstance(base_timeout, (int, float)):
            if target_timeout is None:
                entries.append(
                    DiffEntry(
                        severity="BREAKING",
                        step=str(step_id),
                        field="timeout_sec",
                        message="timeout_sec removed",
                        base=base_timeout,
                        target=target_timeout,
                    )
                )
            elif (
                isinstance(target_timeout, (int, float))
                and float(target_timeout) < float(base_timeout)
            ):
                entries.append(
                    DiffEntry(
                        severity="BREAKING",
                        step=str(step_id),
                        field="timeout_sec",
                        message="timeout_sec decreased",
                        base=base_timeout,
                        target=target_timeout,
                    )
                )

        base_retries = base_step.get("retries")
        target_retries = target_step.get("retries")
        if isinstance(base_retries, int):
            if target_retries is None:
                entries.append(
                    DiffEntry(
                        severity="BREAKING",
                        step=str(step_id),
                        field="retries",
                        message="retries removed",
                        base=base_retries,
                        target=target_retries,
                    )
                )
            elif isinstance(target_retries, int) and target_retries < base_retries:
                entries.append(
                    DiffEntry(
                        severity="BREAKING",
                        step=str(step_id),
                        field="retries",
                        message="retries decreased",
                        base=base_retries,
                        target=target_retries,
                    )
                )

        base_continue = bool(base_step.get("continue_on_error", False))
        target_continue = bool(target_step.get("continue_on_error", False))
        if base_continue != target_continue:
            entries.append(
                DiffEntry(
                    severity="WARNING",
                    step=str(step_id),
                    field="continue_on_error",
                    message="continue_on_error changed",
                    base=base_continue,
                    target=target_continue,
                )
            )

        if base_step.get("policy") != target_step.get("policy"):
            entries.append(
                DiffEntry(
                    severity="WARNING",
                    step=str(step_id),
                    field="policy",
                    message="policy changed",
                    base=base_step.get("policy"),
                    target=target_step.get("policy"),
                )
            )

        if base_step.get("config") != target_step.get("config"):
            entries.append(
                DiffEntry(
                    severity="WARNING",
                    step=str(step_id),
                    field="config",
                    message="config changed",
                    base=base_step.get("config"),
                    target=target_step.get("config"),
                )
            )

        base_required = _extract_required_fields(base_step)
        target_required = _extract_required_fields(target_step)
        removed_required = sorted(base_required - target_required)
        if removed_required:
            entries.append(
                DiffEntry(
                    severity="BREAKING",
                    step=str(step_id),
                    field="input.required",
                    message="Required inputs removed",
                    base=removed_required,
                    target=sorted(target_required),
                )
            )

        base_remaining = {k: v for k, v in base_step.items() if k not in tracked_fields}
        target_remaining = {k: v for k, v in target_step.items() if k not in tracked_fields}
        if base_remaining != target_remaining:
            entries.append(
                DiffEntry(
                    severity="INFO",
                    step=str(step_id),
                    field="metadata",
                    message="Non-execution metadata changed",
                    base=base_remaining,
                    target=target_remaining,
                )
            )

    return entries


def _determine_exit_code(entries: Sequence[DiffEntry]) -> int:
    exit_code = 0
    for entry in entries:
        if entry.severity == "BREAKING":
            return 2
        if entry.severity == "WARNING":
            exit_code = max(exit_code, 1)
    return exit_code


def _render_diff(entries: Sequence[DiffEntry], base_path: Path, target_path: Path) -> None:
    if not entries:
        console.print("[green]No differences detected.[/green]")
        return
    table = Table(title=f"Diff: {base_path.name} -> {target_path.name}", show_lines=False)
    table.add_column("Severity", justify="left")
    table.add_column("Step", justify="left")
    table.add_column("Field", justify="left")
    table.add_column("Message", justify="left")
    table.add_column("Base", justify="left", overflow="fold")
    table.add_column("Target", justify="left", overflow="fold")
    sorted_entries = sorted(
        entries,
        key=lambda item: (SEVERITY_ORDER.get(item.severity, 3), item.step, item.field),
    )
    for entry in sorted_entries:
        base_repr = "-"
        if entry.base is not None:
            base_repr = json.dumps(entry.base, ensure_ascii=False, default=str)
        target_repr = "-"
        if entry.target is not None:
            target_repr = json.dumps(entry.target, ensure_ascii=False, default=str)
        table.add_row(
            entry.severity,
            entry.step or "-",
            entry.field,
            entry.message,
            base_repr,
            target_repr,
        )
    console.print(table)


def _summarize_diff(entries: Sequence[DiffEntry], exit_code: int) -> Dict[str, int]:
    summary = {
        "breaking": 0,
        "warning": 0,
        "info": 0,
        "total": len(entries),
        "exit_code": exit_code,
    }
    for entry in entries:
        key = entry.severity.lower()
        if key in summary:
            summary[key] += 1
    return summary


@app.callback()
def init() -> None:
    """Load environment variables before executing any command."""

    load_dotenv(override=False)


@app.command()
def run(
    flow_file: Path = FLOW_FILE_ARGUMENT,
    run_id: Optional[str] = RUN_ID_OPTION,
    output_dir: Optional[Path] = OUTPUT_DIR_OPTION,
    only: Optional[List[str]] = ONLY_OPTION,
    continue_from: Optional[str] = CONTINUE_FROM_OPTION,
    dry_run: bool = RUN_DRY_RUN_OPTION,
    dev_fast: bool = DEV_FAST_OPTION,
    trace_perf: bool = TRACE_PERF_OPTION,
    progress: bool = PROGRESS_OPTION,
) -> None:
    """Execute a flow definition."""

    try:
        flow = load_flow_from_path(flow_file, skip_schema_validation=dev_fast)
    except Exception as exc:  # pylint: disable=broad-except
        typer.echo(f"Failed to load flow: {exc}", err=True)
        raise typer.Exit(code=1) from exc
    perf_tracer = PerfTracer(enabled=trace_perf)

    step_order: List[str] = []
    step_status: Dict[str, str] = {}
    step_detail: Dict[str, str] = {}
    live: Optional[Live] = None
    progress_requested = progress and not dry_run
    if progress and dry_run:
        console.print("[yellow]Ignoring --progress because --dry-run was specified.[/yellow]")
        progress_requested = False
    progress_active = progress_requested

    def _render_progress_table() -> Table:
        table = Table(title="Flow Progress")
        table.add_column("Step", justify="left")
        table.add_column("Status", justify="left")
        table.add_column("Detail", justify="left", overflow="fold")
        status_styles = {
            "pending": "dim",
            "running": "yellow",
            "ok": "green",
            "fail": "red",
        }
        status_labels = {
            "pending": "Pending",
            "running": "Running",
            "ok": "Completed",
            "fail": "Failed",
        }
        for step_id in step_order:
            status = step_status.get(step_id, "pending")
            label = status_labels.get(status, status.title())
            style = status_styles.get(status)
            status_text = f"[{style}]{label}[/{style}]" if style else label
            detail = step_detail.get(step_id, "")
            table.add_row(step_id, status_text, detail)
        return table

    def _handle_event(event: RunEvent) -> None:
        if not progress_active or event.step not in step_status:
            return
        if event.event == "start":
            step_status[event.step] = "running"
            step_type = event.extra.get("type")
            if isinstance(step_type, str) and step_type:
                step_detail[event.step] = step_type
        elif event.event == "end" and event.status == "ok":
            step_status[event.step] = "ok"
            detail = ""
            result = event.extra.get("result")
            if isinstance(result, dict):
                stdout = result.get("stdout")
                text = result.get("text")
                if isinstance(stdout, str) and stdout.strip():
                    detail = stdout.strip()
                elif isinstance(text, str) and text.strip():
                    detail = text.strip()
            step_detail[event.step] = detail[:80]
        elif event.event == "error":
            step_status[event.step] = "fail"
            error_text = event.extra.get("error")
            if isinstance(error_text, str) and error_text.strip():
                step_detail[event.step] = error_text.strip()[:80]
            else:
                step_detail[event.step] = "Step reported an error."
        if live is not None:
            live.update(_render_progress_table())

    try:
        runner = FlowRunner(
            flow,
            flow_path=flow_file,
            run_id=run_id,
            output_dir=output_dir,
            workspace_dir=Path.cwd(),
            only=set(only) if only else None,
            continue_from=continue_from,
            dev_fast=dev_fast,
            perf_tracer=perf_tracer,
            event_handler=_handle_event if progress_requested else None,
        )
    except StepExecutionError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc

    if progress_requested:
        try:
            step_order = runner.plan()
        except StepExecutionError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
        if step_order:
            step_status = {step_id: "pending" for step_id in step_order}
            step_detail = {step_id: "" for step_id in step_order}
            progress_active = True
        else:
            progress_active = False
    if dry_run:
        try:
            start = time.perf_counter()
            plan = runner.plan()
            elapsed = (time.perf_counter() - start) * 1000
            if trace_perf:
                _emit_perf_metrics([{"stage": "plan", "ms": round(elapsed, 2)}])
        except StepExecutionError as exc:
            typer.echo(str(exc), err=True)
            raise typer.Exit(code=1) from exc
        if not plan:
            console.print("[yellow]No steps selected; nothing to execute.")
        else:
            table = Table(title="Execution Plan")
            table.add_column("Order", justify="right")
            table.add_column("Step ID", justify="left")
            for index, step_id in enumerate(plan, start=1):
                table.add_row(str(index), step_id)
            console.print(table)
        return
    try:
        if progress_active and step_order:
            with Live(_render_progress_table(), console=console, refresh_per_second=8) as live_ctx:
                live = live_ctx
                result_run_id = runner.run()
                live = None
        else:
            result_run_id = runner.run()
    except StepExecutionError as exc:
        if trace_perf:
            _emit_perf_metrics(runner.perf_metrics)
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=1) from exc
    if trace_perf:
        _emit_perf_metrics(runner.perf_metrics)
    console.print(f"[green]Run completed[/green]: {result_run_id}")
    console.print(f"[cyan]Output directory[/cyan]: {runner.run_dir}")

@app.command()
def gc(
    base_dir: Optional[Path] = GC_BASE_DIR_OPTION,
    keep: int = GC_KEEP_OPTION,
    dry_run: bool = GC_DRY_RUN_OPTION,
) -> None:
    """Garbage-collect run directories to control disk usage."""

    resolved_base = base_dir or Path(os.getenv("FLOWCTL_BASE_OUTPUT_DIR", ".runs"))
    resolved_base = resolved_base.expanduser().resolve()
    if not resolved_base.exists():
        console.print(f"[yellow]Base directory not found: {resolved_base}")
        return
    runs = [path for path in resolved_base.iterdir() if path.is_dir()]
    runs.sort(key=lambda candidate: candidate.stat().st_mtime, reverse=True)
    to_prune = runs[keep:]
    if not to_prune:
        console.print("[green]Nothing to prune.")
        return
    for target in to_prune:
        if dry_run:
            console.print(f"[yellow]Would remove {target}")
        else:
            shutil.rmtree(target, ignore_errors=True)
            console.print(f"[red]Removed[/red] {target}")

@app.command()
def logs(
    run_id: str = LOGS_RUN_ID_ARGUMENT,
    output_dir: Optional[Path] = LOGS_OUTPUT_DIR_OPTION,
    json_output: bool = LOGS_JSON_OPTION,
) -> None:
    """Render summary statistics for a past run."""

    summary_path = _resolve_summary_path(run_id, output_dir)
    if not summary_path.exists():
        typer.echo(f"Summary not found at {summary_path}", err=True)
        raise typer.Exit(code=1)
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    started = datetime.fromisoformat(summary["started_at"].replace("Z", "+00:00"))
    finished = datetime.fromisoformat(summary["finished_at"].replace("Z", "+00:00"))
    step_rows = [
        {
            "id": step_id,
            "ok": metrics["ok"],
            "fail": metrics["fail"],
            "p50_ms": float(metrics["p50_ms"]),
            "p95_ms": float(metrics["p95_ms"]),
        }
        for step_id, metrics in summary["steps"].items()
    ]
    total_ok = sum(row["ok"] for row in step_rows)
    total_fail = sum(row["fail"] for row in step_rows)
    total = max(1, total_ok + total_fail)
    success_rate = (total_ok / total) * 100

    if json_output:
        payload = {
            "run_id": run_id,
            "summary_path": str(summary_path),
            "started_at": started.isoformat(),
            "finished_at": finished.isoformat(),
            "steps": step_rows,
            "metrics": {
                "ok": total_ok,
                "fail": total_fail,
                "success_rate": success_rate,
            },
        }
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    table = Table(title=f"Run {run_id}")
    table.add_column("Step", justify="left")
    table.add_column("OK", justify="right")
    table.add_column("Fail", justify="right")
    table.add_column("p50 (ms)", justify="right")
    table.add_column("p95 (ms)", justify="right")
    for row in step_rows:
        table.add_row(
            row["id"],
            str(row["ok"]),
            str(row["fail"]),
            f"{row['p50_ms']:.1f}",
            f"{row['p95_ms']:.1f}",
        )
    console.print(table)
    console.print(
        f"Succeeded: {total_ok}, Failed: {total_fail}, Success rate: {success_rate:.1f}%",
        style="green" if total_fail == 0 else "yellow",
    )
    console.print(f"Started at: {started.isoformat()} | Finished at: {finished.isoformat()}")


def _resolve_summary_path(run_id: str, output_dir: Optional[Path]) -> Path:
    if output_dir is not None:
        candidate = Path(output_dir).expanduser()
        if candidate.exists():
            candidate_resolved = candidate.resolve()
            if candidate_resolved.is_file():
                return candidate_resolved
        else:
            if candidate.suffix:
                return candidate.resolve()
            candidate_resolved = candidate.resolve()
        if candidate_resolved.is_file():
            return candidate_resolved
        summary_candidate = candidate_resolved / "summary.json"
        if summary_candidate.exists():
            return summary_candidate
        if candidate_resolved.name == run_id:
            return summary_candidate
        return (candidate_resolved / run_id / "summary.json").resolve()
    base_dir = os.getenv("FLOWCTL_BASE_OUTPUT_DIR", ".runs")
    base = Path(base_dir).expanduser().resolve() / run_id
    return (base / "summary.json").resolve()


def _emit_perf_metrics(metrics: Sequence[Dict[str, Any]]) -> None:
    if not metrics:
        return
    for entry in metrics:
        typer.echo(json.dumps(entry, ensure_ascii=False), err=True)


@app.command("stats")
def stats_cmd(
    runs_dir: Path = STATS_RUNS_DIR_OPTION,
    last: Optional[int] = STATS_LAST_OPTION,
    group_by: str = STATS_GROUP_OPTION,
    json_output: bool = STATS_JSON_OPTION,
) -> None:
    normalized_group = group_by.lower()
    if normalized_group not in {"step", "model"}:
        typer.echo(f"Unsupported group-by value: {group_by}", err=True)
        raise typer.Exit(code=1)

    if last is not None and last <= 0:
        typer.echo("Option --last must be greater than zero.", err=True)
        raise typer.Exit(code=1)

    resolved_runs_dir = _resolve_workspace_path(runs_dir)
    if not resolved_runs_dir.exists():
        typer.echo(f"Runs directory not found: {resolved_runs_dir}", err=True)
        raise typer.Exit(code=1)

    run_dirs = [path for path in resolved_runs_dir.iterdir() if path.is_dir()]
    if not run_dirs:
        console.print(f"[yellow]No runs found in {resolved_runs_dir}.[/yellow]")
        raise typer.Exit(code=0)

    run_dirs.sort(key=lambda candidate: candidate.stat().st_mtime, reverse=True)
    if last is not None:
        run_dirs = run_dirs[:last]

    aggregates: Dict[str, MetricAggregate] = {}
    missing_logs: List[str] = []
    processed_runs = 0

    for run_dir in run_dirs:
        if normalized_group == "step":
            log_path = run_dir / "runs.jsonl"
            seen = _aggregate_step_metrics(log_path, aggregates)
        else:
            log_path = run_dir / "mcp_calls.jsonl"
            seen = _aggregate_model_metrics(log_path, aggregates)
        if seen:
            processed_runs += 1
        else:
            missing_logs.append(str(log_path))

    if not aggregates:
        console.print("[yellow]No metrics found in the selected runs.[/yellow]")
        raise typer.Exit(code=0)

    rows = _build_metrics_rows(aggregates)
    if json_output:
        payload = {
            "group_by": normalized_group,
            "runs_dir": str(resolved_runs_dir),
            "runs_considered": len(run_dirs),
            "runs_processed": processed_runs,
            "groups": rows,
        }
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        _render_metrics_table(rows, normalized_group, processed_runs)
        if missing_logs:
            warning_message = (
                "[yellow]Skipped "
                f"{len(missing_logs)}"
                " log files due to missing or invalid data.[/yellow]"
            )
            console.print(warning_message)


@app.command("validate")
def validate_cmd(
    flow_path: Path = VALIDATE_FLOW_PATH_ARGUMENT,
) -> None:
    resolved_flow = _resolve_workspace_path(flow_path)
    if not resolved_flow.exists():
        typer.echo(f"Flow file not found: {resolved_flow}", err=True)
        raise typer.Exit(code=1)

    schema_path = _resolve_workspace_path(Path("docs/flow.schema.json"))
    if not schema_path.exists():
        typer.echo(f"Warning: schema not found at {schema_path}", err=True)
        raise typer.Exit(code=1)

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        typer.echo(f"Invalid schema JSON: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    try:
        document = _load_flow_document(resolved_flow)
    except (yaml.YAMLError, ValueError, OSError) as exc:
        typer.echo(f"Failed to load flow: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    try:
        jsonschema_validate(document, schema)
    except JsonSchemaValidationError as exc:
        location = ".".join(str(part) for part in exc.path) or "<root>"
        message = exc.message.replace("\n", " ")
        typer.echo(f"ValidationError at {location}: {message}", err=True)
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Valid:[/green] {resolved_flow}")


@app.command("diff")
def diff_cmd(
    base_flow: Path = DIFF_BASE_FLOW_ARGUMENT,
    target_flow: Path = DIFF_TARGET_FLOW_ARGUMENT,
    json_output: bool = DIFF_JSON_OPTION,
) -> None:
    resolved_base = _resolve_workspace_path(base_flow)
    resolved_target = _resolve_workspace_path(target_flow)

    if not resolved_base.exists():
        typer.echo(f"Base flow not found: {resolved_base}", err=True)
        raise typer.Exit(code=1)
    if not resolved_target.exists():
        typer.echo(f"Target flow not found: {resolved_target}", err=True)
        raise typer.Exit(code=1)

    try:
        base_document = _load_flow_document(resolved_base)
        target_document = _load_flow_document(resolved_target)
    except (yaml.YAMLError, ValueError, OSError) as exc:
        typer.echo(f"Failed to load flows: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    entries = _compute_flow_diff(base_document, target_document)
    exit_code = _determine_exit_code(entries)

    if json_output:
        payload = {
            "base": str(resolved_base),
            "target": str(resolved_target),
            "summary": _summarize_diff(entries, exit_code),
            "differences": [entry.to_dict() for entry in entries],
        }
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        _render_diff(entries, resolved_base, resolved_target)

    raise typer.Exit(code=exit_code)
