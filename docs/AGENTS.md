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
- `reference/tool/mcp/servers/` – official MCP reference servers (Everything, Fetch, Filesystem, Git, Memory, Sequential Thinking, Time) with launch/validation guidance.
- `reference/tool/mcp/chrome-devtools/` – Chrome DevTools MCP launch requirements, CLI flags, and validation workflows.
- `reference/tool/mcp/markitdown/` – MarkItDown MCP conversion tooling requirements and usage notes.
- `reference/tool/mcp/playwright/` – Playwright MCP automation options, flags, and validation guidance.
- `reference/files/AGENTS.md/` – upstream governance for maintaining AGENTS files.
- `reference/files/CHANGELOG.md/` – Keep a Changelog conventions and Openchangelog ingestion notes.
- `reference/reference-template.md` – canonical starting point for new reference entries.

## README placement
- Keep `README.md` at every human-maintained root inside `docs/` (for example `docs/`, `docs/reference/`, and each curated theme subfolder) so downstream agents understand the scope, update cadence, and templates in play.
- Skip `README.md` in purely generated or transient directories (`docs/generated/`, language export folders, or other automation outputs); rely on `.gitkeep` and automation docs instead.
- When introducing a new curated subdirectory (e.g., `docs/reference/<topic>/`), seed a short `README.md` that links back to `reference-template.md`, lists owners/review cadence, and points to any per-folder SOP.

## Markdown naming
- Default to `overview.md` for the primary narrative inside each docs subdirectory; this is where you summarise the topic, link sources, and note update cadence.
- When a folder aggregates multiple upstream sources (for example `docs/reference/engineering/prompt/`), split entries by source or publisher using descriptive TitleCase filenames such as `Anthropic.md`, `Google.md`, or `OpenAI.md`.
- Keep per-source files focused on that provider’s guidance, still based on `reference-template.md`, and cross-link them from the folder’s `overview.md` so readers can pivot between vendor-specific notes.
