Source: https://www.promptingguide.ai/guides/context-engineering-guide (last synced: 2025-10-13)

# DAIR.AI – Context Engineering Guide

## Summary
- Provides a practitioner-focused process for designing, iterating, and evaluating context strategies for LLM applications.
- Offers concrete tooling suggestions (retrievers, memory stores, evaluation frameworks) mapped to each workflow stage.

## Key Details
- Recommends starting with problem framing: identify task goals, user personas, and desired outputs before collecting context.
- Introduces a retrieval stack checklist covering document ingestion, chunking strategy, embedding selection, and ranking.
- Highlights evaluation patterns such as contrastive prompting, ablation tests, and user-in-the-loop reviews to compare context variants.
- Suggests operational playbooks for monitoring drift (e.g., embed telemetry, feedback tagging) and rolling back context updates safely.
- Notes integration best practices—maintain versioned context bundles and automate syncing with source-of-truth repositories.

## Dependencies
- Complements internal Multi Agent Governance automation scripts (`src/automation/scripts/`) that validate documentation payloads.
- Can be combined with Anthropic and Claude references to tailor formatting once context candidates are selected.

## Update Log
- 2025-10-13: Initial capture from DAIR.AI context engineering guide.
