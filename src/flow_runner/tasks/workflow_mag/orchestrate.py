"""WorkFlowMAG planning stage executed via Flow Runner."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from . import common


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="WorkFlowMAG orchestration stage")
    parser.add_argument("--config", required=True, help="Path to workflow configuration JSON.")
    parser.add_argument(
        "--stage",
        default="plan",
        help="Stage label recorded in artifacts (default: plan).",
    )
    return parser.parse_args(argv)


def execute(config_path: str, stage: str = "plan") -> Path:
    config = common.load_config(config_path)
    run_id = os.environ.get("MAG_RUN_ID", "local-run")

    context = common.build_runtime_context(config, run_id=run_id)
    output_dir = context.output_dir

    common.log(stage, f"Initialising run {run_id} for task {config['task']['name']}")
    plan_artifact = {
        "run_id": run_id,
        "task": config["task"],
        "categories": config["task"].get("categories", []),
        "notes": "Workflow plan established. Subsequent stages will populate downstream artifacts.",
    }
    path = output_dir / "plan.json"
    path.write_text(json.dumps(plan_artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    context.register_artifacts({f"{stage}_plan": str(path)})
    context.record_step(
        agent="WorkflowMAG",
        results=[{"stage": stage, "status": "completed"}],
        artifacts={f"{stage}_plan": str(path)},
        metadata={"config_path": str(Path(config_path).resolve())},
    )
    return path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execute(args.config, args.stage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
