"""QAMAG integration stage."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from . import common


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run QAMAG review stage.")
    parser.add_argument("--config", required=True, help="Workflow configuration path.")
    return parser.parse_args(argv)


def execute(config_path: str) -> Path:
    config = common.load_config(config_path)
    run_id = os.environ.get("MAG_RUN_ID", "local-run")
    runtime_ctx = common.build_runtime_context(config, run_id=run_id)
    output_dir = runtime_ctx.output_dir / "qa"
    common.ensure_output_dir(output_dir)

    checklist = config.get("qa", {}).get("checklist", [])
    artifact = {
        "checklist": checklist,
        "status": "pending QAMAG review",
        "findings": [],
    }
    artifact_path = output_dir / "qa_report.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    common.log("qa", f"QA report stub written to {artifact_path}")
    runtime_ctx.register_artifacts({"qa_report": str(artifact_path)})
    runtime_ctx.record_step(
        agent="QAMAG",
        results=[{"status": "scaffolded"}],
        artifacts={"qa_report": str(artifact_path)},
        metadata={"config_path": str(Path(config_path).resolve())},
    )
    return artifact_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execute(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
