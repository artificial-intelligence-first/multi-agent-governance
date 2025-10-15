# MCP Router Package Notes

- CLI entry point: `mcp_router/cli.py` (exposes `mcpctl`).
- Core router implementation lives in `mcp_router/router.py`; keep provider integrations stateless and ensure they close resources.
- Run `uv run -m pytest packages/mcprouter/tests` plus a quick `mcpctl route "ping"` before submitting changes.

Document any new provider options or CLI flags in `packages/mcprouter/README.md`.
