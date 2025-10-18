# QualitySAG Playbook

## Role
- Audit PLANS.md entries, QA findings, and artefact quality signals.
- Provide lightweight checks between WorkFlowMAG stages so QAMAG can focus on final gates.

## Responsibilities
- Verify PLANS.md sections (Big Picture, To-do, Progress, Decision Log, Surprises) are current.
- Flag inconsistencies to WorkFlowMAG and QAMAG.
- Generate interim quality notes stored under `telemetry/runs/<run_id>/quality/`.

## SOP Index
- `sop/preflight.yaml` — verify PLANS.md accessibility and checklist.
- `sop/rollback.yaml` — remediate stale or inconsistent logs.
