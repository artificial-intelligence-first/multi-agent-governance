# MCP Tooling Reference

- `overview.md` — protocol overview plus shared integration guidance for this repository.
- `github/overview.md` — configuration and usage details for GitHub’s MCP server implementation.
- `context7/overview.md` — setup, authentication, and governance notes for the Context7 MCP server.
- `serena/overview.md` — stdio launch guidance, context/mode defaults, and project activation tips for the Serena MCP server.
- `chrome-devtools/overview.md` — Chrome DevTools automation server requirements, launch flags, and validation workflows for browser debugging.
- `markitdown/overview.md` — Markdown conversion tooling for local/remote artefacts via MarkItDown MCP.
- `playwright/overview.md` — Playwright-based automation server covering accessibility-driven browser actions.
- `servers/overview.md` — reference implementations from `modelcontextprotocol/servers`, with per-server guides (Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time).
- `sdk/` — language-specific SDK notes (Python, TypeScript) covering installation, capabilities, and usage patterns.

Centralise documentation for `.mcp/.mcp-config.yaml`, `.mcp/.env.mcp`, and managed MCP servers in this folder. When introducing a new source, duplicate `docs/reference/reference-template.md`, cite upstream URLs with `last synced` dates, enumerate supported transports (REST, GraphQL, SSE, etc.), capture required environment variables, populate the Update Log, and keep content in English so downstream agents maintain consistent instructions across the fleet. Update relevant `AGENTS.md` files whenever MCP workflows or dependencies change.

MCPSAG (`agents/sub-agents/mcp-sag/`) maintains the MCP playbook and checklist. Coordinate with it before altering provider configuration, and ensure the resulting documentation cascade (`AGENTS.md`, `.mcp/AGENTS.md`, `SSOT.md`) remains in sync with this reference.
