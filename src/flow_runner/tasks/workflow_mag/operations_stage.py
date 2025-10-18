"""OperationsMAG integration stage."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from . import common


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run OperationsMAG telemetry aggregation.")
    parser.add_argument("--config", required=True, help="Workflow configuration path.")
    return parser.parse_args(argv)


def execute(config_path: str) -> Path:
    config = common.load_config(config_path)
    run_id = os.environ.get("MAG_RUN_ID", "local-run")
    runtime_ctx = common.build_runtime_context(config, run_id=run_id)
    output_dir = runtime_ctx.output_dir / "operations"
    common.ensure_output_dir(output_dir)

    budgets = config.get("operations", {}).get("telemetry_budget_s", {})
    artifact = {
        "telemetry_budget_s": budgets,
        "status": "pending OperationsMAG analysis",
    }
    artifact_path = output_dir / "operations_summary.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    common.log("operations", f"Operations summary scaffold written to {artifact_path}")
    runtime_ctx.register_artifacts({"operations_summary": str(artifact_path)})
    runtime_ctx.record_step(
        agent="OperationsMAG",
        results=[{"status": "scaffolded"}],
        artifacts={"operations_summary": str(artifact_path)},
        metadata={"config_path": str(Path(config_path).resolve())},
    )
    return artifact_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execute(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
