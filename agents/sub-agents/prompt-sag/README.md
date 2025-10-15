# PromptSAG

PromptSAG is the prompt-engineering specialist for the Multi Agent System fleet. It transforms high-level tasks, reference material, and project guardrails into executable prompts that upstream or downstream agents can reuse.

## Responsibilities
- Extract goals, constraints, and safety requirements from source material (tickets, AGENTS.md excerpts, reference notes).
- Produce structured prompt packages (system/user messages, examples, guardrails) ready for Codex/Claude/Gemini usage.
- Recommend verification steps and tooling alignment (tests, linting, telemetry) for the target runtime.
- Surface gaps, ambiguities, or policy conflicts that need human clarification before automation proceeds.

## Inputs
- Payloads conforming to `agents/contracts/prompt_sag_request.schema.json` (to be introduced alongside this agent).
- Reference documents under `docs/reference/` and existing AGENTS instructions.
- Optional attachments such as logs, prior prompt attempts, or workflow diagrams.

## Outputs
- `prompt_packet` entries matching `agents/contracts/prompt_sag_response.schema.json`, containing structured messages, rationale notes, evaluation guidance, and safety warnings.

## Dependencies
- Shared prompt partials under `agents/shared/prompts/partials/`.
- Validation scripts in `src/automation/scripts/` (added with this implementation) to ensure schema and terminology compliance.
- Downstream consumers: WorkFlowMAG, DocsSAG, and ContextSAG.
- Orchestrated by WorkFlowMAG; findings are reviewed by QAMAG before deployment.

## Observability
- Emits `prompt_sag.latency_ms`, `prompt_sag.prompt_count`, and `prompt_sag.review_flag` metrics via diagnostics.
