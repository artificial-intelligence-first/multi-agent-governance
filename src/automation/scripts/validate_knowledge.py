#!/usr/bin/env python3
"""Validation routine for KnowledgeMag assets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_REQUEST_FIELDS = {"id", "version", "knowledge_domain", "title", "summary", "audience", "topics"}
REQUIRED_RESPONSE_FIELDS = {
    "id",
    "version",
    "knowledge_domain",
    "title",
    "summary",
    "audience",
    "knowledge_cards",
    "source_index",
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
    request_example = contracts_root / "examples" / "knowledge" / "request.json"
    response_example = contracts_root / "examples" / "knowledge" / "response.json"

    if not request_example.exists() or not response_example.exists():
        raise SystemExit("Knowledge examples are missing. Populate agents/contracts/examples/knowledge/.")

    assert_fields(request_example, REQUIRED_REQUEST_FIELDS)
    assert_fields(response_example, REQUIRED_RESPONSE_FIELDS)

    prompt_path = repo_root / "agents" / "main-agents" / "knowledge-mag" / "prompts" / "curate.prompt.yaml"
    if not prompt_path.exists():
        raise SystemExit("KnowledgeMag prompt not found.")

    workflow_path = repo_root / "agents" / "main-agents" / "knowledge-mag" / "workflows"
    if not (workflow_path / "curate_knowledge.wf.yaml").exists():
        raise SystemExit("KnowledgeMag workflow not found.")

    sop_dir = repo_root / "agents" / "main-agents" / "knowledge-mag" / "sop"
    for filename in ("README.md", "preflight.yaml", "rollback.yaml"):
        if not (sop_dir / filename).exists():
            raise SystemExit(f"Missing KnowledgeMag SOP artifact: {filename}")

    print("KnowledgeMag assets validated successfully.")


if __name__ == "__main__":
    sys.exit(main())
