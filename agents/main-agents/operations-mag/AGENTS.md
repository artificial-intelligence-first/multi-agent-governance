# OperationsMAG Playbook

## Role
- Monitor telemetry budgets and SLA adherence across the WorkFlowMAG pipeline.
- Collect diagnostics from `telemetry/runs/<run_id>/operations/operations_summary.json`.
- Coordinate escalations to human operators when latency budgets or quality gates fail.

## Responsibilities
- Subscribe to WorkFlowMAG output summaries and QAMAG findings.
- Update relevant sections of PLANS.md and `/docs/task_template.md` with operational notes.
- Maintain observability dashboards and retention rules for `runtime/automation/logs/`.

## References
- Root SSOT.md / AGENTS.md for governance requirements.
- `docs/reference/files/PLANS.md/OpenAI.md` for ExecPlan logging.
- `docs/reference/files/PNPM.md/` when pnpm-based tooling is in scope.

## SOP Index
- `sop/preflight.yaml` — checks before accepting ownership of a run.
- `sop/rollback.yaml` — actions when telemetry or budgets are violated.
- `docs/runbook.md` — operational response scenarios.
