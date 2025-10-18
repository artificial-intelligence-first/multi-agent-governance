Source: https://github.com/modelcontextprotocol/servers (last synced: 2025-10-18)
Source: https://modelcontextprotocol.io/docs/quickstart (last synced: 2025-10-18)

# MCP Reference Servers Overview

## Summary
- Official repository of sample Model Context Protocol servers maintained by the MCP working group; demonstrates prompts, resources, tools, roots, and streaming transports across multiple runtimes.
- Provides ready-made binaries/packages for Node (`@modelcontextprotocol/*`) and Python (`mcp-server-*`) that we can run via stdio, SSE, or Streamable HTTP.
- Supports validation, onboarding, and feature coverage for MCP clients—ideal for regression testing Codex, Cursor, Flow Runner, and bespoke automations.

## Key Servers Enabled Here
- **Everything** – Full-feature test harness showcasing prompts, resources, sampling, notifications, and annotations.
- **Fetch** – Web retrieval pipeline returning markdown or raw HTML with optional robots.txt compliance.
- **Filesystem** – Read/write/create/search capabilities scoped to configured roots; supports MCP roots protocol.
- **Git** – Repository inspection and mutation tools (`status`, `diff`, `log`, `add`, `commit`, etc.) with branch management.
- **Memory** – Knowledge graph persistence for long-lived context.
- **Sequential Thinking** – Structured reasoning and branching thought sequences for complex problem solving.
- **Time** – Timezone-aware current time queries and conversions.

## Installation & Runtime Notes
- Node-based servers (`everything`, `filesystem`, `memory`, `sequentialthinking`) require `node`/`npm`/`npx` on `PATH`. We launch them with `npx -y @modelcontextprotocol/<package>`.
- Python-based servers (`fetch`, `git`, `time`) ship PyPI packages exposing `mcp-server-*` console scripts; we run them via `uvx` so dependencies stay isolated.
- Update `.mcp/.env.mcp` with:
  - `MCP_FILESYSTEM_ROOT` – absolute path(s) that the filesystem server should expose.
  - `MCP_GIT_REPOSITORY` – absolute repository root for Git operations.
  - Optional toggles: `DISABLE_THOUGHT_LOGGING=true` (sequential thinking), `LOCAL_TIMEZONE=<IANA name>` (time), custom fetch arguments (`--ignore-robots-txt`, `--user-agent <ua>`).
- Launch defaults live under `.mcp/.mcp-config.yaml` (`servers.*`) using stdio; adjust transports only after updating the documentation cascade and MCPSAG checklist.

## Validation
- Confirm tooling availability with `npx -y @modelcontextprotocol/server-everything --help`, `npx -y @modelcontextprotocol/server-filesystem /tmp` (Ctrl+C to exit), `uvx mcp-server-fetch --help`, and `uvx mcp-server-time --help`.
- Run `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"` after enabling servers to ensure the router loads the expanded configuration.
- For Filesystem/Git, run smoke tools (e.g., `read_text_file`, `git_status`) inside a controlled workspace before granting production access.

## Update Log
- 2025-10-18: Initial capture on enabling reference servers in `.mcp/.mcp-config.yaml`.
