# MCPSAG SOP

## Purpose
Standard operating procedure for MCPSAG to govern Model Context Protocol configuration, documentation, and validation across the Multi Agent Governance fleet.

## Prerequisites
- Active virtual environment (`python3 -m venv .venv && source .venv/bin/activate`).
- Updated dependencies (`pip install -r requirements.txt` or `uv sync`).
- Access to `.mcp/.env.mcp` (never commit secrets).
- Change request populated using `templates/mcp_change_checklist.md`.

## Procedure — Add or Update an MCP Provider
1. **Triage**
   - Review the checklist submission, confirm rate limits, token scopes, and target environments.
   - Notify DocsSAG, PromptSAG, ContextSAG, and OpsMAG of pending changes.
2. **Prepare Configuration**
   - Edit `.mcp/.mcp-config.yaml` to add/update the provider.
   - Update `.mcp/.env.mcp.example` with new environment variables and defaults.
   - Capture provider notes in `docs/reference/tool/mcp/` (create a new file when necessary).
3. **Documentation Cascade**
   - Revise `.mcp/AGENTS.md`, root `AGENTS.md`, `agents/AGENTS.md`, `agents/SSOT.md`, `/SSOT.md`, and `docs/reference/tool/mcp/README.md`.
   - Refresh `agents/sub-agents/AGENTS.md` and `agents/AGENT_REGISTRY.yaml` to reference MCPSAG responsibilities and routing.
   - Update ExecPlans or Flow Runner instructions if orchestrations change.
4. **Validation**
   - Run `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"` and provider-specific smoke tests.
   - Execute automated coverage:
     - `PYTHONPATH=src/mcprouter/src uv run python -m pytest src/mcprouter/tests -k mcp`
     - `PYTHONPATH=src/flowrunner/src:src/mcprouter/src uv run python -m pytest src/flowrunner/tests/test_runner.py -k mcp`
     - `make validate` when shared automation is affected.
   - Store logs/artefacts with the change request and share with OpsMAG + QAMAG.
5. **Deploy**
   - Merge only after validation passes and stakeholders sign off.
   - Notify dependent agents once the provider is live.
6. **Monitor & Roll Back**
   - Track telemetry for 24 hours. If regression appears, revert the configuration and follow the rollback checklist below.

## Rollback Checklist
1. Restore the last known-good `.mcp/.mcp-config.yaml`.
2. Remove or comment out new environment variables from `.mcp/.env.mcp.example`.
3. Revert documentation updates or append rollback notes to the affected AGENTS/SSOT files.
4. Alert OpsMAG, QAMAG, and impacted agents.
5. Record the incident summary under the originating ExecPlan and update `templates/mcp_change_checklist.md` with lessons learned if applicable.

## Validation Commands
- `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"`
- `MCP_ROUTER_PROVIDER=github PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"`
- `PYTHONPATH=src/mcprouter/src uv run python -m pytest src/mcprouter/tests -k mcp`
- `PYTHONPATH=src/flowrunner/src:src/mcprouter/src uv run python -m pytest src/flowrunner/tests/test_runner.py -k mcp`
- `make validate`

## Escalation Contacts
- OpsMAG — runtime incidents, telemetry anomalies.
- QAMAG — validation failures, documentation drift.
- DocsSAG/PromptSAG — downstream documentation or prompt updates.
