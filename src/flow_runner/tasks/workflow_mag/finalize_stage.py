"""Finalisation stage summarising WorkFlowMAG run results."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from . import common


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collate outputs at the end of the WorkFlowMAG pipeline.")
    parser.add_argument("--config", required=True, help="Workflow configuration path.")
    return parser.parse_args(argv)


def execute(config_path: str) -> Path:
    config = common.load_config(config_path)
    run_id = os.environ.get("AIAMS_RUN_ID", "local-run")
    output_dir = Path(common.expand_path_template(config["paths"]["output_dir"], run_id))
    common.ensure_output_dir(output_dir)

    summary = {
        "run_id": run_id,
        "task": config["task"],
        "artifacts": [
            "plan.json",
            "docs/draft.md",
            "prompts/prompt_package.json",
            "context/context_plan.json",
            "qa/qa_report.json",
            "operations/operations_summary.json"
        ],
        "status": "pipeline scaffold complete; awaiting agent execution.",
    }
    summary_path = output_dir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    common.log("finalize", f"Workflow summary written to {summary_path}")
    return summary_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execute(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
