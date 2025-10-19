"""Skill execution guardrails for Flow Runner."""

from __future__ import annotations

import json
import os
import re
import subprocess
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Optional, Sequence

from mcp_router.redaction import mask_sensitive

DEFAULT_ALLOWLIST_PATH = Path("skills/ALLOWLIST.txt")
DEFAULT_TELEMETRY_PATH = Path("telemetry/skills/events.jsonl")


@dataclass(frozen=True)
class AllowlistEntry:
    """Parsed representation of a single allowlist row."""

    sha256: str
    args_pattern: str


class SkillExecutionError(RuntimeError):
    """Raised when a skill script is blocked or fails."""

    def __init__(self, message: str, *, status: str, reason: str) -> None:
        super().__init__(message)
        self.status = status
        self.reason = reason


class SkillExecutionGuard:
    """Enforce allowlist, hashing, and telemetry for skill scripts."""

    def __init__(
        self,
        *,
        root: Path,
        exec_enabled: bool,
        sandbox_mode: str = "read-only",
        allowlist_path: Optional[Path] = None,
        telemetry_path: Optional[Path] = None,
    ) -> None:
        self._root = root
        self._exec_enabled = exec_enabled
        self._sandbox_mode = sandbox_mode
        self._allowlist_path = (allowlist_path or (root / DEFAULT_ALLOWLIST_PATH)).resolve()
        self._telemetry_path = (telemetry_path or (root / DEFAULT_TELEMETRY_PATH)).resolve()
        self._allowlist = self._load_allowlist()
        self._telemetry_lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def execute(
        self,
        *,
        skill_name: str,
        script_path: str | Path,
        args: Sequence[str] | None = None,
        allow_exec: bool,
        workspace_dir: Optional[Path] = None,
        env: Optional[Mapping[str, str]] = None,
    ) -> Dict[str, object]:
        """Run a skill script if all guard conditions pass."""

        args = list(args or [])
        workspace = (workspace_dir or self._root).resolve()
        resolved_script = self._resolve_script(script_path)
        script_rel = resolved_script.relative_to(self._root).as_posix()
        self._emit_event(
            "skill_exec_attempt",
            {
                "path": script_rel,
                "script": script_rel,
                "skill": skill_name,
                "allow_exec": allow_exec,
                "sandbox": self._sandbox_mode,
                "args": list(args),
            },
        )

        if not self._exec_enabled:
            self._emit_blocked(script_rel, "skills_exec_disabled", skill=skill_name)
            raise SkillExecutionError(
                "skill execution disabled by feature flag",
                status="blocked",
                reason="skills_exec_disabled",
            )

        if not allow_exec:
            self._emit_blocked(script_rel, "skill_not_allow_exec", skill=skill_name)
            raise SkillExecutionError(
                "skill is not approved for execution",
                status="blocked",
                reason="skill_not_allow_exec",
            )

        entry = self._allowlist.get(script_rel)
        if entry is None:
            self._emit_blocked(script_rel, "missing_allowlist_entry", skill=skill_name)
            raise SkillExecutionError(
                f"script not present in allowlist: {script_rel}",
                status="blocked",
                reason="missing_allowlist_entry",
            )

        try:
            actual_hash = self._hash_file(resolved_script)
        except FileNotFoundError as exc:
            self._emit_blocked(script_rel, "script_not_found", skill=skill_name)
            raise SkillExecutionError(
                "script executable not found or lacks execute permissions",
                status="blocked",
                reason="script_not_found",
            ) from exc

        if actual_hash != entry.sha256:
            self._emit_blocked(script_rel, "hash_mismatch", skill=skill_name)
            raise SkillExecutionError(
                "script hash does not match allowlist entry",
                status="blocked",
                reason="hash_mismatch",
            )

        if entry.args_pattern:
            joined_args = " ".join(args)
            if not re.fullmatch(entry.args_pattern, joined_args):
                self._emit_blocked(script_rel, "args_not_allowed", skill=skill_name)
                raise SkillExecutionError(
                    "script arguments rejected by allowlist pattern",
                    status="blocked",
                    reason="args_not_allowed",
                )

        try:
            result = subprocess.run(
                [str(resolved_script), *args],
                cwd=workspace,
                env=self._build_env(env),
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as exc:
            self._emit_result(
                script_rel,
                status="failed",
                stdout=exc.stdout or "",
                stderr=exc.stderr or "",
                exit_code=exc.returncode,
                sha=actual_hash,
                skill=skill_name,
            )
            raise SkillExecutionError(
                f"skill script failed with exit code {exc.returncode}",
                status="failed",
                reason="non_zero_exit",
            ) from exc
        except FileNotFoundError as exc:
            self._emit_blocked(script_rel, "script_not_found", skill=skill_name)
            raise SkillExecutionError(
                "script executable not found or lacks execute permissions",
                status="blocked",
                reason="script_not_found",
            ) from exc
        except PermissionError as exc:
            self._emit_blocked(script_rel, "permission_denied", skill=skill_name)
            raise SkillExecutionError(
                "skill script is not executable or permission was denied",
                status="blocked",
                reason="permission_denied",
            ) from exc

        self._emit_result(
            script_rel,
            status="succeeded",
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=0,
            sha=actual_hash,
            skill=skill_name,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "path": script_rel,
        }

    # ------------------------------------------------------------------ #
    # Allowlist helpers
    # ------------------------------------------------------------------ #
    def _load_allowlist(self) -> Dict[str, AllowlistEntry]:
        entries: Dict[str, AllowlistEntry] = {}
        if not self._allowlist_path.exists():
            return entries
        for raw_line in self._iter_allowlist_lines():
            parts = raw_line.split()
            if len(parts) < 3:
                continue
            rel_path, sha, args_pattern = parts[0], parts[1], " ".join(parts[2:])
            key = Path(rel_path).as_posix()
            entries[key] = AllowlistEntry(sha256=sha, args_pattern=args_pattern)
        return entries

    def _iter_allowlist_lines(self) -> Iterable[str]:
        with self._allowlist_path.open("r", encoding="utf-8") as handle:
            for raw_line in handle:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                yield line

    def _resolve_script(self, path: str | Path) -> Path:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = (self._root / candidate).resolve()
        else:
            candidate = candidate.resolve()
        try:
            candidate.relative_to(self._root)
        except ValueError as exc:
            raise SkillExecutionError(
                "skill script must reside within the workspace root",
                status="blocked",
                reason="outside_workspace",
            ) from exc
        return candidate

    @staticmethod
    def _hash_file(path: Path) -> str:
        digest = sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _build_env(self, extra: Optional[Mapping[str, str]]) -> Dict[str, str]:
        env = {
            "SKILL_SANDBOX": self._sandbox_mode,
            "PATH": os.getenv("PATH", ""),
            "HOME": os.getenv("HOME", ""),
        }
        if extra:
            env.update(extra)
        return env

    # ------------------------------------------------------------------ #
    # Telemetry
    # ------------------------------------------------------------------ #
    def _emit_blocked(self, path: str, reason: str, *, skill: str) -> None:
        self._emit_result(
            path,
            status="blocked",
            stdout="",
            stderr="",
            exit_code=None,
            sha=None,
            reason=reason,
            skill=skill,
        )

    def _emit_result(
        self,
        path: str,
        *,
        status: str,
        stdout: str,
        stderr: str,
        exit_code: Optional[int],
        sha: Optional[str],
        reason: Optional[str] = None,
        skill: Optional[str] = None,
    ) -> None:
        payload = {
            "path": path,
            "script": path,
            "status": status,
            "stdout_preview": stdout[:160],
            "stderr_preview": stderr[:160],
            "exit_code": exit_code,
            "sha256": sha,
        }
        if reason:
            payload["reason"] = reason
        if skill:
            payload["skill"] = skill
        self._emit_event("skill_exec_result", payload)

    def _emit_event(self, event: str, data: Mapping[str, object]) -> None:
        serializable = mask_sensitive(dict(data))
        body = {
            "ts": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "event": event,
            "data": serializable,
        }
        self._telemetry_path.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(body, ensure_ascii=False)
        with self._telemetry_lock:
            with self._telemetry_path.open("a", encoding="utf-8") as handle:
                handle.write(line)
                handle.write("\n")


__all__ = ["AllowlistEntry", "SkillExecutionError", "SkillExecutionGuard"]
