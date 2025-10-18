"""Execution helpers for agent subprocess calls."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from .runtime import RuntimeContext


@dataclass
class ExecutionResult:
    """Normalised subprocess execution result."""

    step: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    duration_sec: float
    timestamp: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def prepare_environment(context: RuntimeContext | None = None) -> dict[str, str]:
    """Return a subprocess-ready environment with runtime metadata."""

    env = os.environ.copy()
    root = str(Path.cwd())
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = f"{root}:{existing}" if existing else root
    if context:
        env.update(context.as_env())
    return env


def run_subprocess(
    command: Iterable[str],
    *,
    step: str,
    context: RuntimeContext | None = None,
    cwd: Path | None = None,
    env_extra: dict[str, str] | None = None,
    check: bool = False,
) -> ExecutionResult:
    """Execute a command and capture structured results."""

    cmd_list = [str(part) for part in command]
    start = time.time()
    env = prepare_environment(context)
    if env_extra:
        env.update({k: str(v) for k, v in env_extra.items()})

    process = subprocess.run(
        cmd_list,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
        env=env,
    )
    duration = round(time.time() - start, 3)
    timestamp = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    result = ExecutionResult(
        step=step,
        command=cmd_list,
        returncode=process.returncode,
        stdout=process.stdout.strip(),
        stderr=process.stderr.strip(),
        duration_sec=duration,
        timestamp=timestamp,
    )

    if check and result.returncode != 0:
        payload = json.dumps(result.as_dict(), ensure_ascii=False, indent=2)
        raise RuntimeError(f"Step '{step}' failed:\n{payload}")

    return result


def python_command(script: str, *args: str) -> list[str]:
    """Convenience helper to build a python command list."""

    candidate = Path(script)
    if candidate.is_absolute() and candidate.exists():
        return [sys.executable, str(candidate), *map(str, args)]

    scripts_dir = Path("src") / "automation" / "scripts"
    target = scripts_dir / candidate
    if not target.exists() and script.endswith(".py"):
        target = target.with_suffix(".py")
    return [sys.executable, str(target), *map(str, args)]
