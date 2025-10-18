Source: https://github.com/modelcontextprotocol/servers/tree/main/src/memory (last synced: 2025-10-18)

# Memory MCP Server

## Overview
- Node-based knowledge graph memory server enabling persistent storage of entities, relations, and observations for LLM agents.
- Supports CRUD operations on entities, relations, and observations, plus graph reads and targeted searches.
- Provides a simple way to maintain long-lived context between sessions.

## Launch Commands
- Stdio (npx): `npx -y @modelcontextprotocol/server-memory`
- Docker: `docker run -i --rm -v claude-memory:/app/dist mcp/memory`

## Tools
- `create_entities`, `create_relations`, `add_observations`
- `delete_entities`, `delete_relations`, `delete_observations`
- `read_graph`, `search_nodes`, `open_nodes`

## Configuration Notes
- Persists data to the working directory (or mounted Docker volume). Mount a dedicated directory if durable storage is required.
- No mandatory environment variables; keep the storage location outside of main repos to avoid accidental commits.

## Validation
- `npx -y @modelcontextprotocol/server-memory --help`
- Exercise `create_entities` + `read_graph` via an MCP client to confirm persistence across sessions.

## Update Log
- 2025-10-18: Added to shared MCP configuration with npx stdio launch instructions.
