# WorkFlowMAG Runbook

## Preflight
- Confirm PLANS.md reflects the current objective and tasks (`exec plan`).
- Run `uv run -m automation.compliance.pre --task-name "<Task>" --categories workflow,docs,prompt,context,qa,operations`.
- Export `WORKFLOW_CONFIG` pointing to the desired config JSON (e.g., `runtime/automation/workflows/configs/workflow-mag/test.json`).

## Execution
- Dry run: `PYTHONPATH=src uv run flowctl run --dry-run runtime/automation/flow_runner/flows/workflow_mag.flow.yaml` (Docs & Prompts execute in parallel; Context waits on Prompts).
- Production: rerun without `--dry-run`.
- Monitor `.runs/<run_id>/summary.json` for stage completion notes.

## Incident Response
- If a stage fails, consult its artefact directory inside `.runs/<run_id>`.
- Use `sop/rollback.yaml` to determine whether to rerun stages or escalate.
- Update PLANS.md `Surprises` and `Decision Log` with findings before resuming work.

## Rollout
- **Phase 1 (Staging):** Execute the parallel workflow with synthetic payloads; confirm Docs, Prompts, and Context artefacts are populated.
- **Phase 2 (Canary):** Route a limited set of real tasks through WorkFlowMAG; monitor QA findings and operations telemetry for regressions.
- **Phase 3 (Production):** Flip routing defaults in `agents/AGENT_REGISTRY.yaml` and record outcomes in PLANS.md.
