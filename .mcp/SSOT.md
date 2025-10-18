# MCP Single Source of Truth

## Immutable Inputs
- `.mcp/.mcp-config.yaml` is the authoritative router configuration. Use `${VAR}` / `${VAR:-default}` for environment-specific overrides.
- `.mcp/.env.mcp` stores provider secrets (`OPENAI_API_KEY`, `MCP_ROUTER_PROVIDER`, `GITHUB_TOKEN`, etc.). Template: `.env.mcp.example`.
- Default router provider is `dummy`. Enable `openai`, `github`, etc. by extending the `providers` section and updating `.env.mcp`.
- Context7 MCP server lives under `servers.context7`; declare `CONTEXT7_MCP_URL` (HTTPS endpoint), `CONTEXT7_API_KEY` (header value), and optionally `CONTEXT7_API_URL` for tooling that calls the REST API directly.

## Change Procedure
1. Capture objective, impact, and validation plan in PLANS.md.
2. Execute MCPSAG SOP/checklist (`agents/sub-agents/mcp-sag/`).
3. Edit `.mcp-config.yaml`; update `.env.mcp.example` if new variables are introduced.
4. Run all validation commands below and note outcomes in PLANS.md.

## Validation Commands
- Connectivity: `uvx mcpctl route "ping"`
- Router tests: `PYTHONPATH=src/mcprouter/src uv run python -m pytest src/mcprouter/tests/test_router.py`
- Flow integration: `PYTHONPATH=src/flowrunner/src:src/mcprouter/src uv run -m pytest src/flowrunner/tests/test_runner.py -k mcp`

## Audit Checklist
- Ensure no secrets or absolute paths are hard-coded in `.mcp-config.yaml`.
- If legacy entries remain, annotate with reason and retirement timeline.
- Communicate `.env.mcp` changes (GitHub tokens, Context7 keys, etc.) to operations stakeholders after review.

## References
- `agents/sub-agents/mcp-sag/AGENTS.md`
- `src/mcprouter/README.md`
- `src/automation/workflows/lib/mcp_gateway.py`
