---
name: draft-quality
description: >
  DocsSAG-only preflight for Markdown drafts: verify outline coverage, SSOT terminology, draft quality rubric adherence, severity logging, release readiness gates, Flow Runner trace linkage, and publication sign-off requirements.
---

# DocsSAG Draft Quality Skill

> Use this Skill whenever DocsSAG generates a draft that needs publication read-through before release. It consolidates the quality rubric, remediation workflow, and telemetry hooks so reviewers can greenlight drafts quickly.

## Quick start
- Collect the draft package (Markdown, diagnostics, provenance) and the original request outline.
- Cross-check section coverage: every requested heading must exist with substantive content and no TODO placeholders.
- Scan for SSOT terminology drift using `make validate-docs-sag` and manual spot checks on glossary terms.
- Review metadata (`last_synced`, audience, owners) and ensure KnowledgeMag references remain intact.
- Capture findings in `resources/draft-quality-review.md`, tagging severity and remediation owners.
- Log review status to `collab/skills-adoption/notes.md` or the active release tracker so GovernanceSAG sees readiness, and link any Flow Runner trace IDs captured during validation.
- Coordinate with Flow Runner guardrails reviewers when `skills_exec` pilots are active, ensuring remediation logs reference the corresponding guardrail approvals.

## Quality checklist
- Coverage
  - [ ] Outline headings present in order, with narrative paragraphs or bullet structure as required.
  - [ ] Release scope, prerequisites, and rollback guidance documented.
  - [ ] Change log links or telemetry screenshots embedded when referenced.
- Terminology & accuracy
  - [ ] Glossary terms align with `agents/SSOT.md`; no deprecated names or metrics.
  - [ ] Code snippets and commands reflect the current automation behaviour.
  - [ ] Security and compliance annotations included for governance-sensitive flows.
- Editorial
  - [ ] Tone matches DocsSAG prompts (concise, second-person for guides, neutral voice for references).
  - [ ] Tables, callouts, and links render correctly in Markdown preview.
  - [ ] Accessibility guidelines met (alt text, heading hierarchy).
- Remediation
  - [ ] Findings logged with owner + due date.
  - [ ] Follow-up workflow (`workflows/draft_docs.wf.yaml`) queued if automation support is needed.
  - [ ] Final approval recorded in the release communication channel.

## Automation hooks
- `make validate-docs-sag` — run after edits to confirm schema and terminology guardrails.
- `src/automation/scripts/analyze_skills_pilot.py` — capture pilot metrics (Phase 2 uses `--skills-exec`).
- `src/automation/scripts/check_terminology.py` — spot-check additional glossary drift when KnowledgeMag packets change.

## Resources
- [`../../docs/runbook.md`](../../docs/runbook.md) — incident response and diagnostics when drafts regress.
- [`../../prompts/draft.prompt.yaml`](../../prompts/draft.prompt.yaml) — authoritative guardrails for tone, structure, and governance callouts.
- [`../../sop/preflight.yaml`](../../sop/preflight.yaml) — pre-release checklist that complements this Skill.

## Script usage
- No execution is enabled for this Skill. Keep `allow_exec=false` until remediation automation is approved and recorded in `skills/ALLOWLIST.txt`.
