"""Shared helpers for contract validation scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def ensure_exists(path: str | Path) -> Path:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Missing required file: {file_path}")
    return file_path
