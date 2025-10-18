Source: https://github.com/modelcontextprotocol/python-sdk (last synced: 2025-10-18)

# MCP Python SDK

## Summary
- Provides official Python tooling for building Model Context Protocol clients and servers used by Codex, Flow Runner, and VS Code agents.
- Supplies ready-made transports, message models, and async runtime helpers so automation can expose tools and resources with minimal boilerplate.

## Key Details
- **Installation**: Published on PyPI as `mcp`; install with `pip install mcp` inside the repository’s venv. Includes optional extras for WebSocket and CLI tooling.
- **Server utilities**: Offers decorators and helper classes to register tools, resources, and prompts. Supports capability negotiation, pagination, and streaming responses.
- **Client support**: Provides async clients that manage session lifecycle, tool invocation, and resource subscriptions over standard transports (WebSocket by default).
- **Schema types**: Ships typed message models generated from the MCP specification, reducing manual JSON handling and ensuring compatibility with protocol updates.
- **Examples**: Repository contains sample servers (filesystem, Git) plus pytest-based tests illustrating authentication hooks and cancellation handling.
- **Tooling**: Bundles CLI commands to scaffold new servers, inspect manifests, and validate capability definitions against JSON Schema.

## Dependencies
- Align Python SDK usage with `.mcp/.mcp-config.yaml`; update manifests when adding new tools or resources so routing and DocsSAG outputs stay consistent.
- When embedding the SDK in `src/mcprouter`, ensure event loops integrate with existing async infrastructure (e.g., `asyncio.run` within Flow Runner tasks).
- Follow AGENTS guardrails by logging tool invocations and validating long-running actions before enabling them in automation pipelines.

## Update Log
- 2025-10-18: Initial summary based on the official MCP Python SDK repository.
