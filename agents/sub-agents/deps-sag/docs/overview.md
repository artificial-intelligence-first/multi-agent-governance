# DepsSAG Overview

DepsSAG manages dependency lifecycles for the Multi Agent Governance stack. The agent aligns package baselines with supported runtime versions, regenerates lockfiles, and coordinates rollout communications so downstream automation stays stable.

## Capabilities
- Tracks upstream releases for Python packages referenced by `requirements.txt`, `pyproject.toml`, and vendored projects under `src/`.
- Plans upgrade windows with DocsSAG and GovernanceSAG, ensuring documentation and SSOT artefacts update in lock step.
- Executes validation drills (`make validate`, targeted pytest suites, schema validators) after each dependency change.
- Publishes upgrade digests for GovernanceSAG so the fleet capture change history.

## Routing
- Primary route key: `dependencies` (see `agents/AGENT_REGISTRY.yaml`).
- Falls back to GovernanceSAG if change impact or compliance risk exceeds DepsSAG’s remit.

## Lifecycle
1. Run the preflight SOP to capture inventories, outstanding advisories, and pending MCPSAG updates.
2. Execute the upgrade workflow, regenerating locks with documented constraints and emulator checks.
3. Validate changes via `make validate`, targeted pytest runs, and automation scripts under `src/automation/`.
4. Emit upgrade notes and observability breadcrumbs before handing back to GovernanceSAG.
