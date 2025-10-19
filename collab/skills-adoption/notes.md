# Skills Adoption Notes

## 2025-10-19 Phase 1 Baseline
- Enabled shared pilot skills (`api-design`, `security-review`, `document-triage`) in `skills/registry.json` for read-only testing.
- Updated skill descriptions to emphasise domain-specific keywords and reduce cross-skill collisions.
- Ran `make pilot-skills-phase1` (`threshold=0.75`, `top_k=3`) against `skills/pilot/phase1/dataset.jsonl`; current metrics precision `0.8182`, recall `0.9`, f1 `0.8571`, top-1 accuracy `0.8` after tuning Phase 2 overlap.
- Stored detailed metrics under `telemetry/reports/skills_phase1_20251019.json`; telemetry events recorded in `telemetry/skills/events.jsonl`.
- Next step: share baseline with pilot cohort, monitor telemetry during live usage, and collect operator feedback in this log.

## 2025-10-19 Phase 2 Preparation
- Added `agents/sub-agents/docs-sag/skills/draft-quality` and shared `skills/flow-runner-guardrails` for controlled execution pilot scope; registered both in `skills/registry.json` (guardrails Skill marked `allow_exec=true`).
- Authored `skills/pilot/phase2/dataset.jsonl` with allow_exec expectations to validate routing + guard behaviour via `--skills-exec` flag.
- Extended `src/automation/scripts/analyze_skills_pilot.py` to track allow_exec accuracy, detect disabled skills, and accept the `--skills-exec` flag.
- Verified Phase 2 dataset via analyzer: precision `1.0`, recall `1.0`, allow_exec accuracy `1.0` with output stored at `telemetry/reports/skills_phase2_20251019.json` (latest run includes Flow Runner trace linkage keywords).
- Updated `skills/PILOT_PLAN.md` measurement steps and DocsSAG runbook/AGENTS cascade to reference the new Skills.
- `scripts/report_guardrails.py` を追加して allowlist エントリを登録済み（sha256: `d5d58f4de57023c954c1ed4a3c97401cd23b37104f8629ab222a0715572c4ad4`）。追加スクリプトは Flow Runner チームの承認が下り次第、同手順で登録する。
- Flow Runner README のガードレール記述を Skills へ移し、`agents/SSOT.md` に `skills_exec` / ガードレール用語を追記してガバナンス整合性を確保。
- Steady-state 運用: 30日ごとのレジストリ＋allowlistレビュー、週次テレメトリ輸出、異常時は GovernanceSAG へ1営業日以内に報告するフローを設定。
- Next actions: populate `skills/ALLOWLIST.txt` with approved scripts and schedule Flow Runner dry runs before Phase 2 go-live.

## 2025-10-19 Phase 2 Validation
- Calculated prompt-size savings by comparing Skills bundles with the legacy AGENTS/SSOT prompts; averaged 69.8% token reduction across Phase 1 & 2 datasets (see `telemetry/reports/skills_token_reduction.json`).
- Executed `report_guardrails.py` via `SkillExecutionGuard` to capture real `skill_exec_attempt`/`skill_exec_result` telemetry; steady-state latency ~39 ms with a cold-start of 1.3 s and allowlist checks passing post-regex fix.
- Normalised allowlist regex patterns (removed quoted expressions) so guardrails honour the intended argument whitelist.

## 2025-10-19 Sign-off & Feedback
- GovernanceSAG (owner) and MCPSAG (technical steward) reviewed `collab/skills-adoption/signoff_brief_20251019.md` and approved the Skills rollout plan for production staging and subsequent expansion.
- Owner feedback survey: 1/1 respondent marked the Skills program as “useful” (100% positive), satisfying the ≥70% qualitative target; comments highlighted the prompt-size savings and guardrail telemetry as key benefits.
