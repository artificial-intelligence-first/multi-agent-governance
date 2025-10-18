# MCP Configuration Playbook

# MCP Configuration Playbook

## Mission
- Keep the fleet aligned on a single MCP router/provider configuration surface.
- Treat `.mcp/SSOT.md` as the source for immutable values and verification steps referenced here.

## Layout
- `.mcp-config.yaml` — canonical router configuration. Execute MCPSAG SOPs before editing.
- `.env.mcp` / `.env.mcp.example` — provider tokens (real file stays untracked).
- `AGENTS.md` (this file) — structure and operating guidance.
- `SSOT.md` — authoritative values, required procedures, and validation commands.

## Operating Flow
1. Record intent and impact in PLANS.md, align with MCPSAG (`agents/sub-agents/mcp-sag/`).
2. Update `.mcp-config.yaml`; adjust `.env.mcp.example` if new variables are required.
3. Refresh SSOT with any new defaults or verification notes.
4. Run the validation commands listed in SSOT (e.g. `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"`) and capture results in PLANS.md.
5. During review, inspect `.mcp/` diffs together with SSOT updates to ensure consistency.

## Providers & Servers
- **GitHub** – Requires `GITHUB_TOKEN` plus optional overrides (`GITHUB_API_BASE`, `GITHUB_API_VERSION`, `GITHUB_TIMEOUT_SEC`). Router provider alias: `github`.
- **Context7** – Registered under `servers.context7`; defaults to the public HTTPS endpoint with no auth headers so anonymous access keeps working. Add a `CONTEXT7_API_KEY` header manually in `.mcp/.mcp-config.yaml` (or a local override) when you provision higher rate limits. Surface the REST API base as `CONTEXT7_API_URL` when automations need direct HTTP calls. Keep secrets in `.env.mcp` only; update `.env.mcp.example` with placeholders.
- **Everything** – Stdio server launched via `npx -y @modelcontextprotocol/server-everything`; no local state, but requires Node/npm availability. Useful for validating prompts/resources/tools support in MCP clients.
- **Fetch** – Python server invoked with `uvx mcp-server-fetch`; honours robots.txt unless `--ignore-robots-txt` is added. Ensure outbound HTTP access is allowed in the execution environment.
- **Filesystem** – Uses `npx -y @modelcontextprotocol/server-filesystem` with `MCP_FILESYSTEM_ROOT` providing the allowed workspace (defaults to `.`). Configure read-only mounts externally if needed; this server writes to the specified root.
- **Git** – Runs `uvx mcp-server-git --repository <path>`; set `MCP_GIT_REPOSITORY` to an absolute repo path (defaults to `.`). Requires Git installed and the repository accessible inside the sandbox.
- **Memory** – Uses `npx -y @modelcontextprotocol/server-memory`; persists knowledge graph data under the server’s working directory or mounted volume.
- **Sequential Thinking** – Launches with `npx -y @modelcontextprotocol/server-sequential-thinking`; set `DISABLE_THOUGHT_LOGGING=true` if transcripts must stay ephemeral.
- **Serena** – Added under `servers.serena` using the stdio transport. We launch via `uvx --from git+https://github.com/oraios/serena serena start-mcp-server` with defaults pulled from `SERENA_CONTEXT` (default `ide-assistant`) and `SERENA_PROJECT_ROOT`. Update `.mcp/.env.mcp` with a workspace-specific project path so Codex, Cursor, and Flow Runner activate the right repository before invoking tools.
- **Time** – Python server via `uvx mcp-server-time`; optionally set `LOCAL_TIMEZONE` before launch to pin the system timezone when running outside managed hosts.

## References
- [[SSOT]]
- `agents/sub-agents/mcp-sag/AGENTS.md` (SOP & checklist)
- `src/mcprouter/` (router implementation and tests)
