# PLANS.md (ExecPlan) Operating Guidance

## Purpose
- Synchronize human and AI understanding of long-running tasks.
- Prevent context drift by keeping the AI’s objectives, progress, and surprises in one live document.
- Provide reviewers with a concise progress report before inspecting code or other assets.

## Rules
- **Trigger** — When the command phrase `exec plan` is issued, the active agent must open or create `PLANS.md`.
- **Structure** — Maintain the sections: Big Picture, To-do, Progress, Decision Log, Surprises, Outcomes & Retrospectives.
- **Lifecycle** — Initialize before work begins, update after each step (Progress/Decision Log/Surprises), and clean up on completion.
- **Style** — Write in clear English with checkbox lists for tasks; timestamp updates in UTC; preserve Markdown headings.
- **Linkage** — Cross-reference relevant entries in `AGENTS.md` or `SSOT.md` when context or policy dependencies exist.

## Execution Steps
1. **Initiate** — On `exec plan`, ensure `PLANS.md` exists (use `uv run -m automation.execplan` to generate the default template) and populate the Big Picture with the task objective.
2. **Plan** — List actionable To-do items with checkboxes, noting prerequisites or dependent agents.
3. **Operate** — After each action, append entries to Progress (timestamped), Decision Log (what/why), and Surprises (unexpected findings).
4. **Close** — When milestones finish, summarize outcomes in Outcomes & Retrospectives and mark tasks complete.
5. **Archive** — Once the task wraps, capture final observations, then reset or prune the document for the next engagement.

## Notes
- Treat `PLANS.md` as a live external memory; never leave it stale during an active plan.
- Reviewers should consult `PLANS.md` first to understand execution history.
- Other agents may link to relevant sections for coordination or auditing.
