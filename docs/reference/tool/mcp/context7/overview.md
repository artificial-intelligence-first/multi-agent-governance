Source: https://context7.com (last synced: 2025-10-18)
Source: https://github.com/upstash/context7 (last synced: 2025-10-18)

# Context7 MCP Server

## Overview
- Upstash operates Context7 as a Model Context Protocol server that injects up-to-date, versioned documentation and real code examples into LLM prompts so editors like Cursor, Claude Code, and VS Code answer with current APIs instead of stale training data.
- Prompts can simply include `use context7` to signal the client to fetch Context7 snippets, reducing hallucinated endpoints and closing knowledge gaps for fast-moving ecosystems.
- The service maintains multi-language documentation packs and community contributions via the open-source (`@upstash/context7-mcp`) repository and the MCP registry entry published under `mcp/upstash/context7`.

## Setup Options
- **Remote HTTP:** Point MCP clients at `https://mcp.context7.com/mcp`; most editors allow adding the server under `context7` with optional headers.
- **Local stdio:** Run `npx -y @upstash/context7-mcp --api-key <CONTEXT7_API_KEY>` (Node.js ≥ 18) to spawn a local transport if remote connectivity is restricted.
- **Repository config:** The shared `.mcp/.mcp-config.yaml` exposes Context7 as `servers.context7`, defaulting to the public HTTPS endpoint with no auth header so anonymous access works out of the box. Add a `CONTEXT7_API_KEY` header locally when you provision higher limits.
- **Transport note:** Server-Sent Events are being retired; prefer HTTP or stdio transports when wiring Context7 into new automations.
- **Client coverage:** Official install snippets are provided for Cursor, Claude Code, Windsurf, Claude Desktop, Zed, Roo Code, Gemini CLI, Qwen Coder, VS Code, Cline, Amp, Augment Code, Opencode, and more—reuse those samples as references when authoring `.mcp/.mcp-config.yaml`.

## Authentication & Limits
- Public use (no key) works for lightweight lookups, but provisioning a Context7 API key from the dashboard lifts rate limits and unlocks private repository coverage; pass it as `CONTEXT7_API_KEY` in request headers or CLI arguments.
- Treat keys as secrets: store them in `.mcp/.env.mcp`, reference via environment placeholders inside `.mcp/.mcp-config.yaml`, and rotate them alongside other MCP provider credentials.

## Governance Notes
- When onboarding Context7, coordinate changes with MCPSAG so its SOP, rollback plan, and routing defaults capture the new provider configuration.
- After configuration updates, set `MCP_ROUTER_PROVIDER=context7` and run `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"` to confirm connectivity, and document the availability in `docs/AGENTS.md` and `.mcp/AGENTS.md` if routing expectations shift.
