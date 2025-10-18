Source: https://github.com/oraios/serena (last synced: 2025-10-18)
Source: https://github.com/mcp/oraios/serena (last synced: 2025-10-18)

# Serena MCP Server

## Overview
- Open-source semantic coding toolkit that exposes IDE-grade retrieval and editing tools over the Model Context Protocol so clients like Codex, Claude Code, Cursor, and other IDE extensions can manipulate large codebases efficiently.
- Ships as a Python CLI managed by `uv`/`uvx`; the shared configuration launches Serena as a stdio MCP server so downstream agents inherit a consistent command surface.
- Supports multiple contexts and modes to tune tool availability (e.g., `ide-assistant`, `codex`, `desktop-app`) and optional web dashboards that surface logs and shutdown controls.

## Setup Options
- **uvx stdio (default):** `uvx --from git+https://github.com/oraios/serena serena start-mcp-server --context <context> --project <path>` matches Codex and Cursor guidance; stdio keeps lifecycle tied to the MCP client process.
- **Streamable HTTP:** Add `--transport streamable-http --port <port>` when you need to host the server separately and point clients at `http://localhost:<port>/mcp`.
- **Docker:** Run `docker run --rm -i --network host -v /abs/projects:/workspaces/projects ghcr.io/oraios/serena:latest serena start-mcp-server --transport stdio` for sandboxed shells and pre-bundled language servers.
- **Indexing:** Speed warm up by running `uvx --from git+https://github.com/oraios/serena serena project index` inside each repository; Serena caches symbol data under `~/.serena`.

## Environment & Configuration
- `.mcp/.mcp-config.yaml` registers Serena under `servers.serena` with stdio transport; the command reads `SERENA_CONTEXT` (default `ide-assistant`) and `SERENA_PROJECT_ROOT` from `.mcp/.env.mcp`.
- Align `SERENA_PROJECT_ROOT` with other workspace-scoped servers (e.g., `MCP_FILESYSTEM_ROOT`, `MCP_GIT_REPOSITORY`) so tooling launches against the same absolute project directory.
- Projects can also be activated interactively (“Activate the project /abs/path/to/repo”)—Serena persists per-project settings under `.serena/project.yml`.
- Optional flags include `--mode <name>` for behaviour presets, `--enable-web-dashboard` to expose the GUI, and `--tool-timeout` to tune tool execution upper bounds.
- When integrating with Codex, pin `--context codex`; for Cursor, Claude Code, Windsurf, Cline, Roo Code, etc., stick with `ide-assistant` so default tool policies match IDE expectations.

## Operations & Validation
- Smoke test the install with `uvx --from git+https://github.com/oraios/serena serena --help` to confirm CLI entry points before wiring into automation.
- Start the stdio server via the shared config and ensure the MCP client can reach Serena’s tools (e.g., invoke `find_symbol`, `insert_after_symbol`, `switch_modes`).
- Capture dashboard logs in PLANS.md when debugging; they live under `~/.serena/logs/mcp-*`.
- Coordinate MCPSAG updates so `.mcp/.env.mcp.example`, `.mcp/AGENTS.md`, and `agents/SSOT.md` stay aligned with context/mode defaults and project activation steps.

## Update Log
- 2025-10-18: Initial capture after onboarding Serena into the shared MCP configuration (stdio launch, env variables, validation workflow).
