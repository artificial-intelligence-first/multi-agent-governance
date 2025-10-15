"""Pytest configuration: ensure project packages are importable."""

from __future__ import annotations

import sys
from pathlib import Path


def _add_path(path: Path) -> None:
    if path.exists():
        sys.path.append(str(path))


REPO_ROOT = Path(__file__).resolve().parent

_PATHS = [
    REPO_ROOT / "src",
    REPO_ROOT / "src" / "flowrunner" / "src",
    REPO_ROOT / "src" / "mcprouter" / "src",
    REPO_ROOT / "agents" / "main-agents" / "knowledge-mag" / "src",
    REPO_ROOT / "agents" / "main-agents" / "workflow-mag" / "src",
    REPO_ROOT / "agents" / "main-agents" / "operations-mag" / "src",
    REPO_ROOT / "agents" / "main-agents" / "qa-mag" / "src",
    REPO_ROOT / "agents" / "sub-agents" / "docs-sag" / "src",
    REPO_ROOT / "agents" / "sub-agents" / "prompt-sag" / "src",
    REPO_ROOT / "agents" / "sub-agents" / "context-sag" / "src",
    REPO_ROOT / "agents" / "sub-agents" / "quality-sag" / "src",
    REPO_ROOT / "agents" / "sub-agents" / "reference-sag" / "src",
]

for _path in _PATHS:
    _add_path(_path)
