# MCP Change Checklist Template

Fill out this template before MCPSAG approves or implements any MCP configuration change. Attach the completed form to the ExecPlan or ticket.

## Request Metadata
- **Request ID / ExecPlan:** 
- **Requester:** 
- **Date:** 
- **Target environment(s):** (local, staging, production)
- **Change type:** (new provider, update provider, retire provider, config tuning, incident fix)

## Provider Details
- **Provider name:** 
- **Endpoints / transports:** (REST, GraphQL, WebSocket, etc.)
- **Required environment variables:** (list names and expected scopes)
- **Token / credential owner:** 
- **Rotation cadence:** 
- **Rate limits / quotas:** 
- **SDK dependencies:** (library versions, language support)
- **Reference docs updated?** (list `docs/reference/` paths)

## Configuration Tasks
- [ ] `.mcp/.mcp-config.yaml` changes drafted
- [ ] `.mcp/.env.mcp.example` updated
- [ ] Secrets prepared in `.mcp/.env.mcp`
- [ ] Docs cascade updated (`AGENTS.md`, `.mcp/AGENTS.md`, `agents/AGENTS.md`, `agents/SSOT.md`, `/SSOT.md`)
- [ ] `agents/AGENT_REGISTRY.yaml` adjustments (if routing changes)
- [ ] Flow Runner / automation updates queued (list files)
- [ ] Templates or SOPs refreshed

## Validation Plan
- [ ] `uvx mcpctl route "status"` (provider default)
- [ ] `uvx mcpctl route "<custom>" --provider <name>` (if applicable)
- [ ] `PYTHONPATH=src/mcprouter/src uv run python -m pytest src/mcprouter/tests -k mcp`
- [ ] `PYTHONPATH=src/flowrunner/src:src/mcprouter/src uv run python -m pytest src/flowrunner/tests/test_runner.py -k mcp`
- [ ] `make validate`
- [ ] Additional tests / scripts: 

## Rollback & Monitoring
- **Rollback path:** (commit hash, config snapshot, automation steps)
- **Monitoring signals:** (`mcp.config_sync`, provider-specific metrics)
- **Escalation contacts notified:** (OpsMAG, QAMAG, DocsSAG, PromptSAG, Flow Runner)

## Approvals
- [ ] MCPSAG reviewer:
- [ ] OpsMAG:
- [ ] QAMAG:
- [ ] Security (if required):
