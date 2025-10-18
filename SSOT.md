# Multi Agent Governance Single Source of Truth

This repository maintains agent-level terminology, contracts, and governance guidance under `agents/SSOT.md`. The top-level note clarifies how the specifications published by the artificial-intelligence-first **agents** and **flow-runner** projects are composed inside the Multi Agent Governance repository.

## Scope
- Applies to every agent under `agents/` (main, sub, and shared components).
- Covers JSON schemas, glossary entries, upstream/downstream integrations, and operational playbooks.

## Specification Baselines
- Agents Directory open specification: https://github.com/artificial-intelligence-first/agents-directory (repository layout, governance workflow, and vocabulary synchronized as of October 12, 2025).
- Flow Runner workflow specification: https://github.com/artificial-intelligence-first/flow-runner (YAML workflow schema and runtime behaviour mirrored via vendored packages in `src/flowrunner/` and `src/mcprouter/`, synced to commit 477db9c4ae364e30348de58acb29b95e0e5597fa on October 12, 2025).
- MCP routing SSOT: `.mcp/.mcp-config.yaml` (providers, router defaults, and env bindings documented in `.mcp/AGENTS.md`). Update this whenever servers, tokens, or session policies move so Codex/Cursor/Flow Runner stay aligned.
- GitHub MCP usage: see `docs/reference/tool/mcp/github/overview.md` for configuration, token scopes, GraphQL usage, and validation steps; declare `GITHUB_TOKEN` (plus optional `GITHUB_API_BASE` / `GITHUB_API_VERSION`) in `.mcp/.env.mcp` before enabling the provider.
- Context7 MCP usage: see `docs/reference/tool/mcp/context7/overview.md` for remote server setup, API key handling, and validation guidance; store `CONTEXT7_MCP_URL`, `CONTEXT7_API_KEY`, and optionally `CONTEXT7_API_URL` in `.mcp/.env.mcp`.
- Serena MCP usage: see `docs/reference/tool/mcp/serena/overview.md` for stdio launch commands, context/mode defaults, and project activation flows; configure `SERENA_CONTEXT` and `SERENA_PROJECT_ROOT` in `.mcp/.env.mcp` to match the repo under automation.
- Chrome DevTools MCP usage: see `docs/reference/tool/mcp/chrome-devtools/overview.md` for browser automation prerequisites, launch flags, and validation guidance; ensure Node.js 20.19+, npm, and Chrome are installed before enabling `servers.chrome-devtools`.
- MarkItDown MCP usage: see `docs/reference/tool/mcp/markitdown/overview.md` for conversion capabilities, transport options, and Python environment requirements; install `markitdown-mcp` (with relevant extras) before enabling `servers.markitdown`.
- Playwright MCP usage: see `docs/reference/tool/mcp/playwright/overview.md` for accessibility-driven automation guidance, CLI flags, and Node.js requirements; ensure browser binaries are provisioned before enabling `servers.playwright`.
- Browser automation workflows: see `agents/sub-agents/browser-sag/AGENTS.md` for BrowserSAG responsibilities, SOPs, and telemetry requirements.
- Reference server usage: see `docs/reference/tool/mcp/servers/overview.md` plus sub-pages for Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, and Time. Provide `MCP_FILESYSTEM_ROOT` / `MCP_GIT_REPOSITORY` before exposing write-capable tools, and ensure Node/uv tooling versions match upstream guidance.
- MCPSAG (agents/sub-agents/mcp-sag) governs the MCP SSOT, documentation cascade, and validation commands; execute its SOP and checklist before merging configuration changes.
- GovernanceSAG (agents/sub-agents/governance-sag) audits the AGENTS/SSOT/CHANGELOG/PLANS cascade; notify it when governance artefacts or templates change so telemetry stays authoritative.

## How to Use
1. Review `agents/SSOT.md` before editing prompts, workflows, or contracts.
2. Record any new terminology, schema versions, or dependency changes there as part of your change set.
3. Keep examples and validation scripts in sync (`make validate`), ensuring contracts stay compatible with Flow Runner executions.
4. Loop in MCPSAG for any MCP-related deltas (configuration, docs, SDK updates) so the SSOT stays authoritative.

For detailed change-management procedures and glossary definitions, consult `agents/SSOT.md` directly.
