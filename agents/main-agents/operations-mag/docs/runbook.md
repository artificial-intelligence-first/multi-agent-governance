# OperationsMAG Runbook

## Monitoring Loop
- Review `telemetry/runs/<run_id>/operations/operations_summary.json` after each WorkFlowMAG run.
- Compare telemetry budgets against SSOT.md expectations.
- Record findings in PLANS.md Progress and Decision Log.

## Escalation Criteria
- Latency budgets exceeded by >10%.
- Missing artefacts from any stage.
- Repeated WARN/FAIL results from `automation.compliance.pre`.

## Escalation Steps
- Notify the channel defined in `agents/AGENT_REGISTRY.yaml` (default: `#ops-ai`).
- Attach the relevant ExecPlan excerpt and `telemetry/runs/<run_id>/summary.json`.
- Coordinate with QAMAG for joint assessment when quality issues coincide with latency breaches.
