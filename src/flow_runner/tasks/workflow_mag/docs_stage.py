"""DocsSAG integration stage for WorkFlowMAG pipeline."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Sequence

from . import common


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trigger DocsSAG drafting stage.")
    parser.add_argument("--config", required=True, help="Workflow configuration path.")
    return parser.parse_args(argv)


def execute(config_path: str) -> Path:
    config = common.load_config(config_path)
    run_id = os.environ.get("AIAMS_RUN_ID", "local-run")
    output_dir = Path(common.expand_path_template(config["paths"]["output_dir"], run_id)) / "docs"
    common.ensure_output_dir(output_dir)

    target = config.get("documentation", {}).get("target", "docs/generated/workflow-mag.md")
    doc_path = output_dir / "draft.md"
    content = "\n".join(
        [
            "# Workflow Draft (Placeholder)",
            "",
            f"- Target: {target}",
            "- Status: awaiting DocsSAG execution",
        ]
    )
    doc_path.write_text(content, encoding="utf-8")
    common.log("docs", f"Draft placeholder prepared at {doc_path}")
    return doc_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execute(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
