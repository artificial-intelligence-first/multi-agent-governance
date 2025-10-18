# MCPSAG Agent Playbook

## Role & Scope
- Maintain the MCP single source of truth for the Multi Agent Governance fleet.
- Coordinate configuration, documentation, and validation across `.mcp/`, `agents/`, `docs/reference/tool/mcp/`, `src/mcprouter/`, and Flow Runner assets.
- Facilitate MCP access requests from DocsSAG, PromptSAG, ContextSAG, Flow Runner, and external orchestration (Codex CLI, Cursor).

## Inputs
- MCP change tickets or ExecPlan actions that reference the `templates/mcp_change_checklist.md`.
- Provider manifests (token scopes, endpoints, GraphQL requirements).
- Telemetry and incident reports from OpsMAG / QAMAG.
- SDK and specification updates tracked under `docs/reference/tool/mcp/`.

## Outputs
- Updated `.mcp/.mcp-config.yaml` and `.mcp/.env.mcp` guidance (never commit secrets).
- Synchronized documentation in root `AGENTS.md`, `.mcp/AGENTS.md`, `agents/AGENTS.md`, `agents/SSOT.md`, and `docs/reference/tool/mcp/README.md`.
- Validation reports (pytest logs, `uvx mcpctl` results) stored alongside change records or attached to ExecPlans.
- Escalation notes for unresolved incidents, including rollback scripts referenced in `sop/README.md`.

## Primary Resources & Tooling
- `.mcp/.mcp-config.yaml` (router/provider definitions).
- `.mcp/.env.mcp` (runtime secrets; reference the example file for required variables).
- `docs/reference/tool/mcp/` (protocol, GitHub provider, SDK guidance).
- `src/mcprouter/` and `src/flowrunner/` (runtime integrations and unit tests).
- `uvx mcpctl` (runtime smoke tests) and Makefile aliases (`make validate`, `make validate-prompt`, etc.).

## SOP Summary
1. **Intake** – Confirm the request includes the checklist from `templates/mcp_change_checklist.md` and applicable upstream references.
2. **Design** – Update `.mcp/.mcp-config.yaml` with new providers or settings; capture environment variable expectations in `.mcp/.env.mcp.example`.
3. **Documentation Cascade** – Reflect changes in `.mcp/AGENTS.md`, root `AGENTS.md`, `agents/AGENTS.md`, `agents/SSOT.md`, `SSOT.md`, and reference docs (`docs/reference/tool/mcp/README.md` plus provider-specific files).
4. **Validation** – Run smoke tests (`uvx mcpctl route "status"` and targeted provider calls) and automated coverage:
   - `PYTHONPATH=src/mcprouter/src uv run python -m pytest src/mcprouter/tests -k mcp`
   - `PYTHONPATH=src/flowrunner/src:src/mcprouter/src uv run python -m pytest src/flowrunner/tests/test_runner.py -k mcp`
   - `make validate` if broader automation is impacted.
5. **Handoff** – Share validation evidence with OpsMAG/QAMAG, update ExecPlans, and notify dependent agents (DocsSAG/PromptSAG/Flow Runner).
6. **Post-change Monitoring** – Track telemetry (`mcp.config_sync`, `mcp.provider.audit`) and roll back if failure thresholds trigger.

## Update & Review Cadence
- Reconcile `.mcp/AGENTS.md` and this playbook at least every 30 days or sooner when providers change.
- Sync `templates/mcp_change_checklist.md` with SDK updates and new validation tooling.
- Schedule Flow Runner scenario reviews to confirm MCPSAG orchestration remains current (see `docs/runbook.md`).

## Verification Commands
- `uvx mcpctl route "status"`
- `uvx mcpctl route "status" --provider github` (when GitHub is enabled)
- `PYTHONPATH=src/mcprouter/src uv run python -m pytest src/mcprouter/tests -k mcp`
- `PYTHONPATH=src/flowrunner/src:src/mcprouter/src uv run python -m pytest src/flowrunner/tests/test_runner.py -k mcp`
- `make validate` (full suite)

## Change Propagation
- Always update `agents/AGENT_REGISTRY.yaml` when MCPSAG routing or escalation paths change.
- Reference MCPSAG in ExecPlans and Flow Runner workflows before automation depends on new provider capabilities.
- Ensure DocsSAG receives updated generated documentation path instructions (`docs/generated/`) when MCP-driven references shift.
