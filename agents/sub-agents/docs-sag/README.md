# DocsSAG

DocsSAG is the documentation sub-agent that expands KnowledgeMag cards, editorial constraints, and routing requirements into publication-ready Markdown drafts. It focuses on the last-mile authoring work—filling in structured outlines, preserving provenance, and surfacing gaps so editors can approve and publish quickly.

## Responsibilities
- Transform knowledge cards plus document outlines into well-organised Markdown deliverables.
- Preserve SSOT terminology, policy guidance, and knowledge source identifiers supplied in the request payload.
- Surface incomplete sections, missing source material, or citation gaps via review notes and follow-up questions.
- Emit `docs_sag.*` diagnostics to feed observability dashboards and detect drafting regressions.

## Inputs
- Payloads that satisfy `agents/contracts/docs_sag_request.schema.json`, typically produced by KnowledgeMag or editorial tooling.
- Optional contextual metadata such as tone, constraints, release links, or associated knowledge cards to reference.

## Outputs
- `documentation_packet` entries conforming to `agents/contracts/docs_sag_response.schema.json` containing:
  - `document_markdown` — the assembled draft suitable for publication.
  - `sections` — structured summaries with action items and statuses for each requested heading.
  - `review_notes` and `follow_up_questions` — actionable alerts for editors.
- Markdown drafts are persisted under `docs/generated/` so that document creation, updates, and lifecycle management stay centralised in the repository-level `docs/` tree.

## Dependencies
- Shared prompt fragments under `agents/shared/prompts/partials/` (documentation guardrails plus style and safety guidance).
- KnowledgeMag outputs, which supply curated knowledge cards and provenance to enrich drafts.
- Schema validation and terminology checks powered by `src/automation/scripts/check_terminology.py`.
- Coordinates with QualitySAG and ReferenceSAG for interim quality and citation checks during WorkFlowMAG runs.

## Runbooks and SOPs
- `docs/overview.md` summarises the sub-agent’s scope, inputs, and routing.
- `docs/runbook.md` captures alerting, diagnosis, and mitigation procedures.
- `sop/README.md`, `sop/preflight.yaml`, and `sop/rollback.yaml` define operational readiness and recovery paths.

## Observability
- Emits `docs_sag.latency_ms`, `docs_sag.doc_type`, and `docs_sag.section_count` metrics in the diagnostics map.
- Logs generated drafts under `logs/agents/sub-agents/docs-sag/*.json` (configure in runtime harness).
- Integrates with Flow Runner workflows via `workflows/draft_docs.wf.yaml` for regression checks.
