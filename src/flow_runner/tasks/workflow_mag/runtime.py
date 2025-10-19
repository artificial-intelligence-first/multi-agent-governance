"""Runtime context helpers shared across workflow stages."""

from __future__ import annotations

import json
import os
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any, Union

DEFAULT_FLOW = "workflow-mag"
DEFAULT_OUTPUT_ROOT = Path("telemetry/logs/runtime")
DEFAULT_LOG_ROOT = Path("telemetry/logs/runtime")


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return max(int(raw), 1)
    except ValueError:
        return default


DEFAULT_CODEX_MODEL = os.environ.get("MAG_CODEX_MODEL", "gpt-5-codex-medium")
DEFAULT_CODEX_PROMPT_LIMIT = _env_int("MAG_CODEX_PROMPT_LIMIT", 8192)
DEFAULT_CODEX_PROMPT_BUFFER = max(_env_int("MAG_CODEX_PROMPT_BUFFER", 512), 0)


def _env_float(name: str, default: float | None) -> float | None:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    if value <= 0:
        return default
    return value


DEFAULT_CODEX_TIMEOUT_S = _env_float("MAG_CODEX_MCP_TIMEOUT", 180.0)


def _ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _coerce_float(value: Any, default: float | None) -> float | None:
    if value is None:
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    if parsed <= 0:
        return default
    return parsed


@dataclass
class StepRecord:
    """A normalised execution record for a single agent step."""

    agent: str
    results: list[dict[str, Any]]
    artifacts: dict[str, str]
    metadata: dict[str, Any]


@dataclass
class TokenPolicy:
    """Runtime token enforcement settings for Codex prompts."""

    model: str
    limit: int
    buffer: int = 0
    timeout_s: float | None = None


