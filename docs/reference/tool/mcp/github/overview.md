# GitHub MCP Server

## Overview
- Bridges Multi Agent Governance tooling with GitHub repositories via the Model Context Protocol.
- Exposes read/write endpoints for issues, pull requests, commits, and file diffs so agents can coordinate repository work.
- Designed to operate behind the shared `.mcp/.mcp-config.yaml` surface so Codex, Cursor, and Flow Runner consume the same connection details.

## Configuration
- Add a `github` entry under `providers` in `.mcp/.mcp-config.yaml`, for example:

  ```yaml
  providers:
    github:
      type: github
      token: ${GITHUB_TOKEN}
      base_url: ${GITHUB_API_BASE:-https://api.github.com}
      timeout_sec: ${GITHUB_TIMEOUT_SEC:-15}
      api_version: ${GITHUB_API_VERSION:-2022-11-28}
  ```
- Store credentials in `.mcp/.env.mcp` (see `.env.mcp.example`) and reference them via `${GITHUB_TOKEN}` or similar placeholders inside the config.
- When running outside the repository root, set `MCP_CONFIG_PATH` and `MCP_ENV_FILE` to the canonical `.mcp` folder if automatic discovery is unavailable.
- Coordinate every configuration edit with MCPSAG (`agents/sub-agents/mcp-sag/`) so the checklist, SOP, and validation logs stay in sync with the GitHub provider state.

## Authentication
- Requires a GitHub fine-grained personal access token (`GITHUB_TOKEN`) scoped to the target repositories.
- Tokens should be managed via `.mcp/.env.mcp` (never committed). Rotate credentials on a regular cadence and audit scopes quarterly.
- Support for GitHub Apps can be added by extending the provider to handle installation IDs and app tokens.

## Usage
- Agents and routers automatically pick up the GitHub configuration once `router.provider` (or `MCP_ROUTER_PROVIDER`) points to `github`.
- For local smoke tests, run `uvx mcpctl route "status"` with the GitHub provider enabled to confirm authentication and repository access.
- Flow Runner MCP steps inherit the same configuration, so repository interactions can be orchestrated inside workflows without extra setup.
- GraphQL is supported by setting `config.graphql: true`; the prompt (or `config.query`) is used as the query body, and `config.variables` is passed through unchanged.
- Custom HTTP payloads (`config.json`, `config.data`, `config.body`, `config.text_body`) and request headers can be supplied per-step.

## Testing & Validation
- Extend `src/mcprouter/tests` with fixtures that stub GitHub API responses to keep coverage offline.
- Document producer/consumer changes in `.mcp/AGENTS.md` and `AGENTS.md` so downstream teams know when the GitHub server becomes available.
- Track rate limits and error patterns; feed them back into retry/backoff settings in `.mcp/.mcp-config.yaml`.
