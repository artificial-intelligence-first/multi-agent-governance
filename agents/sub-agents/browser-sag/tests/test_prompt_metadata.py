from pathlib import Path
import yaml


def test_prompt_references_browser_mcp_docs() -> None:
    """Ensure the baseline prompt references all browser MCP documentation."""
    prompt_path = Path(__file__).resolve().parent.parent / "prompts" / "browser-sag.prompt.yaml"
    data = yaml.safe_load(prompt_path.read_text())

    refs = data.get("context", {}).get("references", [])
    expected = {
        "docs/reference/tool/mcp/chrome-devtools/overview.md",
        "docs/reference/tool/mcp/playwright/overview.md",
        "docs/reference/tool/mcp/markitdown/overview.md",
    }
    assert expected.issubset(set(refs)), "Browser MCP references missing from prompt context."
