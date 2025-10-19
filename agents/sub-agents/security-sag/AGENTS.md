# SecuritySAG Playbook

## Mission
- Guard the Multi Agent Governance fleet against repository threats by orchestrating GitHub MCP security tooling (secret scanning, push protection, prompt-injection defenses, access control, audit visibility, and authorization hardening).
- Surface actionable findings, remediation owners, and follow-up tickets whenever security checks detect drift.
- Partner with GovernanceSAG and MCPSAG so security posture changes stay reflected across AGENTS/SSOT cascades and shared MCP configuration.

## Dev environment tips
- Activate the repository virtual environment and install requirements from the root before running validation scripts.
- Export a fine-grained `GITHUB_TOKEN` with `security_events`, `repo`, `read:org`, `audit_log`, and `workflow` scopes. Store the token in `.mcp/.env.mcp`; never copy secrets into prompts or SOPs.
- When testing locally, set `MCP_ROUTER_PROVIDER=github` and run `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"` to confirm the token exposes security endpoints.
- Use `uv run python -m pytest agents/sub-agents/security-sag/tests` before commits to keep prompts, docs, and SOPs in sync.

## GitHub MCP dependencies
- Secret scanning & push protection — invoke via GitHub MCP `security/list-secret-scanning-alerts` and `security/configure-push-protection`; ensure alert thresholds and protected branch rules match the SOP.
- Prompt-injection defense — leverage `security/review-copilot-prompts` (REST) to audit context packs; record findings in DocsSAG references when escalations are required.
- Repository access control — sync org/team permission diffs with `repos/list-collaborators` and `orgs/list-app-installations`; flag drift to OperationsMAG.
- Repository scanning & audit log — capture periodic snapshots via `security/list-code-scanning-alerts`, `dependabot/list-alerts`, and `orgs/get-audit-log`.
- Authorization hardening — verify branch protection, token scopes, and SSO requirements with `repos/get-branch-protection` and `orgs/get-saml-sso`.

## Testing instructions
- `python -m pytest agents/sub-agents/security-sag/tests` — prompt and reference validation.
- `make validate-security-sag` (add entry when automation scripts are ready) — pipeline coverage for SOP checklists and GitHub MCP smoke tests.
- Capture GitHub MCP responses in redacted fixtures under `tests/resources/` so CI runs stay offline.

## References
- Docs: `docs/reference/tool/mcp/github/security.md`
- SOP: `agents/sub-agents/security-sag/sop/README.md`
- Prompt: `agents/sub-agents/security-sag/prompts/security_sag.prompt.yaml`
- Governance sync: Update `agents/AGENT_REGISTRY.yaml`, `agents/SSOT.md`, `.mcp/AGENTS.md`, and `.mcp/SSOT.md` whenever security scope, credentials, or workflows change.
