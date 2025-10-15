# Sub-Agents Playbook

## Dev environment tips
- Work from the repository venv; DocsSAG and other scripts assume Python tooling is installed there.
- Follow the same scaffold as DocsSAG when introducing a new sub-agent (README, docs, prompts, workflows, sop, tests, AGENTS.md).
- Keep shared prompt partials referenced via relative paths (`../../shared/...`) to avoid import issues.

## Testing instructions
- DocsSAG: `python -m pytest agents/sub-agents/docs-sag/tests/test_agent.py` plus `make validate-docs-sag`.
- PromptSAG: `python -m pytest agents/sub-agents/prompt-sag/tests/test_agent.py` plus `make validate-prompt`.
- ContextSAG: `python -m pytest agents/sub-agents/context-sag/tests/test_agent.py` plus `make validate-context`.
- Add agent-specific validators under `src/automation/scripts/` when new schemas or assets are introduced.

## PR instructions
- Document new observability metrics and routes in `agents/AGENT_REGISTRY.yaml`.
- Update `agents/SSOT.md` when sub-agents add terminology or contract changes.
- Ensure DocsSAG persists drafts to `docs/generated/` and PromptSAG references the latest material under `docs/reference/`.
- When replacing the sample sub-agent, remove placeholder prompts and update this file to describe the real implementation.

## Directory hints
- `docs-sag/` – documentation drafting specialist.
- `prompt-sag/` – prompt engineering specialist.
- `context-sag/` – context engineering specialist that curates and packages context bundles.
- `quality-sag/` – ExecPlan and interim quality auditor.
- `reference-sag/` – reference and citation auditor.
