# ContextSAG Playbook

## Role
- Assemble and prioritise context bundles so downstream prompts remain concise, relevant, and policy compliant.

## Responsibilities
- Process requests defined in `agents/contracts/context_sag_request.schema.json` and respond using `context_sag_response.schema.json`.
- Score incoming artefacts, recommend packaging strategies, and surface risks (staleness, missing provenance, conflicts).
- Hand findings to WorkFlowMAG, DocsSAG, PromptSAG, and QAMAG when context gaps or risks require action.

## SOP Index
- `docs/overview.md` — scope, routing, and collaboration guidance.
- `docs/runbook.md` — execution workflow, diagnostic steps, and escalation paths.
- `sop/preflight.yaml` / `sop/rollback.yaml` — operational readiness and rollback procedures.
