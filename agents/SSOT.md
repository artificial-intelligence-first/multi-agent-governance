# SSOT — /agents

## Canonical References
- Repository baseline: /SSOT.md (root).
- Docs guidance: docs/SSOT.md.

## Notes
- Use this directory to capture agent-wide terminology, contracts, and governance details that extend the repository SSOT (`/SSOT.md`).
- When policies change, update this file together with /SSOT.md to keep agents aligned.
- MCP routing changes must flow through `.mcp/.mcp-config.yaml`; document any new providers or keys referenced by agents here and in `.mcp/AGENTS.md`.
- GitHub MCP server support requires `GITHUB_TOKEN` credentials; record scope/rotation details (REST + GraphQL) when agents start consuming GitHub data.
- MCPSAG (agents/sub-agents/mcp-sag) owns the MCP change checklist and validation SOP—loop it in before altering provider dependencies or SDK versions.
