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
- Chrome DevTools MCP server support runs under `servers.chrome-devtools` via `npx -y chrome-devtools-mcp@latest`; note which hosts have Node.js 20.19+, npm, and Chrome installed, and whether `--headless`, `--browserUrl`, or custom `--executablePath` flags are required for automation.
- MarkItDown MCP server support runs under `servers.markitdown` via `uvx markitdown-mcp`; ensure Python 3.10+ plus required extras (`markitdown[pdf]`, etc.) are installed on BrowserSAG hosts, and document any Docker usage for remote conversions.
- Playwright MCP server support runs under `servers.playwright` via `npx @playwright/mcp@latest`; record default flags (`--headless`, `--browser`, trace/video capture) and note where browser binaries are cached.
- BrowserSAG (`agents/sub-agents/browser-sag/`) operates the Chrome DevTools MCP workflows. Record prompt names, telemetry paths, and SOP revisions whenever browser automation capabilities change.
- Reference MCP servers from `modelcontextprotocol/servers` expose Everything/Fetch/Filesystem/Git/Memory/Sequential Thinking/Time; require `npx`/`uvx` on PATH and absolute paths via `MCP_FILESYSTEM_ROOT` / `MCP_GIT_REPOSITORY` when enabling filesystem or Git mutations.
- MCPSAG (agents/sub-agents/mcp-sag) owns the MCP change checklist and validation SOP—loop it in before altering provider dependencies or SDK versions.
- GovernanceSAG (agents/sub-agents/governance-sag) audits AGENTS/SSOT/CHANGELOG/PLANS artefacts; involve it whenever governance SOPs or terminology shift.
