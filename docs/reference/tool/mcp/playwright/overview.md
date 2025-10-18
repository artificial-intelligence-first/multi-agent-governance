Source: https://github.com/microsoft/playwright-mcp (last synced: 2025-10-18)
Source: https://github.com/mcp/microsoft/playwright-mcp (last synced: 2025-10-18)

# Playwright MCP Server

## Overview
- Node-based MCP server that exposes Playwright-driven browser automation via structured accessibility trees rather than screenshots.
- Ideal for deterministic interactions that lean on semantic selectors; complementary to Chrome DevTools MCP's tracing and Puppeteer-style tooling.
- Supports STDIO (default) plus SSE/Streamable HTTP; BrowserSAG uses the stdio launch so sessions align with agent lifecycle.

## Requirements
- Node.js 18+ with npm capable of installing `@playwright/mcp`.
- Playwright downloads the required browser channels on first run; ensure host permissions allow installing Chromium/Firefox/WebKit binaries.
- Optional browser extension enables attaching to existing Chrome/Edge sessions; see repository instructions if needed.

## Configuration
- `.mcp/.mcp-config.yaml` registers the server under `servers.playwright` using `npx @playwright/mcp@latest`.
- CLI flags (e.g., `--headless`, `--browser`, `--viewport-size`, `--save-trace`, `--output-dir`) tailor automation runs; coordinate standard defaults via MCPSAG before changing shared config.
- Supports configuration files (`--config path/to/config.json`) for complex setups, including storage state, proxy settings, and permission grants.

## Operations & Validation
- Verify availability with `npx @playwright/mcp@latest --help` and inspect installed browser channels via `npx playwright install --help` if troubleshooting.
- Use BrowserSAG workflows to capture accessibility snapshots, structured actions, and optional traces (`--save-trace`, `--save-video`).
- Store generated Playwright artefacts beneath `telemetry/runs/<run_id>/browser/` alongside Chrome DevTools traces for cross-tool analysis.

## Update Log
- 2025-10-18: Documentation added when BrowserSAG adopted Playwright MCP for structured automation.
