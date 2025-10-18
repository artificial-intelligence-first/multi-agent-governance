Source: https://developers.openai.com/codex/guides/agents-sdk (last synced: 2025-10-13)
Source: https://github.com/openai/openai-agents-python (last synced: 2025-10-13)
Source: https://openai.github.io/openai-agents-python/ja/ (last synced: 2025-10-13)

# OpenAI Agents SDK

## Summary
- Official guide and SDK implementation for orchestrating Codex-powered agents with tool calling and conversation management.
- Provides Python client library, CLI tools, and documentation for building multi-step agent workflows.

## Key Details
- Agents SDK guide explains agent lifecycle: session creation, tool registration, conversation loop, and Codex invocation.
- Python repository offers asynchronous and synchronous clients, example agent templates, and integration tests.
- Documentation site (Japanese edition) covers quick start, tool API design, error handling patterns, and deployment guidance.
- SDK supports extensibility via custom tool definitions, webhook callbacks, and event hooks for logging or metrics.
- Includes configuration samples for environment variables, rate-limit handling, and retry strategies aligned with OpenAI policy.

## Dependencies
- Requires OpenAI API access with Agents feature enabled; can be combined with the Multi Agent Governance’s ContextSAG to supply structured context bundles.
- Works alongside PromptSAG outputs to enforce guardrails and evaluation criteria before agent execution.

## Update Log
- 2025-10-13: Initial capture from OpenAI Agents SDK guide, GitHub repository, and public documentation site.
