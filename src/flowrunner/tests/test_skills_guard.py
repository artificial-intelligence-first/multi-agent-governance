from __future__ import annotations

import stat
import json
from pathlib import Path

import pytest

from flow_runner.skills_guard import SkillExecutionError, SkillExecutionGuard


def _make_script(root: Path, rel_path: str, body: str) -> Path:
    script_path = (root / rel_path)
    script_path.parent.mkdir(parents=True, exist_ok=True)
    script_path.write_text(body, encoding="utf-8")
    script_path.chmod(script_path.stat().st_mode | stat.S_IEXEC)
    return script_path


def _hash_file(path: Path) -> str:
    import hashlib

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_allowlist(root: Path, lines: list[str]) -> Path:
    allowlist = root / "skills/ALLOWLIST.txt"
    allowlist.parent.mkdir(parents=True, exist_ok=True)
    allowlist.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return allowlist


def test_execute_blocked_when_feature_flag_disabled(tmp_path: Path) -> None:
    script = _make_script(tmp_path, "skills/demo/scripts/run.sh", "#!/usr/bin/env bash\necho blocked" )
    sha = _hash_file(script)
    _write_allowlist(tmp_path, [f"skills/demo/scripts/run.sh {sha} .*"])
    telemetry = tmp_path / "telemetry/skills/events.jsonl"
    guard = SkillExecutionGuard(
        root=tmp_path,
        exec_enabled=False,
        allowlist_path=tmp_path / "skills/ALLOWLIST.txt",
        telemetry_path=telemetry,
    )
    with pytest.raises(SkillExecutionError) as exc_info:
        guard.execute(
            skill_name="demo",
            script_path="skills/demo/scripts/run.sh",
            args=[],
            allow_exec=True,
            workspace_dir=tmp_path,
        )
    assert exc_info.value.status == "blocked"
    assert exc_info.value.reason == "skills_exec_disabled"
    assert telemetry.exists()
    events = telemetry.read_text(encoding="utf-8").strip().splitlines()
    decoded = [json.loads(event) for event in events if event.strip()]
    assert decoded[-1]["event"] == "skill_exec_result"


def test_execute_succeeds_with_allowlist(tmp_path: Path) -> None:
    script = _make_script(
        tmp_path,
        "skills/demo/scripts/run.sh",
        "#!/usr/bin/env bash\necho success",
    )
    sha = _hash_file(script)
    _write_allowlist(tmp_path, [f"skills/demo/scripts/run.sh {sha} ^$"])
    telemetry = tmp_path / "telemetry/skills/events.jsonl"
    guard = SkillExecutionGuard(
        root=tmp_path,
        exec_enabled=True,
        allowlist_path=tmp_path / "skills/ALLOWLIST.txt",
        telemetry_path=telemetry,
    )
    result = guard.execute(
        skill_name="demo",
        script_path="skills/demo/scripts/run.sh",
        args=[],
        allow_exec=True,
        workspace_dir=tmp_path,
    )
    assert result["returncode"] == 0
    assert "success" in result["stdout"]
    events = telemetry.read_text(encoding="utf-8").strip().splitlines()
    names = [json.loads(event)["event"] for event in events if event.strip()]
    assert names.count("skill_exec_attempt") == 1
    assert names.count("skill_exec_result") == 1


def test_execute_blocks_on_hash_mismatch(tmp_path: Path) -> None:
    script = _make_script(
        tmp_path,
        "skills/demo/scripts/run.sh",
        "#!/usr/bin/env bash\necho mismatch",
    )
    wrong_sha = "0" * 64
    _write_allowlist(tmp_path, [f"skills/demo/scripts/run.sh {wrong_sha} .*"])
    guard = SkillExecutionGuard(
        root=tmp_path,
        exec_enabled=True,
        allowlist_path=tmp_path / "skills/ALLOWLIST.txt",
        telemetry_path=tmp_path / "telemetry/skills/events.jsonl",
    )
    with pytest.raises(SkillExecutionError) as exc_info:
        guard.execute(
            skill_name="demo",
            script_path="skills/demo/scripts/run.sh",
            args=[],
            allow_exec=True,
            workspace_dir=tmp_path,
        )
    assert exc_info.value.status == "blocked"
    assert exc_info.value.reason == "hash_mismatch"


def test_execute_blocks_when_script_missing(tmp_path: Path) -> None:
    missing_path = "skills/demo/scripts/missing.sh"
    _write_allowlist(tmp_path, [f"{missing_path} {'0'*64} .*"])
    telemetry = tmp_path / "telemetry/skills/events.jsonl"
    guard = SkillExecutionGuard(
        root=tmp_path,
        exec_enabled=True,
        allowlist_path=tmp_path / "skills/ALLOWLIST.txt",
        telemetry_path=telemetry,
    )
    with pytest.raises(SkillExecutionError) as exc_info:
        guard.execute(
            skill_name="demo",
            script_path=missing_path,
            args=[],
            allow_exec=True,
            workspace_dir=tmp_path,
        )
    assert exc_info.value.status == "blocked"
    assert exc_info.value.reason == "script_not_found"
    events = telemetry.read_text(encoding="utf-8").strip().splitlines()
    decoded = [json.loads(event) for event in events if event.strip()]
    assert decoded[-1]["event"] == "skill_exec_result"
    assert decoded[-1]["data"]["reason"] == "script_not_found"


def test_execute_blocks_when_permission_denied(tmp_path: Path) -> None:
    script = _make_script(
        tmp_path,
        "skills/demo/scripts/run.sh",
        "#!/usr/bin/env bash\necho should_not_run",
    )
    script.chmod(script.stat().st_mode & ~stat.S_IEXEC)
    sha = _hash_file(script)
    _write_allowlist(tmp_path, [f"skills/demo/scripts/run.sh {sha} .*"])
    telemetry = tmp_path / "telemetry/skills/events.jsonl"
    guard = SkillExecutionGuard(
        root=tmp_path,
        exec_enabled=True,
        allowlist_path=tmp_path / "skills/ALLOWLIST.txt",
        telemetry_path=telemetry,
    )
    with pytest.raises(SkillExecutionError) as exc_info:
        guard.execute(
            skill_name="demo",
            script_path="skills/demo/scripts/run.sh",
            args=[],
            allow_exec=True,
            workspace_dir=tmp_path,
        )
    assert exc_info.value.status == "blocked"
    assert exc_info.value.reason == "permission_denied"
    events = telemetry.read_text(encoding="utf-8").strip().splitlines()
    decoded = [json.loads(event) for event in events if event.strip()]
    assert decoded[-1]["event"] == "skill_exec_result"
    assert decoded[-1]["data"]["reason"] == "permission_denied"
