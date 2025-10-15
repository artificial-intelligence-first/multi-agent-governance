from __future__ import annotations

from pathlib import Path

from flow_runner.steps.base import ExecutionContext
from flow_runner.steps.mcp import McpStep


def _make_context(tmp_path: Path) -> ExecutionContext:
    run_dir = tmp_path / "run"
    artifacts_dir = run_dir / "artifacts"
    run_dir.mkdir(parents=True, exist_ok=True)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    return ExecutionContext(
        run_id="test-run",
        run_dir=run_dir,
        artifacts_dir=artifacts_dir,
        workspace_dir=tmp_path,
        flow_dir=tmp_path,
        mcp_log_dir=tmp_path,
        mcp_router=None,
    )


def test_numeric_literal_is_not_treated_as_path(tmp_path: Path) -> None:
    context = _make_context(tmp_path)

    value = McpStep._resolve_variable(context, "1.0")

    assert value == "1.0"


def test_relative_filename_resolves_to_run_dir(tmp_path: Path) -> None:
    context = _make_context(tmp_path)

    value = McpStep._resolve_variable(context, "config.json")

    assert value.endswith("config.json")
    assert value.startswith(str(context.run_dir))


def test_hidden_file_pattern_is_treated_as_path(tmp_path: Path) -> None:
    context = _make_context(tmp_path)

    value = McpStep._resolve_variable(context, ".env")

    assert value.endswith(".env")
    assert value.startswith(str(context.run_dir))
