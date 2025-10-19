# Sub-Agents Playbook

## Dev environment tips
- Work from the repository venv; DocsSAG and other scripts assume Python tooling is installed there.
- Follow the same scaffold as DocsSAG when introducing a new sub-agent (README, docs, prompts, workflows, sop, tests, AGENTS.md).
- Keep shared prompt partials referenced via relative paths (`../../shared/...`) to avoid import issues.
- MCPSAG centralises MCP configuration updates—coordinate with it before introducing new MCP dependencies in other sub-agents.

## Testing instructions
- DocsSAG: `python -m pytest agents/sub-agents/docs-sag/tests/test_agent.py` plus `make validate-docs-sag`.
- PromptSAG: `python -m pytest agents/sub-agents/prompt-sag/tests/test_agent.py` plus `make validate-prompt`.
- ContextSAG: `python -m pytest agents/sub-agents/context-sag/tests/test_agent.py` plus `make validate-context`.
- MCPSAG: `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"` plus targeted pytest runs (`src/mcprouter/tests -k mcp`, `src/flowrunner/tests/test_runner.py -k mcp`) and `make validate` when configuration changes impact automation.
- GovernanceSAG: `python -m pytest agents/sub-agents/governance-sag/tests/test_governance_sag_agent.py` and ensure governance telemetry is populated during pipeline dry runs.
- Add agent-specific validators under `src/automation/scripts/` when new schemas or assets are introduced.

## PR instructions
- Document new observability metrics and routes in `agents/AGENT_REGISTRY.yaml`.
- Update `agents/SSOT.md` when sub-agents add terminology or contract changes.
- Ensure DocsSAG persists drafts to `docs/generated/` and PromptSAG references the latest material under `docs/reference/`.
- When replacing the sample sub-agent, remove placeholder prompts and update this file to describe the real implementation.

## Directory hints
- `docs-sag/` – documentation drafting specialist.
- `prompt-sag/` – prompt engineering specialist.
- `context-sag/` – context engineering specialist that curates and packages context bundles.
- `quality-sag/` – ExecPlan and interim quality auditor.
- `reference-sag/` – reference and citation auditor.
- `mcp-sag/` – MCP configuration specialist that governs `.mcp/.mcp-config.yaml`, documentation cascades, and validation workflows.
- `governance-sag/` – governance compliance monitor that keeps AGENTS/SSOT/CHANGELOG/PLANS artefacts aligned.
- `browser-sag/` – browser automation specialist orchestrating Chrome DevTools, Playwright, and MarkItDown MCP servers.
- `deps-sag/` – dependency lifecycle specialist that plans upgrades, regenerates locks, and coordinates with DocsSAG/GovernanceSAG/QAMAG on rollout impacts.
- `security-sag/` – GitHub MCP-driven security specialist that handles secret scanning, push protection, prompt-injection defence, access audits, and authorization hardening.
