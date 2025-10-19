from __future__ import annotations

import json
from pathlib import Path

from mcp_router.providers.dummy_provider import DummyProvider
from mcp_router.router import MCPRouter
from mcp_router.skills import SkillManager


def _write_skill(root: Path, *, enabled: bool = True) -> Path:
    skills_dir = root / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)
    registry = {
        "skills": [
            {
                "name": "sample-skill",
                "path": "skills/sample-skill/SKILL.md",
                "owner": "TestOwner",
                "tags": ["sample", "api"],
                "enabled": enabled,
                "allow_exec": False,
                "sha256": None,
                "notes": "",
            }
        ]
    }
    (skills_dir / "registry.json").write_text(json.dumps(registry, indent=2), encoding="utf-8")
    allowlist = skills_dir / "ALLOWLIST.txt"
    if not allowlist.exists():
        allowlist.write_text("# Skills execution allowlist\n", encoding="utf-8")

    skill_path = skills_dir / "sample-skill"
    skill_path.mkdir(exist_ok=True)
    body = """
---
name: sample-skill
description: >
  Use for api discovery and sample flows where governance applies.
---

# Sample Skill

Guidance for API design tasks.
"""
    (skill_path / "SKILL.md").write_text(body.strip() + "\n", encoding="utf-8")
    return skill_path / "SKILL.md"


def test_skill_manager_prepare_payload_logs_telemetry(tmp_path: Path) -> None:
    _write_skill(tmp_path)
    manager = SkillManager(root=tmp_path, feature_flags={"skills_v1": True})
    payload = manager.prepare_payload("Need API governance guidance")
    assert payload, "expected at least one skill match"
    event_path = tmp_path / "telemetry/skills/events.jsonl"
    assert event_path.exists()
    events = [json.loads(line) for line in event_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    event_names = {entry["event"] for entry in events}
    assert "skill_selected" in event_names
    assert "skill_loaded" in event_names
    match = payload[0]
    assert match["name"] == "sample-skill"
    assert match["truncated"] is False


def test_router_injects_skill_config(tmp_path: Path) -> None:
    _write_skill(tmp_path)
    manager = SkillManager(root=tmp_path, feature_flags={"skills_v1": True})
    log_dir = tmp_path / "logs"
    provider = DummyProvider()
    router = MCPRouter(provider, max_sessions=1, log_dir=log_dir, skills=manager)
    with router:
        result = router.generate(
            prompt="Please help with API governance",
            model="test-model",
            prompt_limit=8096,
            prompt_buffer=256,
            sandbox="read-only",
            approval_policy="never",
        )
    skills_meta = result.meta.get("config", {}).get("skills")
    assert skills_meta, "expected skills config in provider metadata"
    assert skills_meta["matches"][0]["name"] == "sample-skill"
    audit_log = log_dir / "mcp_calls.jsonl"
    assert audit_log.exists()


def test_skill_manager_normalizes_feature_flag_strings(tmp_path: Path) -> None:
    manager = SkillManager(
        root=tmp_path,
        feature_flags={"skills_v1": "false", "skills_exec": "true"},
    )
    assert manager.enabled is False
    assert manager.exec_enabled is True
    assert manager.list_enabled() == []


def test_router_skips_skills_manager_when_flag_false(tmp_path: Path) -> None:
    settings = {"features": {"skills_v1": "false"}}
    manager = MCPRouter._build_skills_manager(settings)
    assert manager is None


def test_router_builds_skills_manager_when_flag_true(tmp_path: Path) -> None:
    settings = {"features": {"skills_v1": "true"}}
    manager = MCPRouter._build_skills_manager(settings)
    assert isinstance(manager, SkillManager)
    assert manager.enabled is True
