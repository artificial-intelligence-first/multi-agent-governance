# Model Context Protocol Reference Servers

- `overview.md` — summary of the official `modelcontextprotocol/servers` repository and shared installation requirements.
- `everything/overview.md` — prompts/resources/tools reference implementation for client testing.
- `fetch/overview.md` — web fetching server (`uvx mcp-server-fetch`) with robots.txt handling.
- `filesystem/overview.md` — secure file operations; requires `MCP_FILESYSTEM_ROOT` to scope access.
- `git/overview.md` — repository automation tools driven via `mcp-server-git`.
- `memory/overview.md` — knowledge graph memory server for persistent context.
- `sequentialthinking/overview.md` — dynamic thought sequencing utilities.
- `time/overview.md` — timezone conversion utilities exposed through `mcp-server-time`.

Keep these notes aligned with `.mcp/.mcp-config.yaml`, `.mcp/.env.mcp.example`, and MCPSAG guidance when enabling or retiring servers. Update `last synced` timestamps on each overview after reviewing upstream changes.
