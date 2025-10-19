"""Helpers for launching the shared MCP gateway.

The Multi Agent Governance stack keeps all routing defaults in
`.mcp/.mcp-config.yaml`.  When Codex-driven stages spin up their own
gateway they should first consult this helper so command lines and
environment flags remain consistent across tools.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import yaml

_DEFAULT_CONFIG_PATH = Path(".mcp/.mcp-config.yaml")
_DEFAULT_ENV_FILE = Path(".mcp/.env.mcp")


@dataclass(frozen=True)
class GatewaySpec:
    """Resolved connection parameters for the MCP gateway."""

    command: str | None = None
    args: Sequence[str] = ()
    env: dict[str, str] | None = None
    cwd: str | None = None

    def summary(self) -> str:
        command = self.command or "stdio"
        arg_preview = " ".join(self.args[:6])
        if len(self.args) > 6:
            arg_preview += " ..."
        return f"{command} {arg_preview}".strip()


def _load_env_file(path: Path) -> dict[str, str]:
    """Load key/value pairs from the shared MCP env file."""

    try:
        raw_text = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    env: dict[str, str] = {}
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :].strip()
        if "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        if not key:
            continue
        value = value.strip()
        if value.startswith(("\"", "'")) and value.endswith(value[0]) and len(value) >= 2:
            value = value[1:-1]
        env[key] = value

    if env:
        return env

    try:
        data = yaml.safe_load(raw_text)
    except (yaml.YAMLError, TypeError):
        return {}
    if not isinstance(data, dict):
        return {}
    return {str(key): str(value) for key, value in data.items()}


def _merge_env(env_sources: Iterable[dict[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for chunk in env_sources:
        result.update(chunk)
    return result


def default_gateway_args() -> list[str]:
    """Return CLI arguments for launching the shared MCP gateway."""

    if _DEFAULT_CONFIG_PATH.exists():
        return ["run", "--config", str(_DEFAULT_CONFIG_PATH.resolve())]
    return ["run"]


def resolve_gateway_spec() -> GatewaySpec:
    """Resolve command, arguments, and environment overrides for the gateway."""

    command = os.environ.get("MAG_MCP_GATEWAY_COMMAND", "mcp")
    args = list(default_gateway_args())

    env_chunks: list[dict[str, str]] = []
    if _DEFAULT_ENV_FILE.exists():
        env_chunks.append(_load_env_file(_DEFAULT_ENV_FILE))

    extra_env_spec = os.environ.get("MAG_MCP_GATEWAY_ENV", "")
    if extra_env_spec:
        for token in extra_env_spec.split(","):
            key, _, value = token.partition("=")
            key = key.strip()
            if key:
                env_chunks.append({key: value})

    env = _merge_env(env_chunks) or None
    cwd = os.environ.get("MAG_MCP_GATEWAY_CWD")
    return GatewaySpec(command=command, args=args, env=env, cwd=cwd)


__all__ = ["GatewaySpec", "default_gateway_args", "resolve_gateway_spec"]
