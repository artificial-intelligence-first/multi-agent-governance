# BrowserSAG Playbook

## Role
- Provide governed browser automation for the fleet by operating Chrome DevTools, Playwright, and MarkItDown MCP tooling on behalf of orchestration agents.
- Translate high-level research or debugging requests into repeatable multi-tool sessions (navigation, accessibility actions, document conversion) with artefacts that downstream reviewers can audit.

## Responsibilities
- Maintain launch and validation procedures for `servers.chrome-devtools`, `servers.playwright`, and `servers.markitdown` (see docs under `docs/reference/tool/mcp/`).
- Curate prompts and workflows that scope navigation targets, sensitive-data guards, and performance expectations.
- Orchestrate post-run conversions (e.g., feed downloaded assets into MarkItDown) so textual artefacts accompany browser traces.
- Record run artefacts (screenshots, traces, console logs, Markdown exports) under `telemetry/` according to repository retention rules.
- Surface browser automation risks to MCPSAG when Chrome or Playwright channels, CLI flags, or MCP interfaces change.

## SOP Index
- `sop/browse_run.yaml` - baseline checklist covering environment prep, prompt selection, trace/artefact capture, and shutdown hygiene across Chrome DevTools, Playwright, and MarkItDown.
- `sop/escalation.yaml` - escalation path for browser security incidents or MCP regressions affecting Chrome DevTools, Playwright, or MarkItDown integrations.
