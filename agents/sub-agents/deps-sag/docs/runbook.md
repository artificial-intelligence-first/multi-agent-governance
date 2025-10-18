# DepsSAG Upgrade Runbook

## Preflight
1. Activate the repository venv (`python3 -m venv .venv && source .venv/bin/activate`).
2. Review open advisories and pending change requests in `agents/SSOT.md`.
3. Export current dependency graph: `uv tree --frozen > telemetry/deps-sag/baseline.txt`.
4. Run `make validate` to confirm the baseline is green before touching requirements.

## Execution
1. Follow `sop/preflight.yaml` and `sop/upgrade.yaml` to select candidate updates.
2. Apply version bumps in `requirements.txt`, `pyproject.toml`, and relevant agent metadata.
3. Regenerate locks with `uv lock --exclude-newer YYYY-MM-DD` and rerun any project-specific `uv lock --project …`.
4. Execute validation suites:
   - `make validate`
   - `python -m pytest agents/sub-agents/**/tests -k dependencies`
   - Targeted automation scripts under `src/automation/scripts/`.

## Post-Upgrade
1. Capture release notes for GovernanceSAG and DocsSAG, updating `agents/SSOT.md` and `AGENT_REGISTRY.yaml`.
2. Update `CHANGELOG.md` (Keep a Changelog format) if user-facing workflows change.
3. Hand off the summary deck to GovernanceSAG and close out the SOP checklist.
