Source: https://github.com/modelcontextprotocol/servers/tree/main/src/fetch (last synced: 2025-10-18)

# Fetch MCP Server

## Overview
- Python-based server exposing a `fetch` tool and prompt to retrieve web content and convert HTML to markdown.
- Supports chunked downloads via `start_index`, raw mode (`raw=true`), and optional robots.txt enforcement.
- Useful for knowledge retrieval tasks and verifying HTTP client behaviour in MCP-enabled agents.

## Launch Commands
- Stdio (uvx): `uvx mcp-server-fetch`
- Pip module: `python -m mcp_server_fetch`
- Docker: `docker run -i --rm mcp/fetch`

## Configuration Options
- Add `--ignore-robots-txt` in the command args to bypass robots.txt (defaults to obeying robots.txt for model-triggered calls).
- Override user-agent with `--user-agent <string>` if required.
- Works without extra environment variables; ensure outbound HTTP is permitted.

## Integration Notes
- Configure under `.mcp/.mcp-config.yaml` as `servers.fetch` with stdio transport.
- No write access is granted—safe for most environments.
- Compatible with Claude, Codex, Cursor, Flow Runner, and other MCP clients via stdio.

## Validation
- `uvx mcp-server-fetch --help` (package availability).
- Exercise tool via MCP client: call `fetch` with a known URL and check markdown output.

## Update Log
- 2025-10-18: Documented launch options and robots.txt handling when enabling the server in shared config.
