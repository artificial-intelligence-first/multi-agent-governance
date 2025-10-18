# Automation & Vendor Sources Guide

## Dev environment tips
- Activate `.venv` before running any scripts; automation is validated on Python 3.12–3.14 (CI targets 3.14.x).
- Keep vendored Flow Runner packages (`src/flowrunner/`, `src/mcprouter/`) untouched unless you are syncing from upstream.
- Use `python -m pip install -r requirements.txt` if additional tooling is introduced; document it in /AGENTS.md.
- Coordinate dependency pin or lockfile changes with DepsSAG before editing project metadata.

## Testing instructions
- Validators under `src/automation/scripts/` are invoked by `make validate-*`; run them directly when debugging (e.g., `python src/automation/scripts/validate_docs_sag.py`).
- Flow demos in `src/automation/flows/` can be run via Flow Runner to exercise agents end-to-end.
- If you add scripts, include pytest coverage or CLI smoke tests and document usage here.

## PR instructions
- Document new automation entry points and required environment variables.
- When updating vendored packages, note upstream commit hashes in the PR description and update `README.md` references.
- Keep script outputs English-only and ensure they align with AGENTS policies so downstream agents can parse them.

## MCP configuration
- `mcp_router` and Flow Runner now read provider settings from `.mcp/.mcp-config.yaml`; extend that file instead of hardcoding environment defaults.
- Secrets belong in `.mcp/.env.mcp` (copy from `.env.mcp.example`); never commit real keys.
- Use `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"` or the Flow Runner MCP tests (`PYTHONPATH=src/flowrunner/src:src/mcprouter/src uv run python -m pytest src/flowrunner/tests/test_runner.py -k mcp`) after editing the config.
