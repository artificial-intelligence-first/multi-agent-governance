# ContextSAG Runbook

## Detection
- Context routing assigns briefs on the `context-engineering` channel to ContextSAG.
- Monitor `context_sag.latency_ms` and `context_sag.risk_count`; alerts trigger when latency exceeds 65s or risk count > 3 for three consecutive runs.

## Triage
1. Inspect the inbound brief. Confirm it includes at least one `context_inputs` entry and a valid `objective`.
2. Review constraints and evaluation criteria. If both are blank, expect ContextSAG to request follow-up information.
3. Validate upstream knowledge sources or retrieval indices referenced in the brief.

## Remediation
- **Missing context inputs:** Request additional artefacts from the operator; the agent returns a follow-up question prompting more material.
- **Stale context:** ContextSAG flags records without `last_updated` dates. Coordinate with KnowledgeMag to refresh the source.
- **Constraint conflicts:** If incompatible constraints are detected (e.g., “no customer data” alongside a CRM export), remove the offending input and rerun.

## Recovery
- Retry the job after curating the inputs and constraints.
- If repeated failures persist, switch routing to the manual handler defined in `agents/AGENT_REGISTRY.yaml` and log the incident in Ops tracker.
- Update this runbook after any major contract or workflow change.
