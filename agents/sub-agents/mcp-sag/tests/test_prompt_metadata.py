from pathlib import Path

import yaml


def test_mcp_sag_prompt_references_docs() -> None:
    """Ensure the MCPSAG prompt references the required documentation."""
    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "mcp_sag.prompt.yaml"
    data = yaml.safe_load(prompt_path.read_text())

    refs = set(data.get("context", {}).get("references", []))
    expected = {
        "agents/sub-agents/mcp-sag/docs/overview.md",
        "agents/sub-agents/mcp-sag/sop/README.md",
        "agents/sub-agents/mcp-sag/templates/mcp_change_checklist.md",
        ".mcp/AGENTS.md",
        ".mcp/SSOT.md",
    }
    missing = expected.difference(refs)
    assert not missing, f"MCPSAG prompt missing references: {sorted(missing)}"

    system_text = data.get("system", "")
    for keyword in ["MCP", "configuration", "validation", "documentation"]:
        assert (
            keyword.lower() in system_text.lower()
        ), f"System prompt should mention '{keyword}'."
