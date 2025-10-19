# DocsSAG Playbook

## Role
- Produce publication-ready Markdown drafts from KnowledgeMag cards, outlines, and governance constraints.

## Responsibilities
- Accept requests defined by `agents/contracts/docs_sag_request.schema.json` and emit `docs_sag_response` payloads with draft content, structured sections, and review notes.
- Preserve SSOT terminology, provenance, and policy guidance provided by upstream agents.
- Coordinate with QualitySAG, ReferenceSAG, and SecuritySAG when drafts require additional checks.

## SOP Index
- `docs/overview.md` — scope, routing, and collaboration guidance.
- `docs/runbook.md` — drafting workflow, diagnostics, and incident response.
- `sop/preflight.yaml` / `sop/rollback.yaml` — operational readiness and recovery steps.
