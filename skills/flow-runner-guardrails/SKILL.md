---
name: flow-runner-guardrails
description: >
  Use when maintaining Flow Runner skills execution guardrails: manage skills_exec feature flags, allowlist hashes, sandbox expectations, and telemetry for approved scripts.
---

# Flow Runner Guardrails Skill

> Apply this Skill whenever a Skills execution request needs review. It consolidates the deny-by-default policy, allowlist workflow, and telemetry requirements so Flow Runner remains safe during the Phase 2 pilot and beyond.

## Quick start
- Confirm `skills_exec=true` is only enabled in the target staging workspace and feature flags are tracked in `PLANS.md`.
- Retrieve the script path, expected sha256, and argument pattern from the change request; verify against `skills/ALLOWLIST.txt`.
- Recompute the fingerprint with `shasum -a 256 <script>` (or `python -m hashlib` for cross-platform) and compare with the proposed allowlist entry.
- Validate sandbox expectations (read/write paths, network access) and ensure documentation appears in the Skill body before approving execution.
- Run `python -m pytest src/flowrunner/tests/test_skills_guard.py -k allowlist` locally to confirm guard enforcement still passes.
- Capture approvals and telemetry snapshot references in `collab/skills-adoption/notes.md` or the relevant change log.

## Guardrail checklist
- Feature flags
  - [ ] `skills_v1` enabled; `skills_exec` scoped to pilot cohorts only.
  - [ ] Rollback plan documented (toggle flags, clear caches, disable Skill).
- Allowlist hygiene
  - [ ] Script path recorded with forward-slash separators and relative to repo root.
  - [ ] sha256 fingerprint recomputed from the committed version of the script.
  - [ ] Argument pattern restricts inputs to expected values; rejects wildcards by default.
- Telemetry
  - [ ] `skill_exec_attempt`/`skill_exec_result` events emitted with script, outcome, and guard status.
  - [ ] Blocked attempts captured with reason codes (`missing_allowlist_entry`, `hash_mismatch`, etc.).
  - [ ] Reports exported to `telemetry/reports/skills_phase2_<date>.json` during the pilot.
- Governance
  - [ ] GovernanceSAG approves execution scope and incident response steps.
  - [ ] DepsSAG reviews new runtime dependencies if the script adds packages or binaries.
  - [ ] SecuritySAG notified when scripts handle secrets or privileged tokens.

## Telemetry & validation
- `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"` — confirm router feature flags and metadata alignment.
- `PYTHONPATH=src/mcprouter/src .venv/bin/python src/automation/scripts/analyze_skills_pilot.py --dataset skills/pilot/phase2/dataset.jsonl --top-k 3 --threshold 0.75 --skills-exec` — reuse the analyzer to verify allow_exec signalling for Phase 2 datasets.
- `python -m pytest src/flowrunner/tests/test_skills_guard.py -k skills_exec` — regression tests for the guard logic.

## Resources
- [`../../src/flowrunner/src/flow_runner/skills_guard.py`](../../src/flowrunner/src/flow_runner/skills_guard.py) — authoritative guard implementation.
- [`../../src/automation/scripts/validate_skills.py`](../../src/automation/scripts/validate_skills.py) — lint to ensure allowlist entries and Skill metadata stay consistent.
- [`../../telemetry/skills/events.schema.json`](../../telemetry/skills/events.schema.json) — schema for execution telemetry; update when new fields are added.
- [`../ALLOWLIST.txt`](../ALLOWLIST.txt) — single source of truth for approved scripts and fingerprints.

## Script usage
- `scripts/report_guardrails.py` — emits a JSON snapshot of allowlist entries; optionally pass `--output` to persist the report. Execution is approved via `skills/ALLOWLIST.txt`.
- Additional automation is allowed once hashes appear in `skills/ALLOWLIST.txt` and the pilot cohort has `skills_exec=true`. Document each approval in `agents/SSOT.md` and the Skills Decision Log.
