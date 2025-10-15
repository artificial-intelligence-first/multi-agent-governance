# Automation Toolkit Guide

## Dev environment tips
- Work inside the repo venv (`source .venv/bin/activate`) so scripts share dependencies.
- Flow definitions in `flows/` expect Flow Runner to be installed via `make setup-flow-runner`.
- Keep scripts portable—prefer standard library modules and document any new dependencies in root `AGENTS.md`.

## Testing instructions
- Run individual scripts with `python src/automation/scripts/<name>.py --help` to confirm CLI behaviour.
- Use Flow Runner (`flowctl run`) on demo flows after editing them to ensure they still execute.
- If you add new automation, include unit tests or smoke checks and reference them here.

## PR instructions
- Describe any new entry point (script or flow) in the PR summary and update this file when usage changes.
- When upgrading Flow Runner or mcprouter sources, capture upstream commit hashes in the PR description.
- Coordinate with agent owners if scripts start enforcing additional validations or metrics.
