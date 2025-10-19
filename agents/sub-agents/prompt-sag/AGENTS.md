# PromptSAG Playbook

## Role
- Engineer structured prompt packages (system/user messages, examples, guardrails) from task briefs, references, and policy constraints.

## Responsibilities
- Consume requests conforming to `agents/contracts/prompt_sag_request.schema.json` and emit `prompt_sag_response` payloads with prompts, rationale, verification guidance, and safety notes.
- Align prompt packaging with downstream runtimes (Codex CLI, Flow Runner, external LLMs) and highlight missing context or conflicting requirements.
- Coordinate with DocsSAG, ContextSAG, and QAMAG to validate coverage, tone, and safety.

## SOP Index
- `docs/overview.md` — scope, routing, and collaboration guidance.
- `docs/runbook.md` — engineering workflow, diagnostics, and escalation paths.
- `sop/preflight.yaml` / `sop/rollback.yaml` — operational readiness and recovery steps.
