# Multi Agent Governance AGENTS Playbook

This repository hosts the Multi Agent Governance agent fleet plus shared automation. Keep this file current with the latest operational reality—sync it whenever you add or change tooling, workflows, or documentation.

## Dev environment tips
- Clone the repo and create an isolated environment: `python3 -m venv .venv && source .venv/bin/activate`.
- Install local tooling as needed via `pip install pytest` (tests expect pytest 8+) and reuse the same venv for validation scripts under `src/automation/`.
- DocsSAG writes Markdown to `docs/generated/`; ensure that directory stays in Git so downstream agents can read the latest drafts.
- For reference updates, follow `docs/reference/README.md`—use the template and update `last synced` whenever you pull new facts.
- Use `pnpm` only inside vendored examples; core automation relies on Python. If you need `pnpm`, install via Homebrew and run commands from the repository root.
- MCP routing lives in `.mcp/.mcp-config.yaml`; copy `.mcp/.env.mcp.example` to `.mcp/.env.mcp` for secrets. Codex, Cursor, and Flow Runner all read from this SSOT, so adjust providers and limits there instead of per-tool config.
- Enabling the GitHub MCP server requires `GITHUB_TOKEN` (and optional `GITHUB_API_BASE` / `GITHUB_API_VERSION`) in `.mcp/.env.mcp`; keep scopes minimal, rotate regularly, and note whether REST or GraphQL endpoints are in use.
- Route all MCP configuration changes through MCPSAG (`agents/sub-agents/mcp-sag/`); follow its SOP and checklist template before editing `.mcp/.mcp-config.yaml`.

## Testing instructions
- Run `make validate` before every commit to check knowledge, prompt, and docs automation scripts.
- Targeted checks:
  - KnowledgeMag: `make validate-knowledge`
  - DocsSAG: `make validate-docs-sag`
  - PromptSAG: `make validate-prompt`
- Unit tests live under each agent directory. Activate the venv and run, e.g., `python -m pytest agents/sub-agents/docs-sag/tests/test_agent.py`.
- When DocsSAG output changes, confirm the generated file appears in `docs/generated/` and passes lint/validation.
- If you touch Flow Runner assets, run the matching validator script under `src/automation/scripts/` (e.g., `validate_workflow.py`) to confirm schema coverage.
- For MCP updates, run `uvx mcpctl route "status"` plus targeted pytest coverage (`src/mcprouter/tests -k mcp`, `src/flowrunner/tests/test_runner.py -k mcp`) as documented in MCPSAG’s playbook.

## PR instructions
- Title format: `[component] summary`, e.g., `[docs-sag] Persist generated markdown`.
- Include updates to `AGENTS.md` or subordinate AGENTS files whenever workflows, commands, or policies change.
- Run `make validate` and relevant pytest suites before pushing.
- Update `agents/SSOT.md` and reference docs if terminology, contracts, or external specs shift; cite upstream sources in commit messages.
- For documentation changes, ensure the generated Markdown is committed and referenced from the appropriate AGENTS file.

## Directory map & AGENTS cascade
- Every top-level directory (`agents/`, `docs/`, `src/`) owns an `AGENTS.md` that summarises its contents; deeper folders reference those instructions rather than duplicating them.
- Current cascade:
  - `agents/AGENTS.md` – fleet structure, routing expectations, and links to agent assets.
  - `docs/AGENTS.md` – documentation workflow, reference syncing rules, and DocsSAG/PromptSAG outputs.
  - `src/AGENTS.md` – automation scripts and vendored Flow Runner housekeeping.
  - `.mcp/AGENTS.md` – MCP configuration SSOT (providers, env files, verification steps).
- MCPSAG maintains the MCP cascade; see `agents/sub-agents/mcp-sag/AGENTS.md` for provider lifecycle and documentation obligations.
- When introducing a brand-new top-level area, add an `AGENTS.md` there and link it from this file.

## Governance checklist
- Maintain alignment with the upstream AGENTS.md specification (see `docs/reference/OpenAI/AGENTS.md/` for synced notes and examples).
- Keep `.mcp/AGENTS.md` synced with operational changes whenever you add or retire MCP servers so downstream agents share the same defaults.
- Ensure every ExecPlan (`PLANS.md`) is generated via `exec plan`, maintains the canonical sections with UTC-stamped updates, and is removed after stakeholders sign off on completion (see `docs/reference/files/PLANS.md/OpenAI.md`).
- When you add or update `CHANGELOG.md`, follow the Keep a Changelog conventions captured in `docs/reference/files/CHANGELOG.md/overview.md` and keep the `Unreleased`+release sections in sync with SemVer tags.
- When interacting with users, prefer the requester’s primary language for conversations and status updates; keep internal artefacts (docs, logs, code) in English.
- Keep `agents/AGENT_REGISTRY.yaml`, `agents/SSOT.md`, and DocsSAG outputs in sync whenever routing or terminology shifts.
- Schedule periodic reviews: if a directory’s AGENTS.md hasn’t changed in 60 days, confirm it still reflects reality.
- Involve MCPSAG whenever MCP providers, credentials, or SDK dependencies move; confirm its checklist and runbook are updated alongside the change.
