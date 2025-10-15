# KnowledgeMag Specification

## Goal
Introduce KnowledgeMag, a knowledge-management main agent that curates structured briefs, policies, and reference links into governed knowledge collections while exposing ownership gaps and stale content.

## Requirements
- Create `agents/main-agents/knowledge-mag/` with README, prompts, workflows, SOPs, docs, and tests mirroring existing agent scaffolds.
- Define `agents/contracts/knowledge_request.schema.json` and `agents/contracts/knowledge_response.schema.json` plus representative examples under `agents/contracts/examples/knowledge/`.
- Implement a runtime agent exposed via `knowledge_mag.agent.KnowledgeMag` that produces knowledge cards, source indices, and reliability signals.
- Add a Flow Runner workflow (`curate_knowledge.wf.yaml`) and automation script (`validate_knowledge.py`) to validate curated outputs.
- Register a `knowledge` route in `agents/AGENT_REGISTRY.yaml` and update SSOT terminology and fleet documentation accordingly.

## Acceptance Criteria
- `make validate-knowledge` succeeds locally and in CI.
- KnowledgeMag request/response examples validate against the new schemas.
- Agent registry and SSOT entries reference KnowledgeMag terminology and routing.
- KnowledgeMag tests under `agents/main-agents/knowledge-mag/tests/` pass and assert key behaviours (card construction, gap surfacing, diagnostics).
- Documentation (overview, runbook, SOP) describe operations, routing, and observability expectations.

## Risks & Mitigations
- **Stale knowledge** → Mitigated by requiring `last_reviewed` metadata and emitting review notes when absent.
- **Incomplete topic coverage** → Mitigated by enforcing dependency and outstanding question follow-ups.
- **Terminology drift** → Mitigated via SSOT-aligned terminology checks in the workflow.
- **Prompt regressions** → Guarded through shared knowledge prompt partials and workflow validation.

## Links
- `agents/main-agents/knowledge-mag/`
- `agents/contracts/knowledge_request.schema.json`
- `agents/contracts/knowledge_response.schema.json`
- `agents/AGENT_REGISTRY.yaml`
- `agents/SSOT.md`
