# Shared Assets Guide

## Dev environment tips
- Shared prompt partials live under `prompts/partials/`; keep file names stable so includes in agents stay valid.
- Templates and tooling scripts should avoid agent-specific assumptions—treat them as reusable building blocks.
- Use Markdown or YAML linters locally to keep shared content machine-readable.

## Testing instructions
- After changing prompt partials, rerun the validators for any agents that include them (`make validate-*`).
- If you add tooling under `tooling/`, provide either a unit test or a usage example and reference it in the relevant agent AGENTS.md.

## PR instructions
- Document breaking prompt or template changes in the PR description and update each affected agent’s AGENTS.md.
- Keep shared assets generic; if something becomes agent-specific, move it into that agent’s directory.
