Source: https://github.com/modelcontextprotocol/servers/tree/main/src/everything (last synced: 2025-10-18)

# Everything MCP Server

## Overview
- Reference/test server covering the full MCP surface area (prompts, resources, tools, sampling, notifications, roots, annotations, images).
- Ideal for validating client support and regression testing routers before deploying new capabilities.
- Ships as a Node package with the binary `mcp-server-everything`.

## Launch Commands
- Stdio (default): `npx -y @modelcontextprotocol/server-everything`
- Explicit transports: `npx -y @modelcontextprotocol/server-everything stdio|sse|streamableHttp`
- Docker alternative: `docker run -i --rm mcp/everything`

## Capabilities
- Tools: `echo`, `add`, `longRunningOperation`, `printEnv`, `sampleLLM`, `getTinyImage`, `annotatedMessage`, `getResourceReference`, `startElicitation`, `structuredContent`, `listRoots`.
- Resources: 100 synthetic test resources (plain text + binary) with pagination and live updates.
- Prompts: simple/complex/resource-driven interactions demonstrating arguments and resource embedding.
- Roots: exercises `roots/list` and `roots/list_changed`.
- Logging: emits periodic log messages at varying levels for telemetry checks.

## Configuration Notes
- Requires `node` and `npx` on the PATH.
- No env vars are mandatory; specify optional dashboard/transport flags on the CLI if needed.
- Works well alongside other reference servers for client conformance suites.

## Validation
- `npx -y @modelcontextprotocol/server-everything --help` confirms package resolution without starting the server.
- Run under `mcp` router in stdio mode to ensure the configuration loads (add to `.mcp/.mcp-config.yaml` as `servers.everything`).

## Update Log
- 2025-10-18: Added to shared MCP configuration with stdio launch instructions.
