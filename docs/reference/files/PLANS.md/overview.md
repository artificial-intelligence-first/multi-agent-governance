# ExecPlans (PLANS.md) Overview

## Purpose
- Provide a landing page for ExecPlan references so contributors know where to find the canonical workflow (`OpenAI.md`) and supporting templates.
- Reinforce that every long-running task in this repository must have a living `PLANS.md` aligned with the compliance checklist.

## Contents
- [OpenAI ExecPlan guidance](OpenAI.md) — authoritative rules and section templates sourced from the OpenAI Cookbook article.
- `README.md` — directory expectations and review cadence for ExecPlan governance notes.

## Usage Notes
- Before starting a substantial task, skim `OpenAI.md` to confirm the ExecPlan sections you must maintain and the validation commands to record.
- Compliance automation (`uv run -m automation.compliance.pre`) asserts the presence of both `PLANS.md` and `OpenAI.md`; treat warnings as blockers until resolved.
- Keep plan updates timestamped in UTC and mirror major decisions into `agents/SSOT.md` when terminology or hand-offs change.

## Maintenance
- Review this overview every 60 days or after upstream ExecPlan guidance evolves.
- When external sources change, update `OpenAI.md` first, then note the sync date here.
