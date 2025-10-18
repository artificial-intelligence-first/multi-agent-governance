Source: https://github.com/modelcontextprotocol/typescript-sdk (last synced: 2025-10-18)

# MCP TypeScript SDK

## Summary
- Official TypeScript toolkit for implementing Model Context Protocol clients and servers within Node.js and browser-based environments.
- Powers MCP integrations for VS Code, web dashboards, and automation agents by offering typed APIs, transport adapters, and manifest helpers.

## Key Details
- **Packages**: Publishes scoped npm modules (`@modelcontextprotocol/sdk`, `@modelcontextprotocol/client`, etc.) covering protocol types, client runtimes, and server utilities.
- **Installation**: Install via `pnpm add @modelcontextprotocol/sdk` (preferred in this repository) or `npm install`. Type definitions ship with the packages for strict TypeScript projects.
- **Server framework**: Provides builder functions to declare tools, resources, prompts, and events. Supports capability negotiation, structured logging, and streaming results over WebSocket.
- **Client APIs**: Includes lightweight clients for both Node.js and browser contexts, handling reconnection, heartbeat, and cancellation semantics.
- **Manifest tooling**: Supplies helpers to generate and validate `mcp.json` manifests so servers can be registered with MCP registries or auto-discovered by clients.
- **Samples**: Repository features example integrations (GitHub, filesystem, OpenAI) plus Vitest suites demonstrating contract testing and capability expansion.

## Dependencies
- Use pnpm inside this repo (`pnpm install`) to maintain deterministic lockfiles; commit updates alongside AGENTS/SSOT changes when new SDK features are adopted.
- When wiring the TypeScript SDK into Codex CLI or Flow Runner scripts, ensure bundlers keep ESM/CJS compatibility per the repo’s build rules.
- Document any custom transports or middleware in DocsSAG so downstream agents understand how to authenticate and observe tool traffic.

## Update Log
- 2025-10-18: Initial summary based on the official MCP TypeScript SDK repository.
