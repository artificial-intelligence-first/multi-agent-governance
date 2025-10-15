# Documentation Playbook

## Dev environment tips
- Keep generated drafts (`docs/generated/`) under version control; DocsSAG writes here automatically.
- Reference material now lives under themed subdirectories in `docs/reference/` (e.g., `agents/`, `engineering/`, `files/AGENTS.md/`). Copy `reference-template.md` when adding new topics so sections stay consistent.
- Use Markdown linting locally if available; ensure headings are ordered consistently so downstream agents can parse them.

## Testing instructions
- Run `make validate-docs-sag` after editing generated docs or templates to ensure automation still passes.
- When DocsSAG output changes, spot-check the persisted Markdown to verify sections, actions, and references render as expected.
- If you script reference updates, add a pytest or script under `src/automation` to keep checks reproducible.

## PR instructions
- Update `docs/reference/` whenever external specs or policies shift; note the sync date in each file.
- Commit DocsSAG outputs alongside AGENTS updates and mention them in the PR description.
- Link documentation changes to the relevant agent or contract updates so reviewers can trace intent.

## Directory hints
- `generated/` – DocsSAG outputs (tracked via `.gitkeep`).
- `reference/agents/` – vendor or product-specific agent specs (e.g., `codex/`).
- `reference/engineering/` – engineering-focused notes; prompt guidance now resides in `reference/engineering/prompt/`.
- `reference/files/AGENTS.md/` – upstream governance for maintaining AGENTS files.
- `reference/files/CHANGELOG.md/` – Keep a Changelog conventions and Openchangelog ingestion notes.
- `reference/reference-template.md` – canonical starting point for new reference entries.
