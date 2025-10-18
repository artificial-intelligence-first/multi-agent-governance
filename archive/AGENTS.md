# AGENTS — `archive`

## Mission
- Preserve legacy artefacts, audit evidence, and migration snapshots without polluting active workflows.
- Provide a single reference point for rollbacks and historical investigations.

## Subdirectories
- `audits/` — immutable audit evidence. Append-only; do not rewrite history.
- `backups/` — periodic backups or exports (note cadence and tooling in `archive/SSOT.md`).
- `deprecated/` — retired assets kept for reference. Never reintroduce files directly from here without review.
- `snapshots/` — before/after snapshots for major schema or workflow changes. Organise by timestamp.

## Operating Notes
- Whenever you archive content, log the action in PLANS.md (Surprises or Decision Log) and capture context in `archive/SSOT.md`.
- Large binary assets must use Git LFS or an external artefact store; document the location if stored elsewhere.
- Link archived items back to the live replacement or rationale (e.g., commit SHA, PR, or ExecPlan entry).

## References
1. [[SSOT]]
2. [[archive/SSOT]]
3. `docs/reference/files/CHANGELOG.md/overview.md`
4. `docs/reference/files/AGENTS.md/OpenAI.md`
