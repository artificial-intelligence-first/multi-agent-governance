# Automation Assets

This directory aggregates operational assets that support the Multi Agent Governance fleet.

- `flows/` — YAML definitions executed by Flow Runner (e.g., demos, smoke tests, CI regressions).
- `scripts/` — Python/Bash utilities for validation, setup, notifications, and registry maintenance (e.g., `cleanup_logs.py` for telemetry retention work in progress). The `precheck` CLI is exposed via `automation.compliance.pre`; install it with `uv tool install --editable .` so updates track the working tree.

All repository references assume these automation assets live under `src/automation/`. Keep new tooling here so the project root stays trim.

To run Flow Runner, execute `make setup-flow-runner` at the repository root and then invoke `flowctl run src/automation/flows/<name>.yaml`. The vendored Flow Runner packages live under `src/flowrunner/` and `src/mcprouter/` and are installed into the Python user site (`python -m site --user-base`). Make sure that bin directory is on your `PATH`.
