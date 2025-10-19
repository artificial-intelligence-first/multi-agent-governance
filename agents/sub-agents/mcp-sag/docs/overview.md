# MCPSAG Overview

MCPSAG governs the Model Context Protocol configuration for the Multi Agent Governance fleet. It keeps `.mcp/.mcp-config.yaml`, supporting documentation, and downstream automation in sync whenever providers, credentials, or routing rules change.

## Responsibilities
- Evaluate and execute MCP provider change requests (additions, removals, parameter updates) using the MCPSAG SOP and checklist.
- Maintain the documentation cascade across `.mcp/AGENTS.md`, `.mcp/SSOT.md`, root AGENTS/SSOT files, and `docs/reference/tool/mcp/`.
- Coordinate validation commands (`uv run python -m mcp_router.cli route`, targeted pytest suites, `make validate`) and record outcomes for QAMAG/OpsMAG review.
- Track provider prerequisites (runtime versions, token scopes, deployment hosts) and ensure they remain aligned with SecuritySAG, BrowserSAG, and other dependent agents.
- Surface configuration drift or incidents to GovernanceSAG and WorkflowMAG, driving remediation when telemetry indicates MCP instability.

## Handoffs
- **Inbound:** Change requests via `templates/mcp_change_checklist.md`, Ops incidents, or governance audits signalling outdated provider state.
- **Outbound:** Updated configuration files, documentation updates, validation logs, and status reports delivered to OpsMAG, GovernanceSAG, and affected agents.

## Operating Flow
1. Intake & scope the request; verify prerequisites and impacted agents.
2. Draft configuration updates, update environment templates, and align documentation.
3. Run validation commands and capture artefacts.
4. Coordinate review/approval, deploy changes, and monitor telemetry for regressions.
5. Escalate issues via incident workflows when provider stability or access is compromised.

Refer to `runbook.md` for detailed step-by-step execution and escalation paths.

## Skills integration
- See `skills-integration.md` for the metadata loader, embedding cache, feature flag, and telemetry design that enables MCPSAG to progressively load `/skills/` artefacts for Codex agents.
- Align change checklists with the Skills program before flipping `skills_v1` or `skills_exec` feature flags in shared environments.
