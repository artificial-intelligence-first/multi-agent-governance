# Skills Program Pilot — Sign-off Brief (2025-10-19)

## Context
- Objective: Decide whether to proceed with the Skills rollout (shared knowledge bundles + guarded execution) beyond the pilot cohorts.
- Scope: Phase 1 read-only Skills (`api-design`, `security-review`, `document-triage`) and Phase 2 execution pilot (`draft-quality`, `flow-runner-guardrails`).
- Stakeholders: GovernanceSAG (program lead), MCPSAG (technical steward), Flow Runner maintainers.

## Metrics Snapshot
- Routing accuracy: Phase 1 precision 0.8182 / recall 0.9000; Phase 2 precision 1.0 / recall 1.0 with allow_exec accuracy 1.0 (`telemetry/reports/skills_phase1_20251019.json`, `telemetry/reports/skills_phase2_20251019.json`).
- Prompt savings: Average 69.8 % token reduction relative to legacy `AGENTS.md` + `agents/SSOT.md` prompts (`telemetry/reports/skills_token_reduction.json`).
- Execution guard: SkillExecutionGuard steady-state p95 38.9 ms, cold-start 1.35 s, max 39.7 ms for repeated runs (`telemetry/reports/skills_exec_latency_20251019.json`); all runs emitted `skill_exec_attempt/result` telemetry with no guardrail escape.
- Telemetry coverage: `telemetry/skills/events.jsonl` captures selection, load, and execution events (including the initial blocked attempt before regex normalization).

## Risk Notes
- Allowlist regex required normalization (quotes removed) before successful execution; remediation tracked in `PLANS.md` Surprises & Discoveries.
- Execution remains limited to staging (`skills_exec=true` only for pilot workspaces); production still defaults to deny-by-default.

## Decisions Requested
1. GovernanceSAG approval to adopt the Skills program (including 30-day registry/allowlist reviews and weekly telemetry exports).
2. MCPSAG authorization to enable `skills_v1` / staged `skills_exec` beyond pilots once guardrails remain stable for two review cycles.
3. Flow Runner maintainer confirmation that the guardrail performance and telemetry meet operational requirements.

## Attachments
- `telemetry/reports/skills_phase1_20251019.json`
- `telemetry/reports/skills_phase2_20251019.json`
- `telemetry/reports/skills_token_reduction.json`
- `telemetry/reports/skills_exec_latency_20251019.json`
- `collab/skills-adoption/notes.md`
- `PLANS.md`
