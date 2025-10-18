# Collaboration SSOT

## Scope
- Decision logs, meeting notes, and review summaries generated inside the repository.
- Applies to cross-functional interactions impacting agents, automation, or governance policy.

## Ownership
- Primary: WorkFlowMAG (ensures PLANS.md and collab artefacts stay in sync).
- Supporting: DocsSAG (formatting/templates), OpsMAG (incident reviews), QAMAG (quality audits).

## Standards
- File naming: `decision-YYYYMMDD-topic.md`, `meeting-YYYYMMDD-slug.md`, `review-<repo>-<id>.md`.
- Frontmatter: include `date`, `owners`, `status`, and references to related tasks or runs.
- Link back to PLANS.md and telemetry artefacts where applicable.

## Procedures
1. When a decision affects routing/tooling, update AGENTS.md and SSOT.md for the impacted directory.
2. Store artefacts in Markdown; append summary tables for checklists or votes.
3. Use `docs/task_template.md` for longer-form coordination notes, then archive the final version here.

## Related Documents
- `collab/AGENTS.md`
- `docs/reference/files/PLANS.md/OpenAI.md`
- `agents/AGENT_REGISTRY.yaml`
