Source: https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/overview#prompting-vs-finetuning (last synced: 2025-10-13)
Source: https://github.com/anthropics/prompt-eng-interactive-tutorial (last synced: 2025-10-13)

# Claude Prompt Engineering Overview

## Summary
- Consolidates Anthropic’s official prompt engineering guidance and interactive tutorial so the Multi Agent Governance can align Claude-related automation and documentation.
- Highlights when to rely on prompt iteration versus finetuning, and how to structure prompts for reproducible outputs.

## Key Details
- **Prompt iteration vs. finetuning**: Anthropic encourages iterative prompt design—start with prompting, only move to finetuning when prompts cannot reliably control behaviour.
- **Prompt patterns**: Use explicit instructions, separate context blocks, and inject examples when precision is needed; the tutorial demonstrates step-by-step refinement techniques.
- **Evaluation loops**: Test prompts with varied inputs to detect edge cases; Anthropic suggests logging intermediate outputs to observe behaviour shifts.
- **Guardrails**: Reinforce safety guidelines and prohibited content in the prompt itself, especially when model outputs may be reused downstream.
- **Interactive tutorial**: The GitHub repository provides hands-on exercises showing Claude’s responsiveness to prompt tweaks, chain-of-thought scaffolding, and debugging strategies.
- **Collaboration**: Capture successful prompt variants and share them across teams to speed up adoption and avoid repeating experimentation.

## Dependencies
- Keep the Multi Agent Governance’s root and agent-level AGENTS.md guardrails in mind—Codex/Claude prompts should both enforce testing, safe edits, and documentation.
- Synchronize DocsSAG or KnowledgeMag guidance when Claude prompts become canonical procedures.
- If finetuning or API requests are integrated into automation, ensure credentials and rate limits are tracked in ops playbooks.

## Update Log
- 2025-10-13: Initial capture of Anthropic prompt engineering resources.
