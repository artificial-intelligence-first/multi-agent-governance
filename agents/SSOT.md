# SSOT — /agents

## Canonical References
- Repository baseline: /SSOT.md (root).
- Docs guidance: docs/SSOT.md.

## Notes
- Use this directory to capture agent-wide terminology, contracts, and governance details that extend the repository SSOT (`/SSOT.md`).
- When policies change, update this file together with /SSOT.md to keep agents aligned.
- MCP routing changes must flow through `.mcp/.mcp-config.yaml`; document any new providers or keys referenced by agents here and in `.mcp/AGENTS.md`.
- GitHub MCP server support requires `GITHUB_TOKEN` credentials; record scope/rotation details (REST + GraphQL) when agents start consuming GitHub data.
- Context7 MCP server support requires `CONTEXT7_MCP_URL`/`CONTEXT7_API_KEY` (HTTPS endpoint + API key) and optional `CONTEXT7_API_URL` for REST fallbacks; capture rotation cadence and access levels alongside GitHub notes.
- Serena MCP server support runs via `uvx --from git+https://github.com/oraios/serena serena start-mcp-server`; align `SERENA_CONTEXT` and `SERENA_PROJECT_ROOT` with each agent’s workspace assumptions and log which projects are pre-indexed.
- Reference MCP servers from `modelcontextprotocol/servers` expose Everything/Fetch/Filesystem/Git/Memory/Sequential Thinking/Time; require `npx`/`uvx` on PATH and absolute paths via `MCP_FILESYSTEM_ROOT` / `MCP_GIT_REPOSITORY` when enabling filesystem or Git mutations.
- MCPSAG (agents/sub-agents/mcp-sag) owns the MCP change checklist and validation SOP—loop it in before altering provider dependencies or SDK versions.
