# Agents Docs Guide

## Dev environment tips
- Specifications live under `specs/`, SOP references under `sop/`, templates under `templates/`; keep file naming consistent so DocsSAG can link to them.
- `flow.schema.json` and `flow-runner.md` define the workflow contract—update them when upstream Flow Runner changes.
- Use Markdown linters locally to keep headings ordered and linkable.

## Testing instructions
- When editing `flow.schema.json`, rerun Flow Runner validators via `make validate-*`.
- If specs or SOPs change, ensure DocsSAG and KnowledgeMag AGENTS files reference the latest expectations.
- Manual spot checks: verify internal links resolve and referenced files exist.

## PR instructions
- Document schema or workflow updates in the PR description.
- Sync changes with `docs/AGENTS.md` if documentation processes change globally.
- When adding new SOPs or specs, mention them in the relevant agent AGENTS file so AI assistants know where to look.
