# Archive SSOT

## Scope
- Legacy artefacts removed from active directories, audit trail exports, and structural snapshots.
- Applies to any material relocated from `agents/`, `docs/`, `src/`, `telemetry/`, or `collab/`.

## Ownership
- Primary: OpsMAG (compliance and retention).
- Supporting: WorkFlowMAG (documents migrations), DocsSAG (ensures references stay accurate).

## Policies
- **Logging**: Every addition must be mentioned in PLANS.md with reason, source path, and destination.
- **Retention**: Follow compliance guidance—default keep forever unless policy dictates purge. Track purge windows here.
- **Integrity**: Files under `audits/` are append-only. Use new filenames for follow-up evidence.
- **Snapshots**: Name directories `YYYYMMDD-description/` and include a README describing trigger and follow-up steps.

## Procedures
1. Move files using standard Git operations so history remains traceable.
2. Update references in AGENTS/SSOT docs to point at the new live location or note deprecation.
3. When restoring from archive, document the review outcome and new location in PLANS.md and this SSOT.

## Related Documents
- `archive/AGENTS.md`
- `docs/reference/files/PLANS.md/OpenAI.md`
- `telemetry/AGENTS.md`
