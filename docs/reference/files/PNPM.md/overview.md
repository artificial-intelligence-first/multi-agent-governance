# PNPM Usage Guidance

## Purpose
- Document how pnpm is used within the Multi Agent System repository.
- Provide a quick refresher for agents when Node.js tooling appears in tasks.

## Core Workflow
- Prefer `pnpm install` at the repository root unless a subproject defines its own workspace.
- Use `pnpm run <script>` to execute package scripts; surface outputs through Flow Runner logs.
- Clean stale artefacts with `pnpm store prune` after large dependency updates.

## Guardrails
- Commit `pnpm-lock.yaml` whenever dependencies change to keep automation deterministic.
- Do not mix npm or yarn commands inside pnpm workspaces.
- When pnpm workflows change, update the `Source` lines in this document with the latest sync date.

## Source
- https://pnpm.io/motivation
- https://github.com/openai/codex/blob/main/PNPM.md
