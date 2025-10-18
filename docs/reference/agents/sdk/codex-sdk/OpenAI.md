Source: https://developers.openai.com/codex/sdk (last synced: 2025-10-18)
Source: https://github.com/openai/codex/tree/main/sdk/typescript (last synced: 2025-10-18)

# Codex SDK (OpenAI)

## Summary
- Official SDK resources for integrating OpenAI Codex into applications via REST and TypeScript helper libraries.
- Provides authentication, request builders, and example workflows for code generation and completion scenarios.

## Key Details
- Supports both REST and TypeScript SDK usage; TypeScript package exposes high-level helpers for completions, edits, and streaming tokens.
- Authentication uses standard OpenAI API keys via environment variables; examples illustrate `.env` usage and API key rotation.
- Documentation outlines rate limits, error handling best practices, and code snippets for editor integrations.
- GitHub repository includes generated SDK source plus unit tests and example projects for Node.js environments.
- Highlights compatibility with modern tooling (ESM, bundlers) and provides guidance for bundling in browser contexts with proper API proxying.

## Dependencies
- Requires an active OpenAI API key with Codex access; works alongside Agents SDK when orchestrating multi-step workflows.
- Recommended to combine with the Multi Agent Governance’s PromptSAG for structured prompt generation feeding Codex completions.

## Update Log
- 2025-10-13: Initial capture from Codex SDK documentation and TypeScript SDK repository.
