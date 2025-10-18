Source: Internal Multi Agent Governance documentation (last synced: 2025-10-18)

# Reference Library Overview

## Scope
- Curate upstream specifications, governance notes, and integration guides that downstream agents rely on when working across the repository.
- Organise topics under themed folders (`agents/`, `engineering/`, `files/`, `tool/`) with dedicated `overview.md` files plus per-source breakdowns where needed.
- Keep everything derived from `docs/reference/reference-template.md` so metadata (`Source`, `last synced`, `Update Log`) stays consistent.

## Navigation
- [Agent references](agents/README.md) — vendor-specific agent behaviour and assets.
- [Engineering playbooks](engineering/README.md) — promptcraft, context strategy, and evaluation templates.
- [Repository file governance](files/README.md) — policies for AGENTS, PLANS, SSOT, CHANGELOG, and pnpm usage.
- [Tool integrations](tool/README.md) — MCP servers, SDKs, and supporting utilities.

## Maintenance
- Review each themed folder at least every 60 days; update `last synced` metadata and the Update Log whenever upstream sources change.
- Run `make validate-docs-sag` after amending references so automation catches missing contracts or prompts.
