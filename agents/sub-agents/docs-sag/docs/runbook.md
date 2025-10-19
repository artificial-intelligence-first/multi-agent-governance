# DocsSAG Runbook

> Quality review guidance for DocsSAG drafts now lives in `agents/sub-agents/docs-sag/skills/draft-quality/SKILL.md`; consult that Skill before escalating incidents.

## Detection
- Alert when `docs_sag.latency_ms` exceeds 45 seconds on the p95 over 10-minute windows.
- Trigger incident if schema validation failures for DocsSAG responses exceed 2% of runs within an hour.
- Monitor `docs_sag.section_count` histogram; sudden drops may indicate truncated drafts.
- Pager source: `alerts/docs-sag.yaml` routed to `#ops-ai`.

## Diagnosis
1. **Schema drift** – Validate failing payloads against `agents/contracts/docs_sag_request.schema.json` and `agents/contracts/docs_sag_response.schema.json`.
2. **Prompt regression** – Compare `prompts/draft.prompt.yaml` against prior versions to spot accidental guardrail removals.
3. **Knowledge mismatch** – Ensure the inbound knowledge packet aligns with requested sections; mismatches may come from KnowledgeMag regressions.
4. **Terminology violations** – Re-run `src/automation/scripts/check_terminology.py` with the captured payload to confirm SSOT alignment.

## Mitigation
- Execute `workflows/draft_docs.wf.yaml` with the failing artifact to reproduce the issue.
- Restore prompts or workflows from the last known good commit if guardrails drifted.
- Temporarily reroute `documentation` traffic to the manual documentation queue defined in `AGENT_REGISTRY.yaml` until DocsSAG recovers.
- Communicate impact and ETA in `#ops-ai`, attaching relevant diagnostics and draft excerpts.

## Recovery
- Verify fixes by running targeted tests under `agents/sub-agents/docs-sag/tests/` and the draft workflow.
- Update `sop/preflight.yaml` and `sop/rollback.yaml` statuses after validating the runbook steps.
- Capture a post-incident summary within 24 hours, including discovered root cause, mitigations, and preventive actions.
