# GovernanceSAG

GovernanceSAG watches the governance cascade (AGENTS/SSOT/CHANGELOG/PLANS)
to ensure repository policies stay aligned with upstream specifications.

## Inputs
- Root `AGENTS.md` plus subordinate AGENTS files
- `SSOT.md` and `agents/SSOT.md`
- `CHANGELOG.md`, `docs/reference/`, and `PLANS.md` artefacts

## Outputs
- Findings recorded in `telemetry/runs/<run_id>/governance/governance_report.json`
- Drift summary per check (`agents_cascade`, `ssot_alignment`, `changelog_compliance`, `execplan`, `telemetry_capture`)
- Status updates relayed to WorkFlowMAG and QAMAG for remediation
