"""GovernanceSAG audit logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


RECENCY_WINDOW_DAYS = 60
PLAN_SECTIONS = ["Big Picture", "To-do", "Progress", "Decision Log", "Surprises"]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def _modified_within(path: Path, window: timedelta) -> bool:
    try:
        mtime = datetime.fromtimestamp(path.stat().st_mtime, UTC)
    except FileNotFoundError:
        return False
    return datetime.now(UTC) - mtime <= window


@dataclass
class GovernanceSAG:
    """Audit governance artefacts and persist findings."""

    clock: Any = field(default=datetime)

    def run(
        self,
        *,
        run_id: str,
        output_dir: str | Path,
        config: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        config = config or {}
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        window = timedelta(days=config.get("recency_window_days", RECENCY_WINDOW_DAYS))
        sources = list(config.get("sources") or [])
        if not sources:
            sources = [
                "AGENTS.md",
                "agents/AGENTS.md",
                "agents/SSOT.md",
                ".mcp/AGENTS.md",
                "CHANGELOG.md",
                "PLANS.md",
            ]

        findings: Dict[str, Dict[str, Any]] = {}
        drift: List[str] = []

        def record(key: str, *, ok: bool, details: str, data: Dict[str, Any] | None = None) -> None:
            findings[key] = {
                "ok": ok,
                "details": details,
            }
            if data:
                findings[key]["data"] = data
            if not ok:
                drift.append(key)

        repo_root = Path.cwd()

        # AGENTS cascade check
        agents_targets = [repo_root / rel for rel in ["AGENTS.md", "agents/AGENTS.md"]]
        missing_agents = [str(p.relative_to(repo_root)) for p in agents_targets if not p.exists()]
        missing_mentions = []
        for path in agents_targets:
            if not path.exists():
                continue
            text = _read_text(path)
            if "GovernanceSAG" not in text:
                missing_mentions.append(str(path.relative_to(repo_root)))
        if missing_agents or missing_mentions:
            details = []
            if missing_agents:
                details.append(f"missing files: {', '.join(missing_agents)}")
            if missing_mentions:
                details.append(f"missing GovernanceSAG mention: {', '.join(missing_mentions)}")
            record("agents_cascade", ok=False, details="; ".join(details) or "AGENTS cascade incomplete")
        else:
            record("agents_cascade", ok=True, details="AGENTS cascade references GovernanceSAG")

        # SSOT alignment
        ssot_files = [repo_root / rel for rel in ["SSOT.md", "agents/SSOT.md", ".mcp/SSOT.md"]]
        missing_ssot = [str(p.relative_to(repo_root)) for p in ssot_files if not p.exists()]
        stale_ssot = [
            str(p.relative_to(repo_root))
            for p in ssot_files
            if p.exists() and not _modified_within(p, window)
        ]
        missing_mentions = []
        for path in ssot_files:
            if not path.exists():
                continue
            if "GovernanceSAG" not in _read_text(path):
                missing_mentions.append(str(path.relative_to(repo_root)))
        if missing_ssot or stale_ssot or missing_mentions:
            parts: List[str] = []
            if missing_ssot:
                parts.append(f"missing files: {', '.join(missing_ssot)}")
            if stale_ssot:
                parts.append(f"stale (> {window.days}d): {', '.join(stale_ssot)}")
            if missing_mentions:
                parts.append(f"missing GovernanceSAG mention: {', '.join(missing_mentions)}")
            record("ssot_alignment", ok=False, details="; ".join(parts) or "SSOT misaligned")
        else:
            record("ssot_alignment", ok=True, details="SSOT artefacts mention GovernanceSAG within recency window")

        # CHANGELOG compliance
        changelog_path = repo_root / "CHANGELOG.md"
        changelog_text = _read_text(changelog_path)
        changelog_ok = bool(changelog_text and "Unreleased" in changelog_text)
        if not changelog_ok:
            reason = "missing" if not changelog_text else "missing 'Unreleased' heading"
            record("changelog_compliance", ok=False, details=f"CHANGELOG.md {reason}")
        else:
            record("changelog_compliance", ok=True, details="CHANGELOG.md contains Unreleased section")

        # ExecPlan hygiene
        plans_path = repo_root / "PLANS.md"
        plans_text = _read_text(plans_path)
        missing_sections = [section for section in PLAN_SECTIONS if section not in plans_text]
        plans_recent = plans_path.exists() and _modified_within(plans_path, timedelta(days=1))
        if not plans_path.exists():
            record("execplan", ok=False, details="PLANS.md missing")
        elif missing_sections or not plans_recent:
            issues = []
            if missing_sections:
                issues.append(f"missing sections: {', '.join(missing_sections)}")
            if not plans_recent:
                issues.append("last update > 1 day")
            record("execplan", ok=False, details="; ".join(issues))
        else:
            record("execplan", ok=True, details="PLANS.md includes required sections with recent updates")

        # Telemetry capture expectation
        telemetry_root = output_path
        telemetry_ok = telemetry_root.exists()
        if telemetry_ok:
            record("telemetry_capture", ok=True, details="Telemetry directory present", data={"path": str(telemetry_root)})
        else:
            record("telemetry_capture", ok=False, details=f"Telemetry path missing: {telemetry_root}")

        # Custom sources reporting
        records: List[Dict[str, Any]] = []
        for rel in sources:
            path = repo_root / rel
            exists = path.exists()
            recent = exists and _modified_within(path, window)
            records.append(
                {
                    "path": rel,
                    "exists": exists,
                    "recent": recent,
                }
            )

        status = "audited" if not drift else "drift-detected"
        payload = {
            "agent": "governance-sag",
            "run_id": run_id,
            "status": status,
            "timestamp": self.clock.now(UTC).isoformat(),
            "drift": drift,
            "findings": findings,
            "sources": records,
            "checks": list(config.get("checks") or []),
        }

        report_path = output_path / "governance_report.json"
        report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

        return payload

    __call__ = run
