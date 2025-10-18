"""GovernanceSAG integration stage."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from . import common

GOVERNANCE_SRC = (
    Path(__file__).resolve().parents[4]
    / "agents"
    / "sub-agents"
    / "governance-sag"
    / "src"
)

if GOVERNANCE_SRC.exists():
    import sys

    if str(GOVERNANCE_SRC) not in sys.path:
        sys.path.insert(0, str(GOVERNANCE_SRC))

try:
    from governance_sag import GovernanceSAG
except ImportError as exc:  # pragma: no cover - import failure surfaces at runtime
    raise RuntimeError("GovernanceSAG package not available") from exc

DEFAULT_SOURCES = [
    "AGENTS.md",
    "agents/AGENTS.md",
    "agents/SSOT.md",
    ".mcp/AGENTS.md",
    "CHANGELOG.md",
    "PLANS.md",
]

DEFAULT_CHECKS = [
    "AGENTS cascade alignment",
    "SSOT propagation",
    "CHANGELOG Keep a Changelog compliance",
    "ExecPlan freshness",
    "Telemetry capture under telemetry/runs/<run_id>/governance/",
]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run GovernanceSAG compliance audit scaffold.")
    parser.add_argument("--config", required=True, help="Workflow configuration path.")
    return parser.parse_args(argv)


def execute(config_path: str) -> Path:
    config = common.load_config(config_path)
    run_id = os.environ.get("MAG_RUN_ID", "local-run")
    runtime_ctx = common.build_runtime_context(config, run_id=run_id)
    output_dir = runtime_ctx.output_dir / "governance"
    common.ensure_output_dir(output_dir)

    governance_cfg = config.get("governance", {})
    checks = governance_cfg.get("checks") or DEFAULT_CHECKS
    sources = governance_cfg.get("sources") or DEFAULT_SOURCES
    agent = GovernanceSAG()
    result = agent.run(run_id=run_id, output_dir=output_dir, config={"checks": checks, "sources": sources})

    artifact_path = output_dir / "governance_report.json"
    if not artifact_path.exists():  # pragma: no cover - defensive
        artifact_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    common.log("governance", f"Governance report generated at {artifact_path}")
    runtime_ctx.register_artifacts({"governance_report": str(artifact_path)})
    runtime_ctx.record_step(
        agent="GovernanceSAG",
        results=[{"status": result.get("status"), "drift": result.get("drift", [])}],
        artifacts={"governance_report": str(artifact_path)},
        metadata={
            "config_path": str(Path(config_path).resolve()),
            "checks": checks,
            "sources": sources,
        },
    )
    return artifact_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execute(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
