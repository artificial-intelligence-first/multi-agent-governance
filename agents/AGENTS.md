# Agents Directory Playbook

This tree contains every Multi Agent Governance agent plus shared contracts and prompts. Keep these instructions close to the latest implementation.

## Dev environment tips
- Run from the repo root after sourcing `.venv`; validators in `src/automation/scripts/` expect dependencies from the shared virtual environment.
- Use `python -m jsonschema` (installed via requirements) to validate contract changes before running the workflows.
- When editing prompts or workflows, keep relative paths short—agents resolve includes relative to their own directory.
- MCP tooling uses the root `.mcp/.mcp-config.yaml`; do not stash agent-specific copies. When an agent needs new MCP access, coordinate with MCPSAG, extend the shared config, and note it in `.mcp/AGENTS.md`.
- GitHub routing is available via the `github` provider—declare `GITHUB_TOKEN` (and optional `GITHUB_API_BASE` / `GITHUB_API_VERSION`) in `.mcp/.env.mcp`, note whether REST or GraphQL endpoints are required, and update the docs cascade before agents depend on it.

## Testing instructions
- Schema and workflow checks live in `make validate-*`; run them whenever you change prompts, SOPs, or contracts.
- Example pytest targets:
  - `python -m pytest agents/main-agents/knowledge-mag/tests`
  - `python -m pytest agents/sub-agents/docs-sag/tests`
  - `python -m pytest agents/sub-agents/prompt-sag/tests`
  - `python -m pytest agents/sub-agents/context-sag/tests`
- For contract updates, run the matching validator (`validate_knowledge.py`, `validate_docs_sag.py`, `validate_prompt_sag.py`, `validate_context_sag.py`) to ensure examples stay in sync.

## PR instructions
- Update the relevant agent documentation (README, docs/, sop/) whenever you add commands, dependencies, or SOP steps.
- Include example payload updates under `agents/contracts/examples/` when schemas change.
- Keep `agents/AGENT_REGISTRY.yaml` and `agents/SSOT.md` in sync with new routes, terminology, or observability metrics.
- Route MCP updates through MCPSAG so SOPs, checklists, and validation commands stay aligned; document changes across the AGENTS/SSOT cascade.
- Capture MCP routing changes alongside agent updates so Codex, Cursor, and Flow Runner continue to share the same configuration surface.

## Directory hints
- `main-agents/` – primary orchestrators (WorkFlowMAG, KnowledgeMag, OperationsMAG, QAMAG). See each subdirectory’s AGENTS.md for runtime instructions.
- `sub-agents/` – supporting specialists (DocsSAG, PromptSAG, ContextSAG, QualitySAG, ReferenceSAG, MCPSAG). See `agents/sub-agents/AGENTS.md` for detailed responsibilities.
- `contracts/` – JSON Schemas and examples; coordinate changes with validators and DocsSAG rules.
- `shared/` – prompt partials and shared tooling; keep naming consistent so prompts can include them reliably.
