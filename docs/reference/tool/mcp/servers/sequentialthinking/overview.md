Source: https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking (last synced: 2025-10-18)

# Sequential Thinking MCP Server

## Overview
- Node-based server that structures reasoning into sequential “thoughts,” supporting revisions, branching, and progress tracking.
- Useful for agents requiring explicit planning or reflective problem-solving workflows.

## Launch Commands
- Stdio (npx): `npx -y @modelcontextprotocol/server-sequential-thinking`
- Docker: `docker run --rm -i mcp/sequentialthinking`

## Tool
- `sequential_thinking`
  - Inputs include `thought`, `nextThoughtNeeded`, `thoughtNumber`, `totalThoughts`, plus optional revision/branch metadata.
  - Encourages agents to iterate, branch, and revisit steps when solving complex tasks.

## Configuration Notes
- Optional env: `DISABLE_THOUGHT_LOGGING=true` to stop writing transcript logs to stdout/stderr.
- Ensure `node`/`npx` are available.

## Validation
- `npx -y @modelcontextprotocol/server-sequential-thinking --help`
- Trigger the tool via MCP client to confirm iterative responses and optional branching metadata.

## Update Log
- 2025-10-18: Added sequential thinking server with stdio launch guidance; logging toggle documented via environment variable.
