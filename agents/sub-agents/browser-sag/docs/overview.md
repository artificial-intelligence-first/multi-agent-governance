# BrowserSAG Documentation

BrowserSAG combines Chrome DevTools MCP, Playwright MCP, and MarkItDown MCP to deliver governed browser automation. Review `docs/reference/tool/mcp/chrome-devtools/overview.md`, `docs/reference/tool/mcp/playwright/overview.md`, and `docs/reference/tool/mcp/markitdown/overview.md` for prerequisites, CLI flags, and validation guidance.

## Knowledge Base
- **Tool reference:** Chrome DevTools MCP, Playwright MCP, MarkItDown MCP (inputs, outputs, CLI flags).
- **Routing:** `.mcp/.mcp-config.yaml` (`servers.chrome-devtools`, `servers.playwright`, `servers.markitdown`).
- **Governance:** Update `agents/SSOT.md` and `.mcp/SSOT.md` whenever browser channels, CLI defaults, or conversion behaviours change.

### Capability summary
- **Chrome DevTools MCP:** Performance tracing, console inspection, screenshots, network analysis via Puppeteer-backed DevTools automation.
- **Playwright MCP:** Deterministic navigation and interaction through accessibility trees, optional trace/video capture, multi-browser channel support.
- **MarkItDown MCP:** Conversion of downloaded or remote resources (PDF, Office, media, etc.) into Markdown for downstream review and searchability.

## Run Artefacts
- Store screenshots (`*.png`), Playwright accessibility transcripts (`*.json`), Chrome DevTools traces (`*.json`/`*.zip`), and MarkItDown exports (`*.md`) under `telemetry/runs/<run_id>/browser/`.
- Provide a short `README.md` inside each run folder summarising URLs visited, tools invoked, and decisions taken.

## Validation Commands
- `PYTHONPATH=src/mcprouter/src uv run python -m mcp_router.cli route "status"`
- `npx -y chrome-devtools-mcp@latest --help` (verifies CLI resolution)
- `npx @playwright/mcp@latest --help`
- `uvx markitdown-mcp --help`
- Optional targeted smoke tests scripted under `tests/`.
- `python src/automation/scripts/validate_browser_sag.py` (checks documentation + MCP config wiring)
