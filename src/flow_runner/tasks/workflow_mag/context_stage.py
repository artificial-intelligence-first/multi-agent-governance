"""ContextSAG integration stage."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from . import common


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trigger ContextSAG stage for context bundle assembly.")
    parser.add_argument("--config", required=True, help="Workflow configuration path.")
    return parser.parse_args(argv)


def execute(config_path: str) -> Path:
    config = common.load_config(config_path)
    run_id = os.environ.get("MAG_RUN_ID", "local-run")
    runtime_ctx = common.build_runtime_context(config, run_id=run_id)
    output_dir = runtime_ctx.output_dir / "context"
    common.ensure_output_dir(output_dir)

    context_cfg = config.get("context", {})
    artifact = {
        "primary_sources": context_cfg.get("primary_sources", []),
        "status": "awaiting ContextSAG",
        "bundles": [],
    }
    artifact_path = output_dir / "context_plan.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    common.log("context", f"Context plan scaffold written to {artifact_path}")
    runtime_ctx.register_artifacts({"context_plan": str(artifact_path)})
    runtime_ctx.record_step(
        agent="ContextSAG",
        results=[{"status": "scaffolded"}],
        artifacts={"context_plan": str(artifact_path)},
        metadata={"config_path": str(Path(config_path).resolve())},
    )
    return artifact_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execute(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
