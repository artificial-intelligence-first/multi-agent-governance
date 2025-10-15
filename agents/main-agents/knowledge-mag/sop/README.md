# KnowledgeMag SOP

## Purpose
Maintain KnowledgeMag as a reliable curator of fleet knowledge, ensuring collections highlight intents, dependencies, and outstanding gaps for downstream consumers.

## Checklists
- Confirm `prompts/curate.prompt.yaml` references knowledge, style, and safety guardrail partials.
- Keep schema examples under `agents/contracts/examples/knowledge/` aligned with real workloads.
- Run `workflows/curate_knowledge.wf.yaml` before promoting prompt or workflow updates.
- Review observability dashboards weekly for `knowledge.latency_ms`, `knowledge.topic_count`, and `knowledge.source_count`.

## Related Documents
- `sop/preflight.yaml`
- `sop/rollback.yaml`
- `agents/main-agents/knowledge-mag/docs/runbook.md`
