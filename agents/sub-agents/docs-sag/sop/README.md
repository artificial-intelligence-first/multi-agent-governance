# DocsSAG SOP

## Purpose
Maintain DocsSAG as a reliable documentation drafter that converts knowledge cards into publication-ready Markdown while signalling gaps for human editors.

## Checklists
- Confirm `prompts/draft.prompt.yaml` references the shared documentation, style, and safety guardrails.
- Keep schema examples under `agents/contracts/examples/docs-sag/` aligned with real-world payloads.
- Run `workflows/draft_docs.wf.yaml` before promoting prompt or workflow updates.
- Review observability dashboards weekly for `docs_sag.latency_ms` and schema failure trends.

## Related Documents
- `sop/preflight.yaml`
- `sop/rollback.yaml`
- `agents/sub-agents/docs-sag/docs/runbook.md`
