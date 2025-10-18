"""Shared utilities for WorkFlowMAG Flow Runner tasks."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

from .runtime import RuntimeContext


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


def build_runtime_context(config: Dict[str, Any], *, run_id: str) -> RuntimeContext:
    """Create a RuntimeContext from the workflow configuration."""

    paths = config.get("paths", {})
    raw_output = paths.get("output_dir", "telemetry/logs/runtime/${RUN_ID}")
    output_dir = Path(expand_path_template(raw_output, run_id))

    raw_log = paths.get("log_dir") or paths.get("logs_dir")
    log_dir = Path(expand_path_template(raw_log, run_id)) if raw_log else None

    runtime_cfg = config.get("runtime", {})
    payload: Dict[str, Any] = {
        "run_id": run_id,
        "flow": config.get("task", {}).get("flow", "workflow-mag"),
        "output_dir": str(output_dir),
        "runtime": runtime_cfg,
    }
    if log_dir:
        payload["log_dir"] = str(log_dir)

    slug = config.get("task", {}).get("slug")
    if slug:
        payload["slug"] = slug

    return RuntimeContext.from_payload(payload)
