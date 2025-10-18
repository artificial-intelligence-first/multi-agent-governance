"""BrowserSAG integration stage."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from . import common


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare BrowserSAG MCP run scaffolding.")
    parser.add_argument("--config", required=True, help="Workflow configuration path.")
    return parser.parse_args(argv)


def execute(config_path: str) -> Path:
    config = common.load_config(config_path)
    run_id = os.environ.get("MAG_RUN_ID", "local-run")
    runtime_ctx = common.build_runtime_context(config, run_id=run_id)
    output_dir = runtime_ctx.output_dir / "browser"
    common.ensure_output_dir(output_dir)

    browser_cfg = config.get("browser", {})
    targets = browser_cfg.get("targets", [])
    mcp_servers = browser_cfg.get(
        "mcp_servers",
        ["chrome-devtools", "playwright", "markitdown"],
    )
    expected_artifacts = browser_cfg.get(
        "expected_artifacts",
        ["screenshots", "accessibility_snapshots", "markdown_exports", "traces"],
    )
    instructions = browser_cfg.get("instructions", [])

    artifact_payload = {
        "run_id": run_id,
        "status": "awaiting BrowserSAG",
        "mcp_servers": mcp_servers,
        "targets": targets,
        "expected_artifacts": expected_artifacts,
        "notes": instructions,
    }
    artifact_path = output_dir / "browser_plan.json"
    artifact_path.write_text(json.dumps(artifact_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    common.log("browser", f"Browser plan scaffold written to {artifact_path}")
    runtime_ctx.register_artifacts({"browser_plan": str(artifact_path)})
    runtime_ctx.record_step(
        agent="BrowserSAG",
        results=[{"status": "scaffolded"}],
        artifacts={"browser_plan": str(artifact_path)},
        metadata={
            "config_path": str(Path(config_path).resolve()),
            "mcp_servers": mcp_servers,
        },
    )
    return artifact_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execute(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
