# WorkFlowMAG

WorkFlowMAG governs the end-to-end Multi Agent System automation pipeline. It sequences
DocsSAG, PromptSAG, ContextSAG, QualitySAG, OperationsMAG, and QAMAG so each stage receives the artefacts it needs.

## Responsibilities
- Resolve Flow Runner configs and launch the orchestrated workflow.
- Synchronise PLANS.md updates with stage transitions.
- Persist intermediate outputs under `.runs/<run_id>` for downstream review.
- Escalate to OperationsMAG when telemetry budgets are at risk.

## Inputs
- `runtime/automation/workflows/configs/workflow-mag/*.json`
- ExecPlan context from `PLANS.md`
- Task metadata captured in `/docs/task_template.md`

## Outputs
- Run artefacts inside `.runs/<run_id>` (plan.json, docs, prompts, context, QA, operations summary, final summary).
- Log entries in `runtime/automation/logs/workflow/`.

## Related Documents
- `docs/overview.md` — concept summary.
- `docs/runbook.md` — incident response checklist.
- `workflows/orchestrate.wf.yaml` — Flow Runner friendly workflow description.
