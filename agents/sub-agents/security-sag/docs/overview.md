# SecuritySAG Overview

SecuritySAG enforces security posture across the Multi Agent Governance fleet. It relies on GitHub MCP security tooling to surface actionable findings, drive remediation, and keep governance artefacts aligned with operational reality.

## Capabilities
- Runs secret scanning, push protection, and prompt review sweeps for every governed repository.
- Audits repository access (collaborators, teams, app installations) and validates branch protection rules.
- Aggregates code scanning, Dependabot, and audit-log events to maintain continuous security coverage.
- Confirms token scopes, SSO settings, and automation entitlements align with least-privilege policy.
- Escalates incidents to WorkflowMAG, GovernanceSAG, and OperationsMAG when findings breach thresholds.

## GitHub MCP Tooling
- **Secret hygiene:** `security/list-secret-scanning-alerts`, `security/update-secret-scanning-alert`, `security/configure-push-protection`.
- **Prompt safety:** `security/review-copilot-prompts`, `repos/get-content` for differential analysis.
- **Access control:** `repos/list-collaborators`, `teams/list-repos`, `orgs/list-app-installations`, `repos/get-branch-protection`.
- **Scanning & audits:** `security/list-code-scanning-alerts`, `dependabot/list-alerts-for-repo`, `orgs/get-audit-log`.
- **Authorization checks:** `applications/get-by-slug`, `orgs/get-saml-sso`, `scim/list-provisioned-identities`.

## Handoffs
- **Inbound:** Security review requests from WorkflowMAG, GovernanceSAG, or automated schedulers. Requires GitHub MCP credentials with `security_events`, `repo`, `read:org`, `workflow`, and `audit_log` scopes.
- **Outbound:** Findings triage logged in `docs/generated/security-securitysag.md`, incident reports in `telemetry/security/incidents/`, and documentation updates across the AGENTS/SSOT cascade.

## Operating Flow
1. Activate the SOP, verify MCP routing, and run the GitHub security toolchain.
2. Summarise findings with severity, owners, and due dates; open remediation tickets as needed.
3. Update `.mcp/AGENTS.md`, `.mcp/SSOT.md`, and `agents/SSOT.md` when scopes or policies change.
4. Emit telemetry metrics (`security.latency_ms`, `security.findings_total`) for observability and feedback into Governance audits.
