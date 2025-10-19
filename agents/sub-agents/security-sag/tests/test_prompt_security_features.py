from pathlib import Path

import yaml


def test_security_prompt_references_github_docs() -> None:
    """Ensure the SecuritySAG prompt references GitHub security documentation."""
    prompt_path = (
        Path(__file__).resolve().parent.parent / "prompts" / "security_sag.prompt.yaml"
    )
    data = yaml.safe_load(prompt_path.read_text())

    refs = set(data.get("context", {}).get("references", []))
    expected = {
        "agents/sub-agents/security-sag/docs/overview.md",
        "docs/reference/tool/mcp/github/overview.md",
        "docs/reference/tool/mcp/github/security.md",
        "agents/sub-agents/security-sag/sop/README.md",
    }
    missing = expected.difference(refs)
    assert not missing, f"SecuritySAG prompt missing references: {sorted(missing)}"

    system_text = data.get("system", "")
    for keyword in [
        "secret scanning",
        "push protection",
        "prompt-injection",
        "audit",
        "authorization",
    ]:
        assert (
            keyword in system_text
        ), f"Security system prompt should mention '{keyword}' capability."
