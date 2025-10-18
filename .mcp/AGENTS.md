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
4. Run the validation commands listed in SSOT (e.g. `uvx mcpctl route "ping"`) and capture results in PLANS.md.
5. During review, inspect `.mcp/` diffs together with SSOT updates to ensure consistency.

## References
- [[SSOT]]
- `agents/sub-agents/mcp-sag/AGENTS.md` (SOP & checklist)
- `src/mcprouter/` (router implementation and tests)
