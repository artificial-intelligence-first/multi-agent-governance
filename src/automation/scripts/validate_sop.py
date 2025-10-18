#!/usr/bin/env python3
"""Validation routine for SOP (Standard Operating Procedures) assets."""

from __future__ import annotations

import sys
from pathlib import Path


def validate_sop_directory(sop_dir: Path) -> None:
    """Validate that a SOP directory contains required files."""
    required_files = ["README.md", "preflight.yaml", "rollback.yaml"]
    
    for filename in required_files:
        file_path = sop_dir / filename
        if not file_path.exists():
            raise SystemExit(f"Missing SOP artifact: {file_path}")
        
        # Check that files are not empty
        if file_path.stat().st_size == 0:
            raise SystemExit(f"Empty SOP file: {file_path}")


def main() -> None:
    """Validate all SOP directories in the repository."""
    repo_root = Path(__file__).resolve().parents[3]
    
    # Define all agent directories that should have SOP
    agent_dirs = [
        "agents/main-agents/knowledge-mag",
        "agents/main-agents/operations-mag", 
        "agents/main-agents/qa-mag",
        "agents/main-agents/workflow-mag",
        "agents/sub-agents/browser-sag",
        "agents/sub-agents/context-sag",
        "agents/sub-agents/docs-sag",
        "agents/sub-agents/governance-sag",
        "agents/sub-agents/mcp-sag",
        "agents/sub-agents/prompt-sag",
        "agents/sub-agents/quality-sag",
        "agents/sub-agents/reference-sag",
    ]
    
    validated_count = 0
    
    for agent_dir in agent_dirs:
        sop_dir = repo_root / agent_dir / "sop"
        if sop_dir.exists():
            validate_sop_directory(sop_dir)
            validated_count += 1
            print(f"✓ Validated SOP for {agent_dir}")
        else:
            print(f"⚠ No SOP directory found for {agent_dir}")
    
    if validated_count == 0:
        raise SystemExit("No SOP directories found to validate")
    
    print(f"\nSOP validation completed successfully. Validated {validated_count} SOP directories.")


if __name__ == "__main__":
    sys.exit(main())
