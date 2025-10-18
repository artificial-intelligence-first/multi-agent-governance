from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parents[3] / "agents" / "sub-agents" / "governance-sag" / "src"))

from flow_runner.tasks.workflow_mag import governance_stage


def test_governance_stage_generates_audit(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "agents").mkdir()
    (tmp_path / ".mcp").mkdir()

    (tmp_path / "AGENTS.md").write_text("GovernanceSAG", encoding="utf-8")
    (tmp_path / "agents" / "AGENTS.md").write_text("GovernanceSAG", encoding="utf-8")
    (tmp_path / "SSOT.md").write_text("GovernanceSAG", encoding="utf-8")
    (tmp_path / "agents" / "SSOT.md").write_text("GovernanceSAG", encoding="utf-8")
    (tmp_path / ".mcp" / "AGENTS.md").write_text("GovernanceSAG", encoding="utf-8")
    (tmp_path / ".mcp" / "SSOT.md").write_text("GovernanceSAG", encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text("## [Unreleased]", encoding="utf-8")
    (tmp_path / "PLANS.md").write_text(
        "\n".join(
            [
                "# Plan",
                "## Big Picture",
                "## To-do",
                "## Progress",
                "## Decision Log",
                "## Surprises",
            ]
        ),
        encoding="utf-8",
    )

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "task": {"name": "workflow-mag-governance"},
                "paths": {
                    "output_dir": str(tmp_path / "runs/${RUN_ID}"),
                    "logs_dir": str(tmp_path / "logs/${RUN_ID}"),
                },
                "governance": {
                    "checks": ["AGENTS cascade alignment", "SSOT propagation"],
                    "sources": ["AGENTS.md", "SSOT.md"],
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("MAG_RUN_ID", "governance-test")
    artifact_path = governance_stage.execute(str(config_path))

    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == "governance-test"
    assert payload["status"] == "audited"
    assert payload["drift"] == []

    summary_path = artifact_path.parents[1] / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["artifacts"]["governance_report"] == str(artifact_path.resolve())
    step_log = artifact_path.parents[1] / "steps" / "GovernanceSAG.json"
    assert step_log.exists()
