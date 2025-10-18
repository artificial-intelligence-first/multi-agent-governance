# BrowserSAG

BrowserSAG is the safe, auditable browser automation sub-agent. It combines Chrome DevTools MCP for tracing and screenshots, Playwright MCP for accessibility-driven actions, and MarkItDown MCP for converting captured artefacts to Markdown so orchestration agents can run consistent investigation flows without bespoke scripting.

## Quick Links
- Configuration & requirements: `docs/reference/tool/mcp/chrome-devtools/overview.md`, `docs/reference/tool/mcp/playwright/overview.md`, `docs/reference/tool/mcp/markitdown/overview.md`
- Router entry: `.mcp/.mcp-config.yaml` (`servers.chrome-devtools`, `servers.playwright`, `servers.markitdown`)
- SOP: `agents/sub-agents/browser-sag/sop/browse_run.yaml`
- Validation workflow: `agents/sub-agents/browser-sag/workflows/validate_browser_assets.wf.yaml`

## Expected Inputs
- ExecPlan tasks that call for live site inspection, trace capture, or debugging (typically from WorkFlowMAG, ContextSAG, or GovernanceSAG).
- Prompt bundles stored under `agents/sub-agents/browser-sag/prompts/` that define navigation scope, guardrails, and artefact expectations.
- WorkFlowMAG's browser stage (`browser_stage.py`) requests run scaffolds via Flow Runner before documentation and prompt stages proceed.

## Outputs
- Telemetry artefacts (screenshots, Playwright accessibility logs, Chrome DevTools traces, MarkItDown exports) saved under `telemetry/runs/<run_id>/browser/`.
- Status notes reported back to the requesting agent, including any escalations raised through MCPSAG.
