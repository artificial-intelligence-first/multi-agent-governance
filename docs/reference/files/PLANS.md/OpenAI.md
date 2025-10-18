Source: https://cookbook.openai.com/articles/codex_exec_plans (last synced: 2025-10-15)

# ExecPlans (PLANS.md) Guidance

## Summary
- ExecPlans are living execution specs that keep multi-hour coding tasks aligned between humans and AI, derived from OpenAI Cookbook guidance.
- The `exec plan` workflow ensures progress, decisions, and surprises stay observable before reviewers inspect code or artefacts.
- Each PLANS.md must remain self-contained so a new contributor can complete the task with only the working tree and the document.

## Key Details
- **Trigger**: Run `uv run -m automation.execplan --task-name "<Task>"` (or equivalent automation) whenever the `exec plan` command phrase is issued or work spans multiple milestones.
- **Structure**: Maintain the canonical sections—Big Picture, To-do, Progress, Decision Log, Surprises & Discoveries, Outcomes & Retrospective, Context & Orientation, Plan of Work, Concrete Steps, Validation & Acceptance, Idempotence & Recovery, Artifacts & Notes, Interfaces & Dependencies.
- **Living record**: Update Progress, Decision Log, and Surprises after every substantive action; timestamp entries in UTC and split partially complete work into “done” vs. “remaining”.
- **Clarity**: Define every term of art or avoid it, cite acceptance evidence, and emphasise observable behaviour over code diffs.
- **Autonomy**: Resolve ambiguities in the document itself and record why changes were made so any agent can resume from the plan alone.

## Lifecycle for this repository
1. **Initiate** – Ensure `PLANS.md` exists in the repo root, summarise the objective in Big Picture, and cross-link relevant sections of `AGENTS.md` / `SSOT.md`.
2. **Plan** – Capture actionable milestones with checkboxes, prerequisites, and assigned agents when multiple roles share the work.
3. **Operate** – After each action, refresh To-do states, add timestamped updates to Progress, log decisions with rationale, and document new findings under Surprises.
4. **Validate** – Keep Concrete Steps and Validation & Acceptance aligned with the latest implementation, including commands, expected output, and rollback notes.
5. **Close** – When outcomes are met, summarise results in Outcomes & Retrospective, confirm every task is checked off, export any artefacts, and remove PLANS.md once stakeholders confirm the work is complete (house rule unchanged).

## Repository practices
- Compliance checks (`uv run -m automation.compliance.pre`) require `PLANS.md` plus this reference file; fix missing artefacts before continuing.
- Reviewers, QAMAG, and OperationsMAG read PLANS.md first—keep it ahead of code pushes and reference any supporting docs or telemetry.
- Prototype or spike milestones are encouraged: label them clearly, explain the validation approach, and specify criteria to adopt or discard results.
- When parallel implementations are required, document how to validate each path, how to converge, and trace the decision in Decision Log.
- Archive significant diffs or transcripts under Artifacts & Notes, but keep the plan concise and navigable.

## Section skeleton
```md
# <Short, action-oriented description>
This ExecPlan is a living document. Keep Progress, Surprises & Discoveries, Decision Log, and Outcomes & Retrospective current as work proceeds.

## Purpose / Big Picture
## To-do
## Progress
## Surprises & Discoveries
## Decision Log
## Outcomes & Retrospective
## Context and Orientation
## Plan of Work
## Concrete Steps
## Validation and Acceptance
## Idempotence and Recovery
## Artifacts and Notes
## Interfaces and Dependencies
```

## Update Log
- 2025-10-15: Rewrote guidance with OpenAI Cookbook ExecPlan details and aligned repository operating rules.
