#!/usr/bin/env python3
"""Validation routine for ContextSAG assets."""

from __future__ import annotations

import json
from pathlib import Path

REQUIRED_REQUEST_FIELDS = {"id", "version", "objective", "primary_use_case", "context_inputs"}
REQUIRED_RESPONSE_FIELDS = {
    "id",
    "version",
    "objective",
    "primary_use_case",
    "context_briefs",
    "assembly_plan",
    "risk_register",
    "follow_up_questions",
    "diagnostics",
}


def assert_fields(path: Path, required_fields: set[str]) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    present = set(document.keys())
    missing = required_fields - present
    if missing:
        raise SystemExit(f"{path} missing required fields: {', '.join(sorted(missing))}")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    contracts_root = repo_root / "agents" / "contracts"
    request_example = contracts_root / "examples" / "context-sag" / "request.json"
    response_example = contracts_root / "examples" / "context-sag" / "response.json"

    if not request_example.exists() or not response_example.exists():
        raise SystemExit("ContextSAG examples are missing. Populate agents/contracts/examples/context-sag/.")

    assert_fields(request_example, REQUIRED_REQUEST_FIELDS)
    assert_fields(response_example, REQUIRED_RESPONSE_FIELDS)

    prompt_path = repo_root / "agents" / "sub-agents" / "context-sag" / "prompts" / "context_assembly.prompt.yaml"
    if not prompt_path.exists():
        raise SystemExit("ContextSAG prompt not found.")

    workflow_path = repo_root / "agents" / "sub-agents" / "context-sag" / "workflows" / "context_plan_demo.wf.yaml"
    if not workflow_path.exists():
        raise SystemExit("ContextSAG workflow not found.")

    sop_dir = repo_root / "agents" / "sub-agents" / "context-sag" / "sop"
    for filename in ("README.md", "preflight.yaml", "rollback.yaml"):
        if not (sop_dir / filename).exists():
            raise SystemExit(f"Missing ContextSAG SOP artifact: {filename}")

    docs_dir = repo_root / "agents" / "sub-agents" / "context-sag" / "docs"
    for filename in ("overview.md", "runbook.md"):
        if not (docs_dir / filename).exists():
            raise SystemExit(f"Missing ContextSAG documentation asset: {filename}")

    print("ContextSAG assets validated successfully.")


if __name__ == "__main__":
    main()
