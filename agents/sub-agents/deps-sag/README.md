# DepsSAG Overview

DepsSAG governs dependency lifecycle management for the repository. Core duties include:

- Update coordination: monitor `pyproject.toml`, `requirements.txt`, `uv.lock`, and vendored packages for new releases and plan upgrade windows.
- Automation upkeep: maintain `uv lock --upgrade`, validation scripts, and ensure `make validate` remains green after dependency changes.
- Cross-agent collaboration: provide upgrade notes to DocsSAG, share change logs with GovernanceSAG, and brief WorkflowMAG/QAMAG on compatibility or rollout risks.
- Security response: watch pip/GitHub advisories and escalate urgent fixes through the governance workflow.

Supporting artefacts:
- `docs/` contains the living overview and upgrade runbook.
- `prompts/upgrade.prompt.yaml` orchestrates SOP-aware change plans.
- `workflows/upgrade_deps.wf.yaml` encodes the validation flow executed post-upgrade.
- `src/deps_sag/` exposes helpers (currently workflow loading) for automations.
- `tests/` verifies workflow assets stay loadable.

See `sop/` for preflight and execution checklists.
