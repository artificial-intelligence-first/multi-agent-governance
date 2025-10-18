import json
import os
from pathlib import Path

import sys

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from governance_sag import agent


def test_governance_sag_audit_creates_report(tmp_path, monkeypatch):
    repo_root = tmp_path
    monkeypatch.chdir(repo_root)

    (repo_root / "agents").mkdir()
    (repo_root / ".mcp").mkdir()
    telemetry_dir = repo_root / "telemetry" / "runs" / "test-run" / "governance"
    telemetry_dir.mkdir(parents=True)

    (repo_root / "AGENTS.md").write_text("# Root AGENTS\nGovernanceSAG", encoding="utf-8")
    (repo_root / "agents" / "AGENTS.md").write_text("# Agents\nGovernanceSAG", encoding="utf-8")
    (repo_root / "SSOT.md").write_text("GovernanceSAG", encoding="utf-8")
    (repo_root / "agents" / "SSOT.md").write_text("GovernanceSAG", encoding="utf-8")
    (repo_root / ".mcp" / "AGENTS.md").write_text("GovernanceSAG", encoding="utf-8")
    (repo_root / ".mcp" / "SSOT.md").write_text("GovernanceSAG", encoding="utf-8")
    (repo_root / "CHANGELOG.md").write_text("## [Unreleased]\n", encoding="utf-8")
    plans = repo_root / "PLANS.md"
    plans.write_text(
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

    gov = agent.GovernanceSAG()
    result = gov(run_id="test-run", output_dir=telemetry_dir)

    assert result["status"] == "audited"
    report_path = telemetry_dir / "governance_report.json"
    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == "test-run"
    assert payload["agent"] == "governance-sag"
    assert "findings" in payload
