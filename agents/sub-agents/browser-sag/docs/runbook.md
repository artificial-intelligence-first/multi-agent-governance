# BrowserSAG Runbook

Use this runbook to operate BrowserSAG’s governed browser automation workflows across Chrome DevTools MCP, Playwright MCP, and MarkItDown MCP.

## Normal Operation
1. Confirm prerequisites: Node.js 20.19+, npm, Chrome/Chromium, Playwright browsers, and Python 3.10+ with `markitdown-mcp`.
2. Export required environment variables (`MCP_ROUTER_PROVIDER`, optional browser flags) and verify MCP connectivity via `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"`.
3. Execute the requested workflow (Flow Runner flow or manual run) and capture artefacts (screenshots, traces, converted Markdown) under `telemetry/runs/<run_id>/browser/`.
4. Summarise visited URLs, tools invoked, and key findings in the run README for downstream auditors.
5. File follow-up tickets if accessibility blockers, automation failures, or content gaps are detected.

## Incident Response
- **MCP connectivity failure** → Validate `.mcp/.mcp-config.yaml`, rerun MCPSAG validation commands, and coordinate with MCPSAG if provider settings drifted.
- **Browser launch errors** → Reinstall Playwright browsers (`npx playwright install`), confirm Chrome availability, and capture logs for OpsMAG.
- **Trace or artefact loss** → Re-run with debug flags (`--save-trace`, `--video`) and upload artefacts manually to telemetry storage.
- **Security findings** → Notify SecuritySAG when automation exposes sensitive data or bypasses protections; halt runs until cleared.
- **Performance regressions** → Record metrics (navigation time, resource usage) and coordinate with WorkflowMAG to adjust automation schedules.
