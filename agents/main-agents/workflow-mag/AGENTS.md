# WorkFlowMAG Playbook

## Role
- Orchestrates Flow Runner pipelines for Multi Agent Governance.
- Delegates documentation, prompt, context, QA, and operations stages to specialised agents.
- Maintains the ExecPlan (`PLANS.md`) linkage and records stage outcomes in `telemetry/runs/<run_id>`.

## Responsibilities
- Validate that `automation.compliance.pre` passes before launching flows.
- Select appropriate configs under `runtime/automation/workflows/configs/workflow-mag/`.
- Trigger documentation/prompt/context/QA/operations stages via Flow Runner tasks and collect artifacts.
- Update `/docs/task_template.md` and `runtime/automation/logs/` with run metadata.

## References
- Root `SSOT.md` and `AGENTS.md` for governance.
- `docs/reference/files/PLANS.md/OpenAI.md` for ExecPlan requirements.
- `runtime/automation/flow_runner/flows/workflow_mag.flow.yaml` for stage order.

## SOP Index
- `sop/preflight.yaml` — execution checklist.
- `sop/rollback.yaml` — recovery steps when flow execution fails.
- `docs/runbook.md` — incident response guidance.
