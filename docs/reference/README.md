# Reference Docs Guide

Store external reference material here using one Markdown file per topic. The directory is split into themed areas so downstream agents know where to look:

- `agents/` – vendor- or product-specific agent references.
- `engineering/` – engineering practices (e.g., prompt guidelines).
- `files/AGENTS.md/` – governance notes that back the AGENTS cascade.
- `sdk/` – SDK references (Codex SDK, Agents SDK, and related tooling).
- `kit/` – Toolkits such as AgentKit; high-level frameworks built on top of SDKs.
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
