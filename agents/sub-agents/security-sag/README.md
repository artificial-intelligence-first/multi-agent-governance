# SecuritySAG

SecuritySAG is the Multi Agent Governance security specialist. It consumes GitHub MCP security capabilities to monitor and remediate risks in governed repositories.

## Responsibilities
- Collect findings from GitHub secret scanning, push protection, code scanning, Dependabot, and audit logs; translate them into remediation tasks for WorkflowMAG and Ops.
- Guard agent prompts and knowledge artefacts against prompt-injection or malicious context by reviewing upstream content before it reaches production pipelines.
- Verify repository access policies (branch protection, collaborator entitlements, SSO enforcement) and coordinate fixes with GovernanceSAG and OperationsMAG.
- Harden authorization flows by validating token scopes, OAuth app installations, and automation permissions referenced in `.mcp/.env.mcp`.

## Assets
- `AGENTS.md` — operating guide for maintainers.
- `prompts/security_sag.prompt.yaml` — baseline instructions for the agent runtime.
- `sop/README.md` — execution checklist for security reviews and incident response.
- `docs/overview.md` — summary of GitHub MCP security features and usage guidance.
- `tests/` — prompt and documentation validation.
- `workflows/` — Flow Runner hooks for periodic security sweeps (populate as automation matures).

## Collaboration
- Coordinate MCP provider edits with MCPSAG before enabling new GitHub endpoints.
- Notify DepsSAG when security alerts reference vulnerable dependencies so rollout plans cover remediation.
- Escalate governance-impacting findings to GovernanceSAG so AGENTS/SSOT artefacts stay accurate.
