"""PromptSAG integration stage."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from . import common


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trigger PromptSAG stage for prompt package assembly.")
    parser.add_argument("--config", required=True, help="Workflow configuration path.")
    return parser.parse_args(argv)


def execute(config_path: str) -> Path:
    config = common.load_config(config_path)
    run_id = os.environ.get("AIAMS_RUN_ID", "local-run")
    output_dir = Path(common.expand_path_template(config["paths"]["output_dir"], run_id)) / "prompts"
    common.ensure_output_dir(output_dir)

    prompt_cfg = config.get("prompt", {})
    artifact = {
        "audience": prompt_cfg.get("audience", "unspecified"),
        "style": prompt_cfg.get("style", "structured"),
        "status": "awaiting PromptSAG",
        "messages": [],
    }
    artifact_path = output_dir / "prompt_package.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    common.log("prompts", f"Prompt package scaffold written to {artifact_path}")
    return artifact_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execute(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
