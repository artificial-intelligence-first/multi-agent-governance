# SSOT — /agents

## Canonical References
- Repository baseline: /SSOT.md (root).
- Docs guidance: docs/SSOT.md.

## Notes
- Use this directory to capture agent-wide terminology, contracts, and governance details that extend the repository SSOT (`/SSOT.md`).
- When policies change, update this file together with /SSOT.md to keep agents aligned.
- MCP routing changes must flow through `.mcp/.mcp-config.yaml`; document any new providers or keys referenced by agents here and in `.mcp/AGENTS.md`.
- GitHub MCP server support requires `GITHUB_TOKEN` credentials; record scope/rotation details (REST + GraphQL) when agents start consuming GitHub data.
- SecuritySAG consumes GitHub MCP security tooling (secret scanning, push protection, prompt review, code scanning, audit logs, authorization checks); provision tokens with `security_events`, `repo`, `read:org`, `workflow`, and `audit_log` scopes and document findings in `docs/generated/security-securitysag.md`.
- Context7 MCP server support requires `CONTEXT7_MCP_URL`/`CONTEXT7_API_KEY` (HTTPS endpoint + API key) and optional `CONTEXT7_API_URL` for REST fallbacks; capture rotation cadence and access levels alongside GitHub notes.
- Serena MCP server support runs via `uvx --from git+https://github.com/oraios/serena serena start-mcp-server`; align `SERENA_CONTEXT` and `SERENA_PROJECT_ROOT` with each agent’s workspace assumptions and log which projects are pre-indexed.
- Chrome DevTools MCP server support runs under `servers.chrome-devtools` via `npx -y chrome-devtools-mcp@latest`; note which hosts have Node.js 20.19+, npm, and Chrome installed, and whether `--headless`, `--browserUrl`, or custom `--executablePath` flags are required for automation.
- MarkItDown MCP server support runs under `servers.markitdown` via `uvx markitdown-mcp`; ensure Python 3.10+ plus required extras (`markitdown[pdf]`, etc.) are installed on BrowserSAG hosts, and document any Docker usage for remote conversions.
- Playwright MCP server support runs under `servers.playwright` via `npx @playwright/mcp@latest`; record default flags (`--headless`, `--browser`, trace/video capture) and note where browser binaries are cached.
- BrowserSAG (`agents/sub-agents/browser-sag/`) operates the Chrome DevTools MCP workflows. Record prompt names, telemetry paths, and SOP revisions whenever browser automation capabilities change.
- Reference MCP servers from `modelcontextprotocol/servers` expose Everything/Fetch/Filesystem/Git/Memory/Sequential Thinking/Time; require `npx`/`uvx` on PATH and absolute paths via `MCP_FILESYSTEM_ROOT` / `MCP_GIT_REPOSITORY` when enabling filesystem or Git mutations.
- MCPSAG (agents/sub-agents/mcp-sag) owns the MCP change checklist and validation SOP—loop it in before altering provider dependencies or SDK versions.
- GovernanceSAG (agents/sub-agents/governance-sag) audits AGENTS/SSOT/CHANGELOG/PLANS artefacts; involve it whenever governance SOPs or terminology shift.
- DepsSAG (agents/sub-agents/deps-sag) plans dependency upgrades, regenerates uv locks, and coordinates security advisories with WorkflowMAG/QAMAG/GovernanceSAG; loop it in before altering language/toolchain baselines.
- **Skill** – Filesystem bundle containing `SKILL.md` (frontmatter + instructions) plus optional resources/scripts. Shared Skills live in `/skills/`; agent overrides reside in `agents/<agent>/skills/`.
- **Skill Registry** – `skills/registry.json` records owner, tags, execution policy, and enablement state; GovernanceSAG reviews changes, MCPSAG consumes it at router startup.
- **skills_v1** – Feature flag enabling progressive Skill loading inside MCPSAG. Default off; toggle per-environment after pilots pass acceptance criteria.
- **Skills Lint** – `make validate-skills` target (wired into `make validate`) that validates frontmatter fields, token budgets, path references, and dangerous commands before Skills merge.
- **skills_exec** – Feature flag gating Skill script execution inside Flow Runner; keep disabled outside controlled pilots and document flips in `PLANS.md`.
- **Flow Runner guardrails Skill** – `skills/flow-runner-guardrails/SKILL.md`; source of truth for allowlist hashing, telemetry, and escalation paths when enabling `skills_exec`.
- **DocsSAG draft-quality Skill** – `agents/sub-agents/docs-sag/skills/draft-quality/SKILL.md`; replaces legacy runbook sections for publication readiness checks and remediation tracking.
