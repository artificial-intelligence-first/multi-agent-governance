# MCP Configuration Playbook

## Structure
- `.mcp-config.yaml` is the single source of truth for MCP routers and servers. Use `${VAR}` or `${VAR:-default}` interpolation so secrets stay in the environment.
- `.env.mcp` stores provider tokens; copy `.env.mcp.example` and keep the real file untracked. Define `OPENAI_API_KEY`, `MCP_ROUTER_PROVIDER`, and any per-provider overrides here.

## Usage
- Codex, Cursor, Flow Runner, and the `mcpctl` CLI all load configuration from this directory. Set `MCP_CONFIG_PATH`/`MCP_ENV_FILE` only when testing alternates; defaults resolve to this folder automatically.
- Switch providers by updating `router.provider` and extending `providers` in `.mcp-config.yaml`. Avoid ad-hoc environment tweaking—update the YAML so every tool reads the same state.
- Active provider templates: `dummy`, `openai`, and `github` (GitHub REST/GraphQL). Supply `GITHUB_TOKEN` via `.env.mcp` before enabling the GitHub provider; override `GITHUB_API_BASE` or `GITHUB_API_VERSION` when targeting Enterprise or new API releases.
- MCPSAG (`agents/sub-agents/mcp-sag/`) owns the documentation and validation cascade for this folder; follow its SOP and checklist before merging configuration edits.

## Verification
- Run `uvx mcpctl route "ping"` to confirm routing after edits; pass `--log-dir` for audit output.
- For regression coverage, execute `PYTHONPATH=src/mcprouter/src uv run python -m pytest src/mcprouter/tests/test_router.py`.
- Consult MCPSAG’s playbook for extended coverage (`src/mcprouter/tests -k mcp`, `src/flowrunner/tests/test_runner.py -k mcp`) and Flow Runner validation guidance.
