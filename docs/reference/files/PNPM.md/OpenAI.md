# PNPM Usage Overview

## Background
pnpm is a fast, disk space–efficient package manager for Node.js projects. It uses a content-addressable store to share dependencies across projects, minimizing install time and storage footprint.

## Repository Policy
- Use pnpm only inside vendored examples or directories explicitly requiring Node.js tooling.
- Install pnpm via Homebrew (`brew install pnpm`) when working locally, ensuring the global executable is available.
- Run pnpm commands from the repository root unless a subproject specifies a different working directory.

## Common Commands
- `pnpm install` — install dependencies defined in `package.json`.
- `pnpm run <script>` — execute scripts declared in the project.
- `pnpm update` — refresh dependencies to the latest compatible versions.
- `pnpm store prune` — clean unused packages from the pnpm store.

## Best Practices
- Commit lockfiles (e.g., `pnpm-lock.yaml`) with dependency updates.
- Avoid mixing npm/yarn commands in the same workspace to prevent lockfile conflicts.
- Verify scripts via CI or Flow Runner workflows when pnpm-based automation is involved.

## Update Log
- 2025-10-13 — Imported guidance from OpenAI Codex PNPM documentation and aligned with Multi Agent Governance usage notes.

## Source
- https://github.com/openai/codex/blob/main/PNPM.md
