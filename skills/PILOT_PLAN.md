# Skills Pilot Playbook

Updated: 2025-10-19

## Phase 1 — Read-only Pilot (Shared Skills)

- **Scope**: `skills/api-design`, `skills/security-review`, `skills/document-triage`
- **Environments**: Development + staging workspaces with `skills_v1=true`, `skills_exec=false`
- **Participants**: GovernanceSAG (lead), DocsSAG (document triage), PromptSAG (prompt hygiene)
- **Cadence**:
  - Week 0: Enable feature flag for pilot cohort, seed curated prompt corpus (10 tasks per skill).
  - Weeks 1–2: Collect telemetry (`skill_selected`, `skill_loaded`), operator feedback via #skills-adoption.
  - Week 3: Review metrics and decide go/no-go for Phase 2.
- **Success metrics**:
  - ≥0.75 precision / ≥0.80 recall on curated tasks (`metrics/skills_phase1.json` baseline).
  - ≥15% average token reduction in Codex prompts once Skills load.
  - Positive qualitative feedback (≥80% “useful” rating) from pilot operators.
- **Data collection**:
  - Export telemetry snapshots weekly (`telemetry/skills/events.jsonl` → `telemetry/reports/skills_phase1_<date>.json`).
  - Capture operator notes in `collab/skills-adoption/notes.md`.
  - Log deviations and tuning in `PLANS.md` Decision Log.
- **Measurement tooling**:
  - Run `make pilot-skills-phase1` (or call `python src/automation/scripts/analyze_skills_pilot.py --dataset skills/pilot/phase1/dataset.jsonl --top-k 3 --threshold 0.75`) to compute precision/recall from the curated corpus (enable `--use-embeddings` when BGE model is available).
  - Store evaluation artifacts under `telemetry/reports/skills_phase1_<date>.json`.
- **Exit criteria**:
  - Metrics met for all three skills across at least two consecutive pilot reviews.
  - No open severity-1 issues (routing failures, hallucinated content).
  - GovernanceSAG signs off on `skills/api-design` + `skills/security-review` readiness checklist.

## Phase 2 — Controlled Execution Pilot (Agent-local Skills)

- **Scope**: Add `agents/sub-agents/docs-sag/skills/draft-quality` + shared automation Skill `skills/flow-runner-guardrails`.
- **Environments**: Staging only, with `skills_exec=true`, allowlist limited to approved scripts.
- **Participants**: GovernanceSAG (lead), MCPSAG (technical steward), Flow Runner maintainers.
- **Preparation**:
  - Populate `skills/ALLOWLIST.txt` with signed hashes, argument patterns, sandbox expectations.
  - Configure telemetry dashboards for `skill_exec_attempt` / `skill_exec_result`.
  - Dry-run Flow Runner guard (deny-by-default) to verify blocked paths and reporting.
- **Measurement tooling**:
  - Use `skills/pilot/phase2/dataset.jsonl`; run `make pilot-skills-phase2` for quick signal checks, or invoke `PYTHONPATH=src/mcprouter/src .venv/bin/python src/automation/scripts/analyze_skills_pilot.py --dataset skills/pilot/phase2/dataset.jsonl --top-k 3 --threshold 0.75 --skills-exec --output telemetry/reports/skills_phase2_<date>.json` to capture telemetry artifacts.
- **Execution window**:
  - Week 0: Enable `skills_exec` for pilot runs, run scripted test matrix (`tests/skills_exec_matrix.yaml`).
  - Week 1: Limited live usage (2–3 flows per day) with real-time monitoring.
  - Week 2: Retrospective; determine expansion to additional agents or rollback.
- **Success metrics**:
  - 0 critical guardrail escapes (no unapproved script execution).
  - 100% telemetry coverage for attempts and results (no missing events).
  - Operator task cycle time ≤ baseline ±10% (execution latency acceptable).
- **Safeguards**:
  - Rollback plan: Toggle `skills_exec=false`, purge cached scripts, notify #skills-adoption.
  - Dependency review: DepsSAG validates new runtime deps before enabling `skills_exec`.
  - Incident process: Escalate blockers to GovernanceSAG within 1 business day.

## Follow-ups

1. Publish pilot outcomes in `telemetry/reports/skills/` with summary dashboards.
2. Update `agents/SSOT.md` and `.mcp/SSOT.md` once pilots graduate to steady-state.
3. Archive temporary pilot notes in `archive/skills-migration/<date>/` after completion.
