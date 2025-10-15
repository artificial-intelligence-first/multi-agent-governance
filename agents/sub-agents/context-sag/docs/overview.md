# ContextSAG Overview

ContextSAG is the Multi Agent System sub-agent responsible for context engineering. It transforms raw context briefs into prioritised context bundles and packaging guidelines so downstream agents can operate within token limits and policy guardrails.

## Key capabilities
- **Prioritisation:** Scores each context input according to declared importance, freshness, and constraint alignment.
- **Assembly planning:** Recommends how to combine background material, knowledge cards, and live signals (multi-document prompt, retrieval index, memory store) with sequencing instructions.
- **Risk surfacing:** Flags stale sources, missing provenance, conflicting constraints, or evaluation gaps, and produces follow-up questions.

## Interface
- **Request contract:** `agents/contracts/context_sag_request.schema.json`
- **Response contract:** `agents/contracts/context_sag_response.schema.json`
- **Primary entrypoint:** `context_sag.agent.ContextSAG.run`

## Dependencies
- Reads reference guidance from `docs/reference/engineering/context/`.
- Shares terminology with PromptSAG and DocsSAG via `agents/SSOT.md` glossary entries.
- Measured via `context_sag.latency_ms`, `context_sag.context_count`, and `context_sag.risk_count`.
