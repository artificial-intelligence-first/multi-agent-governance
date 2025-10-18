# MCP Configuration Runbook

This runbook captures MCPSAG’s operational flow for adding, updating, or retiring MCP providers. Use it alongside `sop/README.md` and the checklist template to keep documentation and automation synchronized.

## 1. Intake & Scoping
- Collect the change request (ticket, ExecPlan action, or incident) and ensure the submitter completed `templates/mcp_change_checklist.md`.
- Validate that prerequisites are met (provider spec, token scopes, endpoint availability, SDK compatibility notes).
- Identify affected agents (DocsSAG, PromptSAG, ContextSAG, Flow Runner, external clients) and notify stakeholders.

## 2. Configuration Draft
- Branch from the latest mainline state and edit `.mcp/.mcp-config.yaml`.
- Document new environment variables in `.mcp/.env.mcp.example`; note defaults and secret handling guidance.
- Capture supporting references in `docs/reference/tool/mcp/` (protocol changes, provider quirks, rate limits).

## 3. Documentation Cascade
- Update: `.mcp/AGENTS.md`, root `AGENTS.md`, `agents/AGENTS.md`, `agents/SSOT.md`, and `/SSOT.md`.
- Add or refresh provider notes under `docs/reference/tool/mcp/` (create a new file if the provider is not tracked yet).
- Ensure `AGENT_REGISTRY.yaml` includes new routing metadata or escalation targets.

## 4. Validation & Testing
- Smoke test via `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"` and provider-specific calls (`MCP_ROUTER_PROVIDER=github`, GraphQL queries, etc.).
- Execute automated coverage:
  - `PYTHONPATH=src/mcprouter/src uv run python -m pytest src/mcprouter/tests -k mcp`
  - `PYTHONPATH=src/flowrunner/src:src/mcprouter/src uv run python -m pytest src/flowrunner/tests/test_runner.py -k mcp`
  - `make validate` when broader automation might be affected.
- Record test output links (artefacts, console logs) for OpsMAG and QAMAG sign-off.

## 5. Deployment & Monitoring
- Merge configuration changes only after OpsMAG approves and QAMAG clears the validation results.
- Notify dependent agents and update Flow Runner workflows if routing changes alter orchestration steps.
- Monitor telemetry for 24 hours (`mcp.config_sync`, `mcp.provider.audit`, `mcp.error.rate`) to confirm stability.
- If issues arise, follow the rollback procedure in `sop/README.md` and complete the incident postmortem.
