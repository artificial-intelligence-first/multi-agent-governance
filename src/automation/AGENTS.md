# Automation Toolkit Guide

## Dev environment tips
- Work inside the repo venv (`source .venv/bin/activate`) so scripts share dependencies.
- Flow definitions in `flows/` expect Flow Runner to be installed via `make setup-flow-runner`.
- Keep scripts portable—prefer standard library modules and document any new dependencies in root `AGENTS.md`.

## Testing instructions
- Run individual scripts with `python src/automation/scripts/<name>.py --help` to confirm CLI behaviour.
- Use Flow Runner (`flowctl run`) on demo flows after editing them to ensure they still execute.
- If you add new automation, include unit tests or smoke checks and reference them here.

## Shared utilities
- `precheck` CLI — install (or refresh) with `uv tool install --editable .` so the command maps to `automation.compliance.pre:cli` and stays synced with the working tree; keep behaviour idempotent and document escalations in PLANS.md or task logs.
- `src/automation/scripts/cleanup_logs.py` — placeholder for telemetry log retention; update once deletion logic is implemented and note behaviour changes in governance records.
- Ensure any new automation entry points live under `src/automation`, remain safe for local invocation, and align with `/AGENTS.md` and `/SSOT.md` guidance.

## PR instructions
- Describe any new entry point (script or flow) in the PR summary and update this file when usage changes.
- When upgrading Flow Runner or mcprouter sources, capture upstream commit hashes in the PR description.
- Coordinate with agent owners if scripts start enforcing additional validations or metrics.
