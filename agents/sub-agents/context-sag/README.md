# ContextSAG

ContextSAG curates, prioritises, and packages context bundles for Multi Agent System agents. It receives context-engineering briefs, scores incoming artefacts, and returns an assembly plan with packaging guidelines, risk flags, and follow-up questions. The runtime lives under `agents/sub-agents/context-sag/src/context_sag/`.

## Responsibilities
- Normalise context-engineering briefs into a consistent structure with prioritised context blocks.
- Recommend packaging and truncation strategies for downstream prompts (e.g., multi-document, retrieval, memory).
- Surface risk flags (staleness, missing provenance, conflicting constraints) and gather follow-up questions for operators.

## Inputs
- Context briefs conforming to `context_sag_request.schema.json`, including the task objective, primary use case, target models, and context inputs with metadata.
- Optional constraints, evaluation checks, and audience annotations to steer assembly decisions.

## Outputs
- Structured response matching `context_sag_response.schema.json`, containing:
  - `context_briefs`: prioritised entries with inclusion guidance and recommended actions.
  - `assembly_plan`: ordered steps for packaging, plus checklist items for rollout.
  - `risk_register` and `follow_up_questions` to highlight gaps or ambiguities.
  - Diagnostics with latency, confidence, and summary metrics.

## Observability
- Emits metrics under the `context_sag.*` namespace (latency, context count, risk count).
- Confidence scores drop when inputs lack provenance or when follow-up questions are raised.

## Runbooks and SOPs
- `docs/overview.md` and `docs/runbook.md` cover high-level behaviour, hand-offs, and recovery steps.
- SOP assets live in `sop/` for preflight, rollback, and operational checklists.
- Feeds WorkFlowMAG with prioritised bundles and flags risks for QAMAG/OperationsMAG review.
