# PromptSAG Overview

PromptSAG converts requirements and guardrails into production-ready prompt packages. It aligns with WorkFlowMAG for orchestration and DocsSAG for documentation drafting so AI tooling receives precise, policy-compliant instructions.

## Scope
- Works on prompt engineering requests for Codex, Claude, Gemini, and other agents supported in `docs/reference/`.
- Outputs structured messages, evaluation checklists, and follow-up questions.
- Highlights missing context or risky operations before automation proceeds.

## Workflow
1. Validate the incoming payload against `prompt_sag_request.schema.json`.
2. Load shared guardrails from `agents/shared/prompts/partials/`.
3. Compose system/user examples; attach verification steps.
4. Emit diagnostics and persist the resulting prompt packet.

## Routing
- Proposed route key: `prompt-engineering` (see `agents/AGENT_REGISTRY.yaml`).
- Backup handler: manual prompt engineers (operator triage) if automation fails.

## Observability
- Metrics: `prompt_sag.latency_ms`, `prompt_sag.prompt_count`, `prompt_sag.review_flag`.
- Logs: store JSON traces under `logs/agents/sub-agents/prompt-sag/` (configure in runtime harness).
