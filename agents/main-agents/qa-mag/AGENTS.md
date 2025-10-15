# QAMAG Playbook

## Role
- Enforce quality gates across the Multi Agent System pipeline.
- Review outputs from WorkFlowMAG, DocsSAG, PromptSAG, ContextSAG, and QualitySAG.
- Publish audit notes and follow-ups in PLANS.md and `.runs/<run_id>/qa/qa_report.json`.

## Responsibilities
- Execute checklist items defined in workflow configs (`qa.checklist`).
- Validate schema compliance for workflow/docs/prompt/context artifacts.
- Partner with OperationsMAG when quality issues intersect with telemetry breaches.

## References
- Root SSOT.md / AGENTS.md.
- `docs/reference/files/PLANS.md/OpenAI.md` for logging expectations.
- `agents/contracts/` for schema validation targets.

## SOP Index
- `sop/preflight.yaml` — QA readiness checks.
- `sop/rollback.yaml` — remediation when gates fail.
- `docs/runbook.md` — end-to-end QA procedures.
