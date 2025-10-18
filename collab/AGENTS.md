# AGENTS — `collab`

## Mission
- Capture decisions, reviews, and meeting notes so contributors can trace intent without digging through external tools.
- Maintain lightweight templates that downstream agents (DocsSAG, OpsMAG, QAMAG) can parse programmatically.

## Subdirectories
- `decisions/` — decision records (`decision-YYYYMMDD-topic.md`). Link to PLANS.md entries and relevant artefacts.
- `meeting-notes/` — meeting or sync minutes. Frontmatter must include date/time, attendees, and agenda.
- `reviews/` — code/doc review transcripts. Reference PR IDs or tasks and summarise outcomes.
- `retrospective/` — sprint or incident retrospectives with action items and owners.

## Operating Notes
- Use English for artefacts unless stakeholders request otherwise; keep timestamps in UTC.
- Each new record should link back to PLANS.md (Decision Log or Progress) and the owning ExecPlan section.
- When decisions introduce or retire tooling, update the relevant AGENTS/SSOT files and note it in `collab/SSOT.md`.

## References
1. [[SSOT]]
2. [[collab/SSOT]]
3. `docs/task_template.md`
4. `docs/reference/files/PLANS.md/OpenAI.md`
