# GovernanceSAG Runbook

## Normal Operation
1. Run the preflight SOP to confirm access to `AGENTS.md`, `SSOT.md`,
   `.mcp/AGENTS.md`, `CHANGELOG.md`, and `PLANS.md`.
2. Execute the audit SOP checklist, recording any drift or missing sections.
3. Persist the governance report under `telemetry/runs/<run_id>/governance/`
   and notify WorkFlowMAG of blockers.

## Incident Response
- Missing AGENTS cascade links → file Bug ticket, coordinate with DocsSAG, update
  references once fixed.
- Out-of-date `SSOT.md` or `.mcp/AGENTS.md` → engage MCPSAG, run the MCP change
  checklist, and document rotation details.
- `CHANGELOG.md` not following Keep a Changelog → synchronize with release owners,
  add missing `Unreleased` or version sections, rerun `make validate`.
- Stale `PLANS.md` (UTC > 24h) → escalate to WorkFlowMAG and log rollback actions.
