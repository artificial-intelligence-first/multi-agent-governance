Source: https://github.com/microsoft/markitdown/tree/main/packages/markitdown-mcp (last synced: 2025-10-18)
Source: https://github.com/mcp/microsoft/markitdown (last synced: 2025-10-18)

# MarkItDown MCP Server

## Overview
- Python-based MCP server that wraps MarkItDown's document conversion pipeline so agents can turn URLs or local files into Markdown via the `convert_to_markdown` tool.
- Supports STDIO (default), Streamable HTTP, and SSE transports; stdio integration keeps BrowserSAG runs co-located with the calling process.
- Accepts `http`, `https`, `file`, and `data` URIs, returning structured Markdown plus extracted metadata for downstream processing.

## Requirements
- Python 3.10+ with `markitdown-mcp` installed (`uvx markitdown-mcp` or `pip install markitdown-mcp`).
- Optional extras (`markitdown[pdf]`, `markitdown[docx]`, etc.) unlock additional file converters; install them before launching long-lived servers.
- For Docker usage, mount local directories when converting on-disk artefacts (e.g., `-v /abs/path:/workdir`).

## Configuration
- `.mcp/.mcp-config.yaml` registers the server under `servers.markitdown` using `uvx markitdown-mcp`.
- Add CLI flags to the shared config or client overrides when switching transports (`--http`, `--sse`) or target hosts/ports.
- Auth is not built in; restrict network exposure by binding to localhost or running inside trusted containers.

## Operations & Validation
- Run `uvx markitdown-mcp --help` to inspect available arguments and confirm the executable is on `PATH`.
- Use BrowserSAG prompts to call `convert_to_markdown` when summarising downloaded files or web resources. Store outputs under `telemetry/runs/<run_id>/browser/`.
- Combine with Chrome DevTools or Playwright MCP sessions by feeding downloaded artefacts into MarkItDown for text extraction.

## Update Log
- 2025-10-18: Initial capture coinciding with BrowserSAG onboarding of MarkItDown MCP.
