"""Helpers for loading MCP router configuration from .mcp/.mcp-config.yaml."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

DEFAULT_CONFIG_PATH = ".mcp/.mcp-config.yaml"
DEFAULT_ENV_PATH = ".mcp/.env.mcp"
_ENV_PATTERN = re.compile(r"\$\{([^}:]+)(?::-(.*?))?\}")


def load_settings(
    *,
    base_dir: Path | None = None,
    config_path: str | os.PathLike[str] | None = None,
) -> dict[str, Any]:
    """Load and interpolate the MCP configuration file.

    Environment files listed in the config are sourced before interpolation.
    """

    root = Path(base_dir) if base_dir is not None else Path.cwd()
    override_config = config_path or os.getenv("MCP_CONFIG_PATH")
    resolved_config = _resolve_config_path(root, override_config)
    resolved_env = _resolve_env_path(root, resolved_config, os.getenv("MCP_ENV_FILE"))

    if resolved_env.exists():
        load_dotenv(resolved_env, override=False)
    elif os.getenv("MCP_ENV_FILE"):
        raise FileNotFoundError(f"configured MCP env file not found: {resolved_env}")

    if not resolved_config.exists():
        if override_config:
            raise FileNotFoundError(f"configured MCP config file not found: {resolved_config}")
        return {}

    raw_data = yaml.safe_load(resolved_config.read_text(encoding="utf-8")) or {}
    for candidate in _iter_env_files(raw_data, resolved_config.parent):
        if candidate.exists():
            load_dotenv(candidate, override=False)

    return _interpolate(raw_data)


def _resolve_config_path(root: Path, override: str | os.PathLike[str] | None) -> Path:
    if override:
        candidate = Path(override)
        if not candidate.is_absolute():
            candidate = root / candidate
        return candidate
    default_target = Path(DEFAULT_CONFIG_PATH)
    found = _find_upwards(root, default_target)
    if found is not None:
        return found
    return root / default_target


def _resolve_env_path(
    root: Path,
    config_path: Path,
    override: str | os.PathLike[str] | None,
) -> Path:
    if override:
        candidate = Path(override)
        if not candidate.is_absolute():
            candidate = root / candidate
        return candidate
    default_name = Path(DEFAULT_ENV_PATH).name
    return config_path.parent / default_name


def _find_upwards(start: Path, relative: Path) -> Path | None:
    for base in (start, *start.parents):
        candidate = base / relative
        if candidate.exists():
            return candidate
    return None


def _iter_env_files(config: dict[str, Any], config_dir: Path) -> list[Path]:
    env_section = config.get("env")
    if not isinstance(env_section, dict):
        return []
    files = env_section.get("files", [])
    if not isinstance(files, list):
        return []
    results: list[Path] = []
    for entry in files:
        if not isinstance(entry, str):
            continue
        path = Path(entry)
        if not path.is_absolute():
            path = config_dir / path
        results.append(path)
    return results


def _interpolate(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _interpolate(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_interpolate(item) for item in value]
    if isinstance(value, str):
        return _expand_env(value)
    return value


def _expand_env(raw: str) -> str:
    def replacer(match: re.Match[str]) -> str:
        var_name = match.group(1)
        default = match.group(2)
        env_value = os.getenv(var_name)
        if env_value not in (None, ""):
            return env_value
        if default is not None:
            return default
        return match.group(0)

    interpolated = _ENV_PATTERN.sub(replacer, raw)
    return os.path.expandvars(interpolated)
