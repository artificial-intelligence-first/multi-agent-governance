# KnowledgeMag Runbook

## Detection
- Alert when `knowledge.latency_ms` exceeds 45 seconds at p95 over 10-minute windows.
- Trigger incident if schema validation failures for knowledge responses exceed 2% of runs within an hour.
- Monitor `knowledge.topic_count` histogram; unexpected drops may indicate truncated collections.
- Pager source: `alerts/knowledge-mag.yaml` routed to `#ops-ai`.

## Diagnosis
1. **Schema drift** – Validate failing payloads against `agents/contracts/knowledge_request.schema.json` and `agents/contracts/knowledge_response.schema.json`.
2. **Prompt regression** – Compare `prompts/curate.prompt.yaml` against prior revisions for missing guardrails.
3. **Source freshness gaps** – Inspect incoming payloads for missing `last_reviewed` metadata or stale knowledge sources.
4. **Dependency coverage** – Ensure dependent topics referenced by knowledge cards are present in the request or scheduled for DocsSAG follow-up.

## Mitigation
- Execute `workflows/curate_knowledge.wf.yaml` with the failing artifact to reproduce the issue.
- Restore prompt or workflow files from the last known good commit if guardrails drifted.
- Temporarily reroute `knowledge` traffic to the manual knowledge custodians defined in `AGENT_REGISTRY.yaml` if automated curation is impaired.
- Communicate impact and mitigation steps in `#ops-ai`, attaching diagnostics and knowledge packet excerpts.

## Recovery
- Verify fixes by running targeted tests under `agents/main-agents/knowledge-mag/tests/` plus the knowledge workflow.
- Update `sop/preflight.yaml` and `sop/rollback.yaml` once mitigation steps are confirmed.
- Capture a post-incident summary within 24 hours, highlighting root cause, remedial actions, and follow-up owners.
