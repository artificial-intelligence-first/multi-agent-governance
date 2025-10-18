# DepsSAG Playbook

## Role
- Own dependency lifecycle management across Python projects, locks, and build tooling.
- Coordinate update windows with downstream agents so CI, docs, and prompts stay in sync.

## Responsibilities
- Monitor upstream releases for `pyproject.toml`, `requirements.txt`, and `uv.lock` plus vendored packages under `src/`.
- Run the dependency upgrade SOP, regenerate locks via `uv`, and capture change notes for GovernanceSAG and DocsSAG.
- Flag breaking changes or security advisories to WorkflowMAG/QAMAG before merge.
- Keep compatibility guidance (Python baseline, tooling versions) current in AGENTS cascade and SSOT artefacts.

## SOP Index
- `sop/preflight.yaml` — environment checks before starting an upgrade.
- `sop/upgrade.yaml` — canonical checklist for bumping dependencies and locks.
- `sop/rollback.yaml` — remediation steps when an upgrade must be reverted or postponed.

## Artefact map
- `docs/` — overview and runbook content for downstream agents.
- `prompts/upgrade.prompt.yaml` — orchestration prompt that plans upgrade executions.
- `workflows/upgrade_deps.wf.yaml` — validation flow executed after lock regeneration.
- `src/deps_sag/` — helper utilities for loading workflow definitions.
- `tests/` — smoke tests that ensure workflow assets stay loadable.
