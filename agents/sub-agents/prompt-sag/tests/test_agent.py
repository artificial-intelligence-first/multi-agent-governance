import asyncio
import sys
from pathlib import Path

AGENT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(AGENT_SRC) not in sys.path:
    sys.path.insert(0, str(AGENT_SRC))

from prompt_sag.agent import PromptSAG  # noqa: E402


def _build_sample_request() -> dict:
    return {
        "id": "prompt-001",
        "version": "1.0",
        "objective": "Create a prompt that updates README.md with new setup instructions.",
        "context": "Repository uses Python 3.13, pytest, and make validate.",
        "constraints": [
            "Avoid editing files outside README.md.",
            "Always run make validate before finalising.",
        ],
        "references": [
            "AGENTS.md",
            "docs/reference/engineering/prompt/OpenAI.md",
        ],
        "target_models": ["gpt-5-codex"],
        "evaluation": ["Run make validate", "Summarise file changes"],
    }


def test_prompt_sag_compiles_prompt_components(tmp_path: Path):
    agent = PromptSAG()
    payload = _build_sample_request()

    result = asyncio.run(agent.run(request=payload, output_path=tmp_path / "response.json"))

    assert result["id"] == payload["id"]
    assert len(result["prompt_components"]) == 2
    assert result["prompt_components"][0]["role"] == "system"
    assert "AGENTS.md" in result["prompt_components"][0]["content"]
    assert result["evaluation"] == payload["evaluation"]
    assert result["diagnostics"]["metrics"]["prompt_sag.prompt_count"] == 2

    stored = (tmp_path / "response.json").read_text(encoding="utf-8")
    assert payload["objective"] in stored


def test_prompt_sag_flags_missing_constraints():
    agent = PromptSAG()
    payload = _build_sample_request()
    payload["constraints"] = []
    payload["evaluation"] = []

    result = asyncio.run(agent.run(request=payload))

    assert any("restrictions" in question.lower() for question in result["follow_up_questions"])
    assert any("verification" in question.lower() for question in result["follow_up_questions"])
