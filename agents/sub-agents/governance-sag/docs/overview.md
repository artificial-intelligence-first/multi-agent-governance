# GovernanceSAG Overview

GovernanceSAG continuously audits repository governance artefacts to keep the
Multi Agent Governance fleet aligned with upstream specifications.

## Focus Areas
- **AGENTS cascade**: root file plus directory-specific AGENTS notes.
- **SSOT alignment**: `/SSOT.md`, `agents/SSOT.md`, `.mcp/AGENTS.md`.
- **ExecPlans**: `PLANS.md` presence, freshness, and canonical sections.
- **Changelog hygiene**: `CHANGELOG.md` format, `Unreleased`, SemVer sync.
- **Reference drift**: `docs/reference/` and `docs/generated/` last-synced metadata.

## Outputs
- `telemetry/runs/<run_id>/governance/governance_report.json` with `status`, `drift`, and per-check findings (agents cascade, SSOT alignment, changelog compliance, ExecPlan hygiene, telemetry capture).
- Source recency snapshot for each configured artefact.
- Optional inline comments for WorkFlowMAG or QAMAG during pipeline runs.
