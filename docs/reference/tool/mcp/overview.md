Source: https://modelcontextprotocol.io (last synced: 2025-10-18)
Source: https://blog.modelcontextprotocol.io (last synced: 2025-10-18)
Source: https://github.com/modelcontextprotocol (last synced: 2025-10-18)

# Model Context Protocol (MCP) Overview

## Summary
- Consolidates the official Model Context Protocol documentation so agents can connect to MCP servers consistently across the fleet.
- Highlights how the protocol bridges Codex, Flow Runner, and other automation clients to shared toolchains and data sources.

## Key Details
- **Protocol model**: MCP uses a client-server design with bidirectional messaging, borrowing from JSON-RPC semantics. Capability negotiation enables or disables tools, resources, prompts, and events per session.
- **Transports**: WebSocket is the reference transport, while the specification allows mapping onto alternatives such as gRPC or HTTP/2. Secure channels (TLS or equivalent) are expected for production deployments.
- **Resource graph**: Servers expose a tree of resources (documents, configs, binary assets) addressable by path; clients can subscribe to subtrees, fetch snapshots, or receive diffs as resources change.
- **Tool invocation**: Actions are described with JSON Schema payloads for inputs and outputs. Long-running operations should emit progress events and honour cancellation messages to keep automation responsive.
- **Authentication and security**: The protocol is transport-agnostic, so bearer tokens, mTLS, or sidecar proxies can enforce access control. Example implementations in the GitHub org demonstrate audit logging and scoped permissions.
- **Reference ecosystem**: The GitHub organisation ships TypeScript and Python SDKs, sample servers, VS Code tooling, and integration guides that show how to register tools, route prompts, and manage session lifecycle.

## Dependencies
- Keep MCP routing definitions in sync with `.mcp/.mcp-config.yaml`; whenever you add a server, update AGENTS/SSOT entries and store credentials in `.mcp/.env.mcp`.
- Flow Runner and Codex CLI integrations should validate tool signatures through `src/mcprouter`, recording capability negotiation outcomes for observability and rollback.
- DocsSAG and KnowledgeMag outputs that rely on MCP resources must record the resource paths and version metadata so validation scripts can detect drift.
- MCPSAG (`agents/sub-agents/mcp-sag/`) acts as the gatekeeper for configuration, documentation, and validation—engage it before deploying protocol or provider changes.

## Update Log
- 2025-10-18: Initial capture based on the official site and GitHub repositories.
