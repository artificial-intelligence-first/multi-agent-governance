---
name: document-triage
description: >
  Apply to DocsSAG and KnowledgeMag triage: backlog grooming, severity tagging, metadata freshness checks, release note routing, ownership hand-offs, remediation tracking, and publication readiness coordination.
---

# Document Triage Skill

> Apply this Skill when a generated document needs review before publication. It helps codify triage categories, capture remediation tasks, and surface blockers to the right agents.

## Quick start
- Identify the document source (DocsSAG draft, KnowledgeMag summary, external import) and intended audience.
- Scan backlog items for high-severity issues first (misinformation, policy violations, missing references) using the severity rubric below.
- Label findings with severity, assign owners (DocsSAG, KnowledgeMag, GovernanceSAG), and note deadlines.
- Update the triage log using the template in `resources/document-triage-log.md`.
- Notify stakeholders via the established channel (`#docs-triage`) with summary + next actions.
- Re-run validation scripts (`make validate-docs-sag`) after remediation before closing the ticket.

## Severity rubric
- **Critical** — Content violates policy, leaks secrets/PII, or contradicts SSOT. Immediate block; escalate to GovernanceSAG.
- **High** — Technical inaccuracies, broken references, or missing sections preventing publication; requires prompt fix.
- **Medium** — Style/structure issues, outdated examples, or minor inconsistencies; schedule within sprint.
- **Low** — Cosmetic fixes, typos, formatting polish; bundle with upcoming updates.

## Triage checklist
- Metadata
  - [ ] Title accurately reflects content and audience.
  - [ ] Last synced date present and current.
  - [ ] Source links valid and accessible.
- Content accuracy
  - [ ] Facts match SSOT terminology and metrics.
  - [ ] Code snippets execute or compile; include test evidence if available.
  - [ ] Procedures align with current SOPs and automation capabilities.
- Compliance
  - [ ] No confidential data or restricted tokens present.
  - [ ] Follows DocsSAG prompt guardrails (tone, voice, inclusive language).
  - [ ] Accessibility considerations noted (alt text, headings).
- Remediation
  - [ ] Owners assigned for each finding.
  - [ ] Validation steps defined (`make validate-docs-sag`, custom lint).
  - [ ] Follow-up ticket or PR referenced.

## Examples
- Reviewing DocsSAG draft for a release note: use checklist to confirm feature descriptions, update triage log with missing telemetry screenshots.
- Triage KnowledgeMag summary: ensure references back to SSOT entries, flag outdated metrics, and schedule updates.
- Importing external policy doc: classify gaps vs. local standards, assign GovernanceSAG for compliance review.

## Resources
- [`resources/document-triage-log.md`](resources/document-triage-log.md) — copy and fill for each triaged document.
- `docs/reference/README.md` — documentation syncing rules and references.
- `docs/reference/files/SKILL.md/Anthropic.md` — context on Skills structure for progressive disclosure.
- `agents/sub-agents/docs-sag/` — DocsSAG SOPs and runbook for remediation workflows.

## Script usage
- No scripts bundled. If automation (e.g., link checkers, style lint) is added, place scripts under `scripts/` and register them in `skills/ALLOWLIST.txt` with sha256 hashes before enabling.
