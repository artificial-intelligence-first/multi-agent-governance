# ContextSAG SOP

## Preflight
- Confirm the incoming brief references `context_sag_request.schema.json` version 1.x.
- Ensure at least one context input includes provenance (`source` or `last_updated`).
- Run `make validate-context` to catch missing assets or stale examples.

## Rollback
- If ContextSAG fails repeatedly, route the task to `manual-handlers/manual-context:triage`.
- Notify Ops and revert to the previous context package template stored in `docs/reference/engineering/context/`.
- Capture incident details and update this SOP with remediation steps.
