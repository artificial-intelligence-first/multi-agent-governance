from __future__ import annotations

from pathlib import Path

from flow_runner.tasks.workflow_mag import common


def test_build_runtime_context_honors_legacy_logs_dir(tmp_path: Path) -> None:
    config = {
        "paths": {
            "output_dir": str(tmp_path / "runs/${RUN_ID}"),
            "logs_dir": str(tmp_path / "legacy_logs/${RUN_ID}"),
        },
        "task": {"flow": "workflow-mag"},
    }
    ctx = common.build_runtime_context(config, run_id="test-run")
    assert ctx.log_dir == (tmp_path / "legacy_logs/test-run").resolve()


def test_build_runtime_context_prefers_log_dir_key(tmp_path: Path) -> None:
    config = {
        "paths": {
            "output_dir": str(tmp_path / "runs/${RUN_ID}"),
            "log_dir": str(tmp_path / "primary_logs/${RUN_ID}"),
            "logs_dir": str(tmp_path / "legacy_logs/${RUN_ID}"),
        },
        "task": {"flow": "workflow-mag"},
    }
    ctx = common.build_runtime_context(config, run_id="test-run")
    assert ctx.log_dir == (tmp_path / "primary_logs/test-run").resolve()
