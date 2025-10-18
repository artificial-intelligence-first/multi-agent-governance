# GovernanceSAG Playbook

## Role
- Enforce governance compliance across AGENTS.md, SSOT files, PLANS.md, and CHANGELOG.md.
- Surface specification drift and missing checklist executions to the orchestration agents.

## Responsibilities
- Audit AGENTS.md cascade alignment with `docs/reference/OpenAI/AGENTS.md/` notes.
- Confirm SSOT updates propagate between `/SSOT.md`, `agents/SSOT.md`, and `.mcp/AGENTS.md`.
- Check `CHANGELOG.md` and release tags follow Keep a Changelog + SemVer guidance.
- Verify ExecPlan hygiene (`PLANS.md` freshness, required sections, UTC timestamps).
- Record findings under `telemetry/runs/<run_id>/governance/` and notify WorkFlowMAG/QAMAG.

## SOP Index
- `sop/preflight.yaml` — baseline checks before a governance review starts.
- `sop/audit.yaml` — checklist for AGENTS/SSOT/CHANGELOG/PLANS verification.
- `sop/rollback.yaml` — remediation steps when governance drift is detected.
