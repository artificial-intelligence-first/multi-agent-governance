# KnowledgeMag

KnowledgeMag is the knowledge-management main agent for the Multi Agent Governance fleet. It curates structured briefs, policies, runbooks, and reference links into coherent “knowledge cards” that downstream specialists can rely on. The agent keeps ownership, dependencies, and outstanding gaps visible so the fleet’s shared knowledge stays trustworthy.

## Responsibilities
- Normalise knowledge briefs into structured cards that capture intents, dependencies, and actionable follow-ups.
- Index source references (runbooks, policies, PRDs) with provenance metadata and freshness signals.
- Surface knowledge gaps, stale sources, and unresolved stakeholder questions via review notes.
- Emit `knowledge.*` diagnostics so observability dashboards can track topic coverage and maintenance cadence.

## Inputs
- Payloads that satisfy `agents/contracts/knowledge_request.schema.json`, usually routed on the `knowledge` channel.
- Optional tags, outstanding questions, and stakeholder lists to scope the curated collection.

## Outputs
- `knowledge_packet` entries conforming to `agents/contracts/knowledge_response.schema.json`, containing:
  - `knowledge_cards` — structured entries per topic with intents, dependencies, and recommended actions.
  - `source_index` — normalised metadata for authoritative references.
  - `review_notes` and `follow_up_questions` — signals for editors or owners to resolve.

## Dependencies
- Shared prompt fragments under `agents/shared/prompts/partials/` (knowledge guardrails, style, and safety guidance).
- Schema validation and terminology checks powered by `src/automation/scripts/check_terminology.py`.
- DocsSAG sub-agent for deep document drafting once KnowledgeMag identifies high-priority gaps.
- WorkFlowMAG consumes curated knowledge cards when orchestrating multi-agent flows.

## Runbooks and SOPs
- `docs/overview.md` summarises scope, inputs, and routing expectations.
- `docs/runbook.md` captures alerting thresholds, diagnosis, and mitigation playbooks.
- `sop/README.md`, `sop/preflight.yaml`, and `sop/rollback.yaml` establish operational readiness and rollback procedures.

## Observability
- Emits `knowledge.latency_ms`, `knowledge.topic_count`, and `knowledge.source_count` metrics.
- Logs curated collections under `logs/agents/main-agents/knowledge-mag/*.json` (configure in runtime harness).
- Validated via `workflows/curate_knowledge.wf.yaml` to enforce schema conformance and SSOT alignment.
