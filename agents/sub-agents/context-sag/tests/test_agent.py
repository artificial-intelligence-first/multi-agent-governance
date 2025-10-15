import asyncio
import sys
from pathlib import Path

AGENT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(AGENT_SRC) not in sys.path:
    sys.path.insert(0, str(AGENT_SRC))

from context_sag.agent import ContextSAG  # noqa: E402


def _build_sample_request() -> dict:
    return {
        "id": "context-001",
        "version": "1.0",
        "objective": "Prepare a multi-document context bundle for incident response automation.",
        "primary_use_case": "WorkFlowMAG escalation workflow",
        "target_models": ["gpt-5-codex", "claude-3-opus"],
        "audience": ["Agents Ops", "Incident commanders"],
        "constraints": [
            "Exclude personally identifiable information.",
            "Highlight runbook steps before metrics.",
        ],
        "evaluation_checks": [
            "Replay incident LT-245 with new context bundle.",
            "Run hallucination regression prompts weekly.",
        ],
        "context_inputs": [
            {
                "name": "Incident Response Runbook",
                "type": "document",
                "summary": "Canonical incident mitigation playbook covering detection through recovery.",
                "importance": "critical",
                "source": "docs/reference/engineering/runbooks/incident-response.md",
                "last_updated": "2025-09-28",
                "tags": ["runbook", "operations"],
            },
            {
                "name": "Postmortem LT-199",
                "type": "knowledge_card",
                "summary": "Highlights communication gaps from previous outage.",
                "importance": "medium",
                "risks": ["stale insights"],
            },
            {
                "name": "PagerDuty Export",
                "type": "dataset",
                "summary": "Contains historical on-call schedules and escalations.",
                "importance": "low",
                "source": "s3://internal/oncall/export.csv",
                "tags": ["sensitive"],
            },
        ],
    }


def test_context_sag_prioritises_and_flags_risks(tmp_path: Path):
    agent = ContextSAG()
    payload = _build_sample_request()
    output_path = tmp_path / "response.json"

    result = asyncio.run(agent.run(request=payload, output_path=output_path))

    assert result["id"] == payload["id"]
    assert len(result["context_briefs"]) == len(payload["context_inputs"])
    assert result["context_briefs"][0]["name"] == "Incident Response Runbook"
    assert result["context_briefs"][-1]["inclusion"] == "defer"
    assert "risk_register" in result and result["risk_register"]
    assert result["diagnostics"]["metrics"]["context_sag.context_count"] == len(payload["context_inputs"])
    assert output_path.exists()


def test_context_sag_requests_followups_when_metadata_missing():
    agent = ContextSAG()
    payload = _build_sample_request()
    payload["constraints"] = []
    payload["evaluation_checks"] = []
    payload["context_inputs"][0]["source"] = ""
    payload["context_inputs"][0]["last_updated"] = ""

    result = asyncio.run(agent.run(request=payload))

    followups = result["follow_up_questions"]
    assert any("constraints" in question.lower() for question in followups)
    assert any("provenance" in question.lower() for question in followups)
