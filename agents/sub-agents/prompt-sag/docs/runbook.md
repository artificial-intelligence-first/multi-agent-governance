# PromptSAG Runbook

Use this runbook when PromptSAG encounters incidents or requires maintenance.

## Detection
- CI failures in `make validate-prompt` or `python src/automation/scripts/validate_prompt_sag.py`.
- Elevated `prompt_sag.review_flag` counts in diagnostics.
- Missing or malformed prompt packets in downstream automation.

## Triage
1. Inspect the most recent request/response pair in `telemetry/runs/<RUN_ID>/`.
2. Re-run the validator locally to reproduce the failure.
3. Check shared partials and reference docs for missing updates.

## Mitigation
- Patch prompt templates, guardrails, or validation logic as required.
- If automation cannot safely continue, route to manual prompt engineers (see AGENT_REGISTRY backup).
- Communicate status in the ops channel and log the incident.

## Recovery
- Once fixes land, run `make validate-prompt` and targeted pytest suites.
- Confirm diagnostics metrics return to baseline.
- Update `docs/reference/` entries if new best practices emerged.
