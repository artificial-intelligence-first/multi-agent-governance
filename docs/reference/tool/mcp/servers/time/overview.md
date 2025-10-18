Source: https://github.com/modelcontextprotocol/servers/tree/main/src/time (last synced: 2025-10-18)

# Time MCP Server

## Overview
- Python server supplying timezone-aware utilities: `get_current_time` and `convert_time`.
- Uses IANA timezone names and detects the host timezone automatically; exposes consistent responses for scheduling workflows.

## Launch Commands
- Stdio (uvx): `uvx mcp-server-time`
- Pip module: `python -m mcp_server_time`
- Docker: `docker run -i --rm mcp/time`

## Tools
- `get_current_time(timezone)` – returns current time for the specified timezone (defaults to system timezone if omitted).
- `convert_time(source_timezone, time, target_timezone)` – converts HH:MM between IANA zones.

## Configuration Notes
- Optional env `LOCAL_TIMEZONE` overrides the system timezone detection (useful in containers).
- Requires Python 3.10+ (`uvx` handles virtualenv creation automatically).

## Validation
- `uvx mcp-server-time --help`
- Verify timezone conversion via MCP client (e.g., convert between `America/Los_Angeles` and `Asia/Tokyo`).

## Update Log
- 2025-10-18: Captured launch commands and optional timezone override when enabling the server in shared config.
