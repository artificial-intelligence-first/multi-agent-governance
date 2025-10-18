Source: https://github.com/ChromeDevTools/chrome-devtools-mcp (last synced: 2025-10-18)
Source: https://github.com/mcp/chromedevtools/chrome-devtools-mcp (last synced: 2025-10-18)
Source: https://developer.chrome.com/blog/chrome-devtools-mcp (last synced: 2025-10-18)

# Chrome DevTools MCP Server

## Overview
- Official Chrome DevTools team server that lets MCP clients drive a live Chrome browser via Puppeteer and DevTools Protocol for debugging, tracing, screenshots, and network inspection.
- Exposes more than 25 automation tools grouped under input, navigation, emulation, performance, network, and debugging categories; outputs align with Chrome's Lighthouse-style diagnostics.
- Ships as an npm package launched with `npx -y chrome-devtools-mcp@latest` so clients always receive the newest server build without a separate install step.

## Requirements
- Node.js 20.19 LTS or newer, npm, and a stable-channel Chrome (or Chromium) installation on the host machine.
- The shared configuration starts the server via stdio; ensure MCP clients have permission to spawn GUI apps (or enable `--headless` when running in CI/headless hosts).
- Optional environment variable: set `DEBUG=*` to stream verbose logs; point `--logFile <path>` at a writable location if you need persistent traces.

## Configuration
- `.mcp/.mcp-config.yaml` registers the server under `servers.chrome-devtools` with `npx -y chrome-devtools-mcp@latest`.
- Launch flags can be added by MCPSAG when a consistent behaviour is required:
  - `--headless` to run without a visible Chrome window.
  - `--browserUrl <url>` / `--wsEndpoint <ws://>` to attach to an already-running Chrome session.
  - `--executablePath <abs/path>` or `--channel <stable|beta|dev|canary>` to pick a specific Chrome binary.
  - `--viewport 1280x720` (or other `widthxheight`) to pin initial window size; `--isolated` to use a throwaway user data dir.
- When invoking manually, run `npx -y chrome-devtools-mcp@latest --help` to confirm the CLI is resolvable in the active environment.

## Operations & Validation
- Smoke-test connectivity with `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"` after enabling the server and ensure Chromedriver/Chrome pop up when invoking a tool (e.g., `performance_analyze_insight` against a public URL).
- Capture trace output artifacts under `~/.config/Chrome DevTools MCP` (default working directory) when troubleshooting performance runs; clean regularly to avoid disk bloat.
- Coordinate updates through MCPSAG so `.mcp/AGENTS.md`, `.mcp/.env.mcp.example`, root `AGENTS.md`, and `agents/SSOT.md` stay aligned with prerequisites (Node/Chrome versions, headless guidance, logging expectations).

## Update Log
- 2025-10-18: Documentation captured on onboarding Chrome DevTools MCP via stdio launch with `npx -y chrome-devtools-mcp@latest`.
