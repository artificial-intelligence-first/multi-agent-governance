# Telemetry SSOT

## Scope
- Canonical location for run artefacts, logs, validation outputs, and telemetry schemas.
- Applies to Flow Runner executions, Codex MCP interactions, and manual audits captured by OpsMAG/QAMAG.

## Ownership
- Primary: OperationsMAG (observability and retention policy).
- Supporting: QAMAG (quality gates), WorkFlowMAG (run exports), MCPSAG (MCP routing logs).

## Key Policies
- **Retention**: Default keep for 90 days unless legal/compliance says otherwise. Redact secrets before committing.
- **Structure**: Every run generates `<run_id>/summary.json` plus per-step JSON in `steps/`. Keep token usage in metadata when Codex MCP is involved.
- **Validation**: `make validate` pipelines must write JSON/Markdown artefacts to `validation/` with UTC timestamps in filenames.
- **Snapshots**: Place migration snapshots under `snapshots/<YYYYMMDD>/`. Mark large assets as LFS if they exceed repository limits.

## Required Procedures
1. Update PLANS.md when telemetry schema, retention, or report scope changes.
2. Run `make validate` (or the targeted validator) after editing scripts or schemas; attach outputs to the PR.
3. Coordinate with DocsSAG when telemetry summaries inform published documentation.

## Related Documents
- `telemetry/AGENTS.md`
- `docs/reference/files/CHANGELOG.md/overview.md`
- `docs/reference/agents/sdk/codex-sdk/OpenAI.md`
- `.mcp/AGENTS.md` (for MCP-related telemetry defaults)
