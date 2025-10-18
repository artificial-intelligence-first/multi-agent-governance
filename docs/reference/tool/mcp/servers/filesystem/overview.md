Source: https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem (last synced: 2025-10-18)

# Filesystem MCP Server

## Overview
- Node-based server offering secure file operations with configurable roots and support for the MCP roots protocol.
- Provides read/write/edit/search capabilities, directory listings, size summaries, and metadata inspection.
- Ideal for IDE-style automations that require structured file manipulation within controlled directories.

## Launch Commands
- Stdio (npx): `npx -y @modelcontextprotocol/server-filesystem <allowed-path>`
- Multiple roots: pass additional absolute paths as extra arguments (all must be absolute).
- Docker: `docker run --rm -i mcp/filesystem /projects` (mount directories via `--mount type=bind,...`).

## Required Environment
- `MCP_FILESYSTEM_ROOT` (absolute path) must be set in `.mcp/.env.mcp` to scope read/write operations when using the shared config.
- Optional: rely on MCP roots protocol if the client supports `roots/list` and `roots/list_changed`.
- Requires Node/npm; the official server is shipped on npm and invoked via `npx`.

## Tools
- `read_text_file`, `read_media_file`, `read_multiple_files`
- `write_file`, `edit_file`, `create_directory`, `move_file`
- `list_directory`, `list_directory_with_sizes`, `directory_tree`
- `get_file_info`, `search_files`, `list_allowed_directories`

## Governance Notes
- Treat the configured root as a mutable workspace; enable read-only mounts via Docker or OS permissions if required.
- Always document the chosen roots in PLANS.md / ExecPlans when expanding access.

## Validation
- Smoke test: `npx -y @modelcontextprotocol/server-filesystem /tmp` (Ctrl+C to stop).
- Dry-run `edit_file` or `list_directory` on a safe fixture directory before enabling for production repositories.

## Update Log
- 2025-10-18: Added with `MCP_FILESYSTEM_ROOT` guidance when onboarding reference servers.
