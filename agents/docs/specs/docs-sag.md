# DocsSAG Specification

## Goal
Introduce DocsSAG, a documentation drafting sub-agent that converts KnowledgeMag outputs and editorial constraints into publication-ready Markdown drafts while surfacing outstanding gaps for editors.

## Requirements
- Create `agents/sub-agents/docs-sag/` with README, prompts, workflows, SOPs, docs, and tests mirroring the sub-agent scaffold.
- Define `agents/contracts/docs_sag_request.schema.json` and `agents/contracts/docs_sag_response.schema.json` plus representative examples under `agents/contracts/examples/docs-sag/`.
- Implement a runtime sub-agent exposed via `docs_sag.agent.DocsSAG` that produces Markdown drafts, structured section metadata, review notes, and follow-up questions.
- Add a Flow Runner workflow (`draft_docs.wf.yaml`) and automation script (`validate_docs_sag.py`) to validate drafting outputs.
- Update the agent registry and SSOT entries to register the `documentation` route for DocsSAG and describe its dependencies on KnowledgeMag.

## Acceptance Criteria
- `make validate-docs-sag` succeeds locally and in CI.
- DocsSAG request/response examples validate against the new schemas.
- Agent registry and SSOT entries reference DocsSAG terminology, routing, and observability metrics.
- DocsSAG unit tests under `agents/sub-agents/docs-sag/tests/` assert Markdown generation, knowledge reference propagation, and diagnostics.
- Documentation (overview, runbook, SOP) describes operations, routing, and observability expectations.

## Risks & Mitigations
- **Knowledge drift** → Mitigated by preserving knowledge references in section metadata and highlighting gaps in review notes.
- **Terminology misalignment** → Mitigated via SSOT-aligned terminology checks in the drafting workflow.
- **Prompt regressions** → Guarded through shared documentation prompt partials and automated workflow validation.
- **Schema mismatches** → Controlled by versioned schemas and example validation in CI.

## Links
- `agents/sub-agents/docs-sag/`
- `agents/contracts/docs_sag_request.schema.json`
- `agents/contracts/docs_sag_response.schema.json`
- `agents/AGENT_REGISTRY.yaml`
- `agents/SSOT.md`
