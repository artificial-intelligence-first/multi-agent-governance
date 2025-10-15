#!/usr/bin/env python3
"""Validation routine for DocsSAG assets."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_REQUEST_FIELDS = {"id", "version", "doc_type", "title", "summary", "audience", "sections"}
REQUIRED_RESPONSE_FIELDS = {
    "id",
    "version",
    "doc_type",
    "title",
    "document_markdown",
    "sections",
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
    request_example = contracts_root / "examples" / "docs-sag" / "request.json"
    response_example = contracts_root / "examples" / "docs-sag" / "response.json"

    if not request_example.exists() or not response_example.exists():
        raise SystemExit("DocsSAG examples are missing. Populate agents/contracts/examples/docs-sag/.")

    assert_fields(request_example, REQUIRED_REQUEST_FIELDS)
    assert_fields(response_example, REQUIRED_RESPONSE_FIELDS)

    prompt_path = repo_root / "agents" / "sub-agents" / "docs-sag" / "prompts" / "draft.prompt.yaml"
    if not prompt_path.exists():
        raise SystemExit("DocsSAG prompt not found.")

    workflow_path = repo_root / "agents" / "sub-agents" / "docs-sag" / "workflows" / "draft_docs.wf.yaml"
    if not workflow_path.exists():
        raise SystemExit("DocsSAG workflow not found.")

    sop_dir = repo_root / "agents" / "sub-agents" / "docs-sag" / "sop"
    for filename in ("README.md", "preflight.yaml", "rollback.yaml"):
        if not (sop_dir / filename).exists():
            raise SystemExit(f"Missing DocsSAG SOP artifact: {filename}")

    print("DocsSAG assets validated successfully.")


if __name__ == "__main__":
    sys.exit(main())
