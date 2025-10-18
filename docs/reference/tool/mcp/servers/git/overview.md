Source: https://github.com/modelcontextprotocol/servers/tree/main/src/git (last synced: 2025-10-18)

# Git MCP Server

## Overview
- Python server providing Git status, diff, log, branch, add/commit/reset, and checkout operations to MCP clients.
- Designed for repository automation and agent workflows that need Git introspection or write access.

## Launch Commands
- Stdio (uvx): `uvx mcp-server-git --repository <abs-path>`
- Pip module: `python -m mcp_server_git --repository <abs-path>`
- Docker: `docker run --rm -i --mount type=bind,src=<abs-path>,dst=/workspace mcp/git`

## Environment & Inputs
- Set `MCP_GIT_REPOSITORY` (absolute path) in `.mcp/.env.mcp` for the shared configuration; defaults to `.` but an explicit path is recommended.
- Requires `git` installed and accessible to the server process.
- Accepts additional arguments such as `--max-diff-lines` via CLI when necessary.

## Notable Tools
- `git_status`, `git_diff_unstaged`, `git_diff_staged`, `git_diff`
- `git_add`, `git_reset`, `git_commit`
- `git_log` (supports relative dates), `git_show`, `git_branch`, `git_checkout`, `git_create_branch`

## Governance Notes
- Treat this server as write-capable: stage/commit, branch creation, and reset operations can mutate repository history.
- Provide guidance in ExecPlans when exposing repositories to automation and coordinate with Ops/QAMAG.

## Validation
- `uvx mcp-server-git --help`
- Run `git_status` and `git_diff_unstaged` against a safe test repository before enabling on production clones.

## Update Log
- 2025-10-18: Documented launch requirements and added to shared MCP config with `MCP_GIT_REPOSITORY` placeholder.
