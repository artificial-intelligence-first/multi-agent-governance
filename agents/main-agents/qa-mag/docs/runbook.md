# QAMAG Runbook

## Preflight
- Run `make test` and relevant `make validate-*` targets.
- Confirm docs/prompt/context artefacts exist under `telemetry/runs/<run_id>/`.
- Review PLANS.md To-do items assigned to QAMAG.

## Execution
- Execute schema validation scripts (docs, prompt, context).
- Record PASS/WARN/FAIL results in `telemetry/runs/<run_id>/qa/qa_report.json`.
- Update PLANS.md Progress and Decision Log with findings.

## Follow-up
- If blocking issues are found, coordinate with WorkFlowMAG for remediation.
- Log surprises and recommendations for future runs.
