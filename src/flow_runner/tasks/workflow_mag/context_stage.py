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
    run_id = os.environ.get("AIAMS_RUN_ID", "local-run")
    output_dir = Path(common.expand_path_template(config["paths"]["output_dir"], run_id)) / "context"
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
    return artifact_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execute(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
