#!/usr/bin/env python3
"""Validation routine for PromptSAG assets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_REQUEST_FIELDS = {"id", "version", "objective"}
REQUIRED_RESPONSE_FIELDS = {
    "id",
    "version",
    "objective",
    "prompt_components",
    "guardrails",
    "evaluation",
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
    request_example = contracts_root / "examples" / "prompt-sag" / "request.json"
    response_example = contracts_root / "examples" / "prompt-sag" / "response.json"

    if not request_example.exists() or not response_example.exists():
        raise SystemExit("PromptSAG examples are missing. Populate agents/contracts/examples/prompt-sag/.")

    assert_fields(request_example, REQUIRED_REQUEST_FIELDS)
    assert_fields(response_example, REQUIRED_RESPONSE_FIELDS)

    prompt_path = repo_root / "agents" / "sub-agents" / "prompt-sag" / "prompts" / "engineer.prompt.yaml"
    if not prompt_path.exists():
        raise SystemExit("PromptSAG prompt not found.")

    workflow_path = repo_root / "agents" / "sub-agents" / "prompt-sag" / "workflows" / "engineer_prompt.wf.yaml"
    if not workflow_path.exists():
        raise SystemExit("PromptSAG workflow not found.")

    sop_dir = repo_root / "agents" / "sub-agents" / "prompt-sag" / "sop"
    for filename in ("README.md", "preflight.yaml", "rollback.yaml"):
        if not (sop_dir / filename).exists():
            raise SystemExit(f"Missing PromptSAG SOP artifact: {filename}")

    if len(sys.argv) > 1 and sys.argv[1] not in {"--help", "-h"}:
        response_path = Path(sys.argv[1])
        if response_path.exists():
            assert_fields(response_path, REQUIRED_RESPONSE_FIELDS)

    print("PromptSAG assets validated successfully.")


if __name__ == "__main__":
    main()