@dataclass
class RuntimeContext:
    """Parsed context payload shared across agents and flows."""

    run_id: str
    flow: str
    output_dir: Path
    log_dir: Path
    runtime: dict[str, Any]
    slug: str | None = None
    input_uri: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    _history: list[StepRecord] = field(default_factory=list, init=False)
    _artifacts: dict[str, str] = field(default_factory=dict, init=False)
    _lock: RLock = field(init=False, repr=False, compare=False)

    @classmethod
    def from_payload(cls, payload: dict[str, Any] | None) -> RuntimeContext:
        data = dict(payload or {})
        run_id = str(
            data.get("run_id")
            or datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        )
        flow = str(data.get("flow") or DEFAULT_FLOW)

        raw_output = data.get("output_dir")
        if raw_output:
            output_dir = Path(raw_output).expanduser().resolve()
        else:
            output_dir = (DEFAULT_OUTPUT_ROOT / flow / run_id).resolve()

        raw_log = data.get("log_dir")
        if raw_log:
            log_dir = Path(raw_log).expanduser().resolve()
        else:
            log_dir = (output_dir / "logs").resolve()

        runtime_cfg = data.get("runtime")
        if runtime_cfg is None:
            runtime_cfg = {}
        elif not isinstance(runtime_cfg, dict):
            raise TypeError("context.runtime must be a mapping")

        slug = data.get("slug")
        input_uri = data.get("input_uri")

        ctx = cls(
            run_id=run_id,
            flow=flow,
            output_dir=_ensure_dir(output_dir),
            log_dir=_ensure_dir(log_dir),
            runtime=runtime_cfg,
            slug=slug,
            input_uri=input_uri,
            raw=data,
        )
        _ensure_dir(ctx.steps_dir)
        ctx._load_existing_state()
        ctx._write_summary()
        return ctx

    def __post_init__(self) -> None:  # pragma: no cover - simple initialiser
        self._lock = RLock()

    @property
    def steps_dir(self) -> Path:
        return self.output_dir / "steps"

    def as_env(self) -> dict[str, str]:
        env = {
            "MAG_RUN_ID": self.run_id,
            "MAG_FLOW": self.flow,
            "MAG_OUTPUT_DIR": str(self.output_dir),
            "MAG_LOG_DIR": str(self.log_dir),
        }
        if self.slug:
            env["MAG_SLUG"] = self.slug
        if self.input_uri:
            env["MAG_INPUT_URI"] = self.input_uri
        return env

    def get_section(self, name: str, *, required: bool = False) -> dict[str, Any]:
        section = self.runtime.get(name)
        if section is None:
            if required:
                raise KeyError(f"runtime.{name} config is required for flow '{self.flow}'")
            return {}
        if not isinstance(section, dict):
            raise TypeError(f"runtime.{name} must be a mapping")
        return section

    def resolve_codex_policy(self, agent: str) -> TokenPolicy:
        """Resolve token enforcement policy for the given agent."""

        model = DEFAULT_CODEX_MODEL
        limit = DEFAULT_CODEX_PROMPT_LIMIT
        buffer = DEFAULT_CODEX_PROMPT_BUFFER
        timeout_s = DEFAULT_CODEX_TIMEOUT_S

        settings = self.runtime.get("codex_mcp")
        if isinstance(settings, dict):
            model = str(settings.get("model") or model)
            limit = _coerce_int(settings.get("prompt_limit"), limit)
            buffer = max(_coerce_int(settings.get("prompt_buffer"), buffer), 0)
            timeout_s = _coerce_float(settings.get("timeout_s"), timeout_s)

            agents_cfg = settings.get("agents")
            if isinstance(agents_cfg, dict):
                agent_cfg = agents_cfg.get(agent)
                if isinstance(agent_cfg, dict):
                    model = str(agent_cfg.get("model") or model)
                    limit = _coerce_int(agent_cfg.get("prompt_limit"), limit)
                    buffer = max(_coerce_int(agent_cfg.get("prompt_buffer"), buffer), 0)
                    timeout_s = _coerce_float(agent_cfg.get("timeout_s"), timeout_s)

        if limit <= 0:
            limit = 1
        return TokenPolicy(model=model, limit=limit, buffer=buffer, timeout_s=timeout_s)

    def register_artifacts(self, artifacts: dict[str, str]) -> None:
        with self._lock:
            for key, value in artifacts.items():
                if value is None:
                    continue
                self._artifacts[key] = self._normalise_path(value)

    def record_step(
        self,
        agent: str,
        results: Iterable[dict[str, Any]],
        *,
        artifacts: dict[str, str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        artifacts = artifacts or {}
        metadata = metadata or {}
        serialised_results = [dict(item) for item in results]
        with self._lock:
            record = StepRecord(
                agent=agent,
                results=serialised_results,
                artifacts={k: self._normalise_path(v) for k, v in artifacts.items() if v},
                metadata=metadata,
            )
            self._history.append(record)
            if artifacts:
                for key, value in artifacts.items():
                    if value is None:
                        continue
                    self._artifacts[key] = self._normalise_path(value)

            step_path = self.steps_dir / f"{agent}.json"
            payload = {
                "run_id": self.run_id,
                "flow": self.flow,
                "agent": agent,
                "timestamp": datetime.now(UTC).isoformat(),
                "results": serialised_results,
                "artifacts": record.artifacts,
                "metadata": metadata,
            }
            step_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self._write_summary()
            return step_path

    def _write_summary(self) -> None:
        with self._lock:
            summary = {
                "run_id": self.run_id,
                "flow": self.flow,
                "slug": self.slug,
                "input_uri": self.input_uri,
                "output_dir": str(self.output_dir),
                "log_dir": str(self.log_dir),
                "steps": [
                    {
                        "agent": item.agent,
                        "results": item.results,
                        "artifacts": item.artifacts,
                        "metadata": item.metadata,
                    }
                    for item in self._history
                ],
                "artifacts": dict(self._artifacts),
            }
        summary_path = self.output_dir / "summary.json"
        summary_path.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _load_existing_state(self) -> None:
        """Load summary/steps when the context directory already exists."""

        summary_path = self.output_dir / "summary.json"
        if not summary_path.exists():
            return
        try:
            payload = json.loads(summary_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        steps = payload.get("steps")
        artifacts = payload.get("artifacts")
        if isinstance(artifacts, dict):
            self._artifacts.update({str(k): str(v) for k, v in artifacts.items()})
        if isinstance(steps, list):
            for item in steps:
                if not isinstance(item, dict):
                    continue
                agent = item.get("agent")
                results = item.get("results")
                metadata = item.get("metadata") or {}
                artifacts_map = item.get("artifacts") or {}
                if not isinstance(agent, str):
                    continue
                if not isinstance(results, list):
                    results = []
                if not isinstance(metadata, dict):
                    metadata = {}
                if not isinstance(artifacts_map, dict):
                    artifacts_map = {}
                record = StepRecord(
                    agent=agent,
                    results=[dict(r) for r in results if isinstance(r, dict)],
                    artifacts={str(k): str(v) for k, v in artifacts_map.items()},
                    metadata=dict(metadata),
                )
                self._history.append(record)

    def to_payload(self) -> dict[str, Any]:
        payload = dict(self.raw)
        payload.update(
            {
                "run_id": self.run_id,
                "flow": self.flow,
                "output_dir": str(self.output_dir),
                "log_dir": str(self.log_dir),
                "runtime": self.runtime,
            }
        )
        if self.slug:
            payload["slug"] = self.slug
        if self.input_uri:
            payload["input_uri"] = self.input_uri
        return payload

    def get_artifact(self, name: str) -> Path | None:
        """Retrieve the path of a previously registered artifact."""

        with self._lock:
            value = self._artifacts.get(name)
        if value is None:
            return None
        return Path(value)

    def list_artifacts(self) -> dict[str, str]:
        """Return a copy of the registered artifact mapping."""

        with self._lock:
            return dict(self._artifacts)

    def snapshot_history(self) -> list[StepRecord]:
        """Return a shallow copy of the recorded step history."""

        with self._lock:
            return list(self._history)

    def get_step_record(self, agent: str) -> dict[str, Any] | None:
        """Load the persisted step record for the given agent if available."""

        path = self.steps_dir / f"{agent}.json"
        if not path.exists():
            return None
        raw = path.read_text(encoding="utf-8")
        return json.loads(raw)

    @staticmethod
    def _normalise_path(value: str) -> str:
        path = Path(str(value)).expanduser()
        return str(path.resolve())


ContextLike = Union[RuntimeContext, dict[str, Any], None]


def ensure_context(value: ContextLike) -> RuntimeContext:
    """Convert arbitrary context payloads into a RuntimeContext instance."""

    if isinstance(value, RuntimeContext):
        return value
    if isinstance(value, dict) or value is None:
        return RuntimeContext.from_payload(value)
    raise TypeError(f"Unsupported context payload: {type(value)!r}")
