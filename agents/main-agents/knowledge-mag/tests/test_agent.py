import asyncio
import sys
from pathlib import Path

AGENT_SRC = Path(__file__).resolve().parents[2] / "src"
if str(AGENT_SRC) not in sys.path:
    sys.path.insert(0, str(AGENT_SRC))

from knowledge_mag.agent import KnowledgeMag


def _build_sample_request() -> dict:
    return {
        "id": "knowledge-001",
        "version": "1.0",
        "knowledge_domain": "operations",
        "title": "Knowledge Base: Multi Agent Governance Operations",
        "summary": "Curated knowledge covering incident response, SOP governance, and release cadence.",
        "audience": ["Ops on-call", "Program managers"],
        "tags": ["operations", "governance"],
        "topics": [
            {
                "name": "Incident Response Playbook",
                "intents": [
                "Summarise detection signals for WorkFlowMAG and KnowledgeMag",
                    "Outline stabilization steps and escalation paths",
                ],
                "dependencies": ["On-call staffing model"],
            },
            {
                "name": "Knowledge Refresh Cadence",
                "intents": [
                    "Define quarterly review checkpoints",
                    "Record owners for SSOT updates",
                ],
                "gaps": ["Need confirmed reviewer list from Ops PM"],
            },
            {
                "name": "On-call staffing model",
                "intents": [
                    "List primary and backup rotations",
                    "Link to pager escalation chart",
                ],
            },
        ],
        "sources": [
            {
                "id": "KB-OPS-001",
                "title": "WorkFlowMAG Runbook",
                "uri": "https://kb.multi-agent-governance.example.com/workflow-mag/runbook",
                "type": "runbook",
                "last_reviewed": "2025-09-30",
            },
            {
                "id": "KB-OPS-002",
                "title": "Ops Staffing Model",
                "uri": "https://kb.multi-agent-governance.example.com/ops/staffing",
                "type": "policy",
            },
        ],
        "outstanding_questions": ["Provide forecast for next SSOT delta review."],
    }


def test_knowledge_mag_compiles_cards_and_sources():
    agent = KnowledgeMag()
    payload = _build_sample_request()

    result = asyncio.run(agent.run(request=payload))

    assert result["id"] == payload["id"]
    assert result["knowledge_domain"] == payload["knowledge_domain"]
    assert len(result["knowledge_cards"]) == len(payload["topics"])
    assert result["knowledge_cards"][0]["topic"] == payload["topics"][0]["name"]
    assert result["source_index"][0]["id"] == payload["sources"][0]["id"]
    assert result["diagnostics"]["metrics"]["knowledge.topic_count"] == len(payload["topics"])


def test_knowledge_mag_flags_gaps_and_missing_metadata():
    agent = KnowledgeMag()
    payload = _build_sample_request()
    payload["sources"][1]["last_reviewed"] = ""

    result = asyncio.run(agent.run(request=payload))

    assert any("last_reviewed" in note for note in result["review_notes"])
    assert result["follow_up_questions"], "Expect follow-up questions when outstanding items exist"
