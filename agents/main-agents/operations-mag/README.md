# OperationsMAG

OperationsMAG safeguards observability for the Multi Agent Governance automation fleet.
It ingests telemetry summaries, tracks SLA budgets, and highlights risks or
escalations for human operators.

## Responsibilities
- Monitor stage latency and output freshness against budgets defined in SSOT.md.
- Coordinate cleanup of `runtime/automation/logs/` per retention policy.
- Surface anomalies to PLANS.md and WorkFlowMAG before runs proceed.

## Inputs
- `telemetry/runs/<run_id>/operations/operations_summary.json`
- Flow Runner telemetry streams (when available)
- ExecPlan decision logs

## Outputs
- Operational notes back into PLANS.md and `/docs/task_template.md`
- Alerts via designated escalation channels (see `agents/AGENT_REGISTRY.yaml`)
