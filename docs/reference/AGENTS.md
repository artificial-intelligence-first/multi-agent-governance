# Reference Library Guide

## Dev environment tips
- Reference entries are plain Markdown; no additional tooling beyond the repo venv.
- Copy `reference-template.md` when adding a new topic so sections stay consistent.
- Place new documents in the appropriate themed folder (`agents/`, `engineering/`, or `files/AGENTS.md/`) and keep filenames dash-case for predictable linking.

## Testing instructions
- Manual checks only: confirm each file starts with an up-to-date `Source` line and an “Update Log”.
- When syncing multiple files, run `git diff --stat docs/reference` to ensure you touch only the intended topics.
- Consider adding link-check scripts under `src/automation` if external URLs change frequently.

## PR instructions
- Mention the upstream version/date in the PR description when updating reference files.
- Update related AGENTS files (root or agent-specific) so automation knows about new guidance.
- Keep vendor folders (e.g., `OpenAI/`) tidy; create subfolders only when a spec spans multiple documents.

## Directory map
- `agents/` – per-agent or vendor-aligned references (e.g., `codex/OpenAI.md`).
- `engineering/` – engineering practices and prompt design guidance (`engineering/prompt/` feeds PromptSAG).
- `files/AGENTS.md/` – upstream policies, templates, and FAQs for AGENTS maintenance.
- `reference-template.md` – canonical template; duplicate it whenever you add a new reference entry.
