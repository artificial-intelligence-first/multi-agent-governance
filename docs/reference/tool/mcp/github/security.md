Source: https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning (last synced: 2025-10-19)
Source: https://docs.github.com/en/code-security/secret-scanning/introduction/about-push-protection (last synced: 2025-10-19)
Source: https://docs.github.com/en/organizations/keeping-your-organization-secure/managing-security-settings-for-your-organization/reviewing-the-audit-log-for-your-organization (last synced: 2025-10-19)
Source: https://docs.github.com/en/enterprise-cloud@latest/organizations/managing-saml-single-sign-on-for-your-organization (last synced: 2025-10-19)

> Note: GitHub removed the previous public article covering prompt-injection protections. Track upstream docs for a replacement before reintroducing that citation.

# GitHub MCP Security Capabilities

## Overview
- GitHub MCP exposes security endpoints that let agents scan repositories, enforce protection rules, and audit access in real time.
- SecuritySAG consumes these tools to keep the Multi Agent Governance fleet compliant with least-privilege and secure-by-default policies.

## Feature Matrix
- **Secret scanning & push protection** — Detect hard-coded secrets and block commits that match high-signal detectors. Endpoints: `security/list-secret-scanning-alerts`, `security/update-secret-scanning-alert`, `security/configure-push-protection`.
- **Prompt-injection defense** — Review prompts and documentation context for exfiltration or escalation patterns before publication. Endpoint: `security/review-copilot-prompts`.
- **Repository access control** — Audit collaborators, teams, and app installations to enforce least privilege. Endpoints: `repos/list-collaborators`, `teams/list-repos`, `orgs/list-app-installations`.
- **Repository scanning & audit logging** — Aggregate code scanning, Dependabot, and audit-log events to maintain compliance records. Endpoints: `security/list-code-scanning-alerts`, `dependabot/list-alerts-for-repo`, `orgs/get-audit-log`.
- **Authorization hardening** — Confirm SAML enforcement, token scopes, and branch protection before approving automation changes. Endpoints: `orgs/get-saml-sso`, `applications/get-by-slug`, `repos/get-branch-protection`.

## Operational Guidance
- Store security findings in `docs/generated/security-securitysag.md` so downstream agents (DocsSAG, WorkflowMAG, GovernanceSAG) can reference current risks.
- Raise incidents via `telemetry/security/incidents/` when GitHub MCP highlights critical alerts or permission changes.
- Coordinate dependency-driven alerts with DepsSAG before modifying lockfiles or runtime versions.
- Record all scope or configuration changes in `.mcp/AGENTS.md` and `.mcp/SSOT.md`, and mention SecuritySAG as the accountable owner.
