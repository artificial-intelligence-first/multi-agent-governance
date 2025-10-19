---
name: security-review
description: >
  Apply to security reviews covering authn/authz changes, threat modeling, SBOM coverage, secret management, push protection, incident response runbooks, GovernanceSAG compliance checklists, and escalation contact updates.
---

# Security Review Skill

> Use this Skill whenever a change could affect authentication, authorization, secrets handling, network boundaries, or data retention. It consolidates GovernanceSAG guidance so reviews remain consistent across agents.

## Quick start
- Identify the change surface (code modules, infrastructure, dependencies) and classification (routine, heightened, emergency).
- Retrieve the latest threat model or create one using STRIDE categories. Document assets, trust boundaries, and attacker capabilities.
- Review dependencies for known vulnerabilities (CVEs, GHSA advisories) and confirm `deps-sag` sign-off when upgrading packages.
- Cross-check secrets handling: storage location, rotation policy, access controls, audit logging, and incident contacts.
- Perform checklist walkthrough (below) and capture findings in the security review template.
- Summarise risk level (Low/Medium/High) and recommend mitigation timeline. Escalate High findings to GovernanceSAG immediately.

## Review checklist
| Area | Questions | Status |
| --- | --- | --- |
| Authentication | Are credential flows unchanged? If modified, are tokens scoped and rotated? | [ ] |
| Authorization | Do new endpoints enforce principle of least privilege? Are IAM policies updated? | [ ] |
| Data protection | Are secrets encrypted at rest/in transit? Do logs redact sensitive fields? | [ ] |
| Dependency risk | Are new dependencies vetted (license, maintenance, CVEs)? Is SBOM updated? | [ ] |
| Network exposure | Are ingress/egress rules bounded? Are ports/protocols documented? | [ ] |
| Observability | Do alerts/logs cover new failure modes? Are dashboards updated? | [ ] |
| Incident response | Are rollback paths defined? Is on-call aware of risk window? | [ ] |

## Examples
- Reviewing a new authentication flow: validate token issuance, session storage, and fallback paths; ensure STRIDE threat model updated.
- Dependency upgrade: confirm advisories addressed, run `make validate`, document SBOM changes, reference `deps-sag` approval.
- Infrastructure change: update network topology diagram, confirm firewall rules, simulate failure to ensure alerts trigger.

## Resources
- [`resources/security-review-template.md`](resources/security-review-template.md) — copy to the change workspace and fill before final approval.
- `docs/reference/tool/mcp/github/security.md` — GitHub MCP security endpoints (secret scanning, push protection).
- `agents/sub-agents/governance-sag/` — governance SOPs and escalation contacts.
- `docs/reference/files/SKILL.md/Anthropic.md` — background on Skills structure and progressive disclosure.

## Script usage
- No scripts are bundled. If automated scanners or SBOM generators are required, add them under `scripts/` and register hashes in `skills/ALLOWLIST.txt` before enabling execution.
