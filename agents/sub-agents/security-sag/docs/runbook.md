# SecuritySAG Runbook

## Normal Operation
1. Follow the SecuritySAG SOP to initialise the review (venv activated, `MCP_ROUTER_PROVIDER=github`, token scopes verified).
2. Execute GitHub MCP secret scanning, push protection, prompt review, access audit, and authorization checks; log findings in `docs/generated/security-securitysag.md`.
3. File remediation tasks or incidents when alerts exceed SOP thresholds, and notify WorkflowMAG / GovernanceSAG per escalation rules.
4. Update `.mcp/AGENTS.md`, `.mcp/SSOT.md`, and `agents/SSOT.md` if token scopes, provider settings, or security policies change; re-run validation commands.

## Incident Response
- **Leaked secret detected** → Rotate credentials immediately, enable push protection for affected patterns, add post-mortem entry under `telemetry/security/incidents/<date>.md`.
- **Prompt-injection risk** → Quarantine offending artefacts, coordinate with DocsSAG/PromptSAG to patch content, rerun prompt review tools before release.
- **Unauthorized access change** → Revoke access via GitHub, capture audit log evidence, inform OperationsMAG and GovernanceSAG for documentation updates.
- **Branch protection or automation drift** → Reinstate required checks (`make validate`, security sweep), confirm token scopes are least privilege, and document the fix in the SSOT cascade.
