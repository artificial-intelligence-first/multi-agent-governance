# SecuritySAG SOP

Follow this checklist whenever running a security review, responding to incidents, or onboarding new repositories into the Multi Agent Governance fleet.

## Prerequisites
- Repository virtual environment activated.
- `GITHUB_TOKEN` with `security_events`, `repo`, `read:org`, `workflow`, and `audit_log` scopes stored in `.mcp/.env.mcp`.
- `MCP_ROUTER_PROVIDER=github` exported for the current shell (or configured in the runtime harness).
- Confirm MCPSAG signed off on any pending `.mcp/.mcp-config.yaml` edits.

## Execution Steps
1. **Secret scanning sweep**
   - Run the GitHub MCP tool `security/list-secret-scanning-alerts` scoped to the repository.
   - For each open alert, add findings to `docs/generated/security-securitysag.md` (create if absent) and notify owners.
   - Verify push protection status via `security/configure-push-protection`; enable protections for high-signal detectors when disabled.
2. **Prompt-injection audit**
   - Call `security/review-copilot-prompts` for the latest prompt diffs (DocsSAG, PromptSAG, KnowledgeMag).
   - Flag risky content in `agents/sub-agents/security-sag/docs/prompt-findings.md` and coordinate mitigation with the authoring agent.
3. **Access control verification**
   - Use `repos/list-collaborators` and `teams/list-repos` to enumerate write access.
   - Cross-check against `agents/SSOT.md`. Escalate mismatches to GovernanceSAG and update documentation.
   - Confirm branch protection via `repos/get-branch-protection`; ensure required status checks include `make validate` and security sweeps.
4. **Repository scanning snapshot**
   - Collect code scanning and Dependabot alerts (`security/list-code-scanning-alerts`, `dependabot/list-alerts-for-repo`).
   - Create remediation tickets or update existing ones; mark blockers in PLANS.md if resolution requires coordination.
5. **Audit log review**
   - Invoke `orgs/get-audit-log` (filter by repository) and review changes to permissions, secrets, or branch settings.
   - For any suspicious events, open an incident entry under `telemetry/security/incidents/YYYY-MM-DD.md`.
6. **Authorization hardening**
   - Validate SAML/SSO and token scopes (`orgs/get-saml-sso`, `applications/get-by-slug`).
   - Document results in `.mcp/SSOT.md` and confirm automation tokens remain scoped to least privilege.

## Exit Criteria
- All findings triaged with owners and due dates.
- Documentation updated (`agents/SSOT.md`, `.mcp/AGENTS.md`, `.mcp/SSOT.md`, DocsSAG references).
- Telemetry events recorded (security.latency_ms, security.findings_total, audit anomalies).
- GovernanceSAG notified when policy updates or documentation revisions are required.

## sop_refs
sop_refs:
  - label: Preflight checks
    path: ./preflight.yaml
  - label: Rollback steps
    path: ./rollback.yaml
  - label: Prompt guardrail tests
    path: ../tests/test_prompt_security_features.py
