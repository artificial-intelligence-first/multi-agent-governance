# MCP Router Package Notes

- CLI entry point: `mcp_router/cli.py` (invoke with `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli`).
- Providers and router defaults now resolve from `.mcp/.mcp-config.yaml`; update that file plus `.mcp/AGENTS.md` whenever servers or limits change.
- First-party providers: `DummyProvider`, `OpenAIProvider`, and `GitHubProvider` (REST/GraphQL, propagating rate-limit metadata). Keep implementations stateless and ensure cleanup happens in `aclose()`.
- Run `PYTHONPATH=src/mcprouter/src uv run python -m pytest src/mcprouter/tests` and `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"` before submitting changes.

Document any new provider options or CLI flags in `src/mcprouter/README.md`.
