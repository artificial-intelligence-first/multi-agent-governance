# Reference Docs Guide

Store external reference material here using one Markdown file per topic. The directory is split into themed areas so downstream agents know where to look:

- `agents/` – vendor- or product-specific agent references, including `codex/`, `kit/agent-kit/`, and `sdk/`.
- `engineering/` – engineering practices (e.g., prompt guidelines and context engineering).
- `files/` – governance notes that back AGENTS, PLANS, SSOT, PNPM, and other repo-wide conventions.
- `tool/` – MCP and related runtime tooling references (e.g., `tool/mcp/`).
- `reference-template.md` – canonical template for new entries.

How to use:
- Start from `reference-template.md` in this directory when creating a new entry.
- Keep the “Source” line at the top and update the `last synced` date whenever upstream content changes.
- Place each file in the matching subfolder and use concise dash-case filenames such as `prompt-basics.md`.
- Capture every refresh as a short bullet in the “Update Log” section of the document.

Example source line:
```
Source: https://example.com/foo (last synced: 2025-10-13)
```

Feel free to create vendor-specific folders under the relevant theme (e.g., `agents/codex/` or `engineering/prompt/google/`) so related references stay grouped.
