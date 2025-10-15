# Main Agents Playbook

Primary orchestrators live here. Keep these notes in sync with the active main agents (WorkFlowMAG, KnowledgeMag, OperationsMAG, QAMAG).

## Dev environment tips
- Work from the repo root with `.venv` activated so validators and pytest pick up packages.
- Shared prompt partials resolve via relative paths such as `../../shared/prompts/partials`; verify includes after moving files.
- When adding a new main agent, copy an existing directory (e.g., WorkFlowMAG or KnowledgeMag) and adjust the metadata immediately.

## Testing instructions
- KnowledgeMag: `python -m pytest agents/main-agents/knowledge-mag/tests`
- WorkFlowMAG: `python -m pytest agents/main-agents/workflow-mag/tests`
- OperationsMAG: `python -m pytest agents/main-agents/operations-mag/tests`
- QAMAG: `python -m pytest agents/main-agents/qa-mag/tests`
- Run the matching validators (`make validate-knowledge`, `make validate-workflow`, etc.) after schema, prompt, or workflow edits.
- If you modify Flow Runner workflows under `workflows/`, run the automation demos in `src/automation/flows/`.

## PR instructions
- Update route metadata in `agents/AGENT_REGISTRY.yaml` when behaviour or SLAs change.
- Refresh SOPs (`sop/`), docs (`docs/`), and this AGENTS file when procedures or runbooks evolve.
- For new dependencies (providers, APIs), document environment variables and add checks to the relevant validator script.

## Directory hints
- `knowledge-mag/` – knowledge curation agent.
- `workflow-mag/` – orchestration and planning agent.
- `operations-mag/` – observability and telemetry agent.
- `qa-mag/` – quality assurance gatekeeper.
- Future main agents should mimic this layout to keep automation consistent.
