"""Shared utilities for WorkFlowMAG Flow Runner tasks."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


def load_config(config_path: str | Path) -> Dict[str, Any]:
    """Load JSON config with optional relative `extends` support."""
    path = Path(config_path).expanduser().resolve()
    data = _read_json(path)

    if "extends" in data:
        parent_path = (path.parent / data["extends"]).resolve()
        parent = load_config(parent_path)
        merged = _deep_merge(parent, {k: v for k, v in data.items() if k != "extends"})
        return merged

    return data


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def log(stage: str, message: str) -> None:
    print(f"[{stage}] {message}")


def expand_path_template(value: str, run_id: str | None = None) -> str:
    """Expand ${RUN_ID} placeholders and environment variables."""
    result = value
    if run_id:
        result = result.replace("${RUN_ID}", run_id)
    result = os.path.expandvars(result)
    return result
