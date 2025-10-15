import asyncio
import sys
from pathlib import Path

AGENT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(AGENT_SRC) not in sys.path:
    sys.path.insert(0, str(AGENT_SRC))

from docs_sag.agent import DocsSAG


def _build_sample_request() -> dict:
    return {
        "id": "docs-001",
        "version": "1.0",
        "doc_type": "overview",
        "title": "DocsSAG Draft Overview",
        "summary": "Capture the purpose, scope, and workflow for the DocsSAG documentation sub-agent.",
        "audience": "Docs platform engineers",
        "style_tone": "Concise, operational English",
        "sections": [
            {
                "heading": "Purpose",
                "knowledge_refs": ["Incident Response Playbook"],
                "key_points": [
                    "Document automation-first workflows",
                    "Centralise editorial guardrails",
                ],
                "details": "DocsSAG delivers publication-ready drafts derived from knowledge packets.",
            },
            {
                "heading": "Workflow",
                "knowledge_refs": ["Knowledge Refresh Cadence"],
                "key_points": [
                    "Validate payload against docs_sag_request schema",
                    "Generate markdown with actionable sections",
                    "Emit diagnostics metrics for observability",
                ],
                "status": "stable",
            },
            {
                "heading": "Open Questions",
                "knowledge_refs": ["Knowledge Refresh Cadence"],
                "details": "Need confirmation on integration timelines and release notes coverage.",
            },
        ],
        "constraints": ["Adhere to SSOT terminology", "Avoid speculative commitments"],
        "references": ["https://docs.multi-agent-system.example.com"],
    }


def test_docs_sag_generates_markdown_document():
    agent = DocsSAG()
    payload = _build_sample_request()

    result = asyncio.run(agent.run(request=payload))

    assert result["id"] == payload["id"]
    assert result["doc_type"] == payload["doc_type"]
    assert result["document_markdown"].startswith(f"# {payload['title']}")
    assert len(result["sections"]) == len(payload["sections"])
    assert result["review_notes"], "Expect review notes to surface missing details"
    assert result["diagnostics"]["metrics"]["docs_sag.section_count"] == len(payload["sections"])
    assert result["sections"][0]["knowledge_refs"]
    generated_path = AGENT_SRC.parents[3] / result["diagnostics"]["generated_document_path"]
    assert generated_path.exists(), "Generated Markdown file should be persisted under /docs"
    generated_path.unlink()


def test_docs_sag_handles_missing_details_with_followups():
    agent = DocsSAG()
    payload = _build_sample_request()
    payload["sections"][0]["details"] = ""
    payload["sections"][1]["key_points"] = []

    result = asyncio.run(agent.run(request=payload))

    assert any("expand" in note.lower() for note in result["review_notes"])
    assert result["follow_up_questions"], "Follow-up questions should be generated for incomplete sections"
    generated_path = AGENT_SRC.parents[3] / result["diagnostics"]["generated_document_path"]
    assert generated_path.exists(), "Generated Markdown file should be persisted under /docs"
    generated_path.unlink()
