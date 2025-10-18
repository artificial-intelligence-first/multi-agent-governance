# AGENTS — `telemetry`

## Mission
- Centralise run logs, validation output, and compliance artefacts so every agent can audit behaviour without pulling ad‑hoc files.
- Keep retention policies, schema contracts, and dashboards consistent with the governance SSOT.

## Subdirectories
- `logs/` — raw runtime logs grouped by domain (`context`, `prompt`, `ops`, etc.); keep `.gitkeep` files so the tree survives clean clones.
- `runs/` — flow execution folders (`<run_id>/summary.json`, `steps/*.json`, artefacts).
- `reports/` — aggregated telemetry reports (dashboards, scorecards, notebooks) that downstream reviewers consume.
- `validation/` — outputs from `make validate` and targeted pytest suites.
- `agent_usage/` — statistics exported by routing and usage auditors.
- `schemas/` — JSON Schemas backing telemetry payloads.
- Retention tooling lives under `src/automation/scripts/` (e.g., `cleanup_logs.py` handles log pruning); keep this directory focused on telemetry artefacts only.
- `snapshots/` — dated snapshots for migrations or audits. Treat everything under here as read-only.

## Operating Notes
- Before rerouting telemetry, update this file, `telemetry/SSOT.md`, and the relevant schema so OpsMAG and QAMAG stay aligned.
- When you introduce a new report type, add a README or index entry and ensure validators cover the file shape.
- Retention or redaction policy changes must land in `telemetry/SSOT.md` and the automation script that enforces them.

## References
1. [[SSOT]]
2. [[telemetry/SSOT]]
3. `docs/reference/files/PLANS.md/OpenAI.md` — ExecPlan logging requirements.
4. `docs/reference/agents/sdk/agents-sdk/OpenAI.md` — context for telemetry emitted by Codex-driven agents.
