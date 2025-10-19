---
name: template-skill
description: >
  Replace this text with a concise description of what the Skill does and when to trigger it (≤1024 characters).
---

# Skill Title

> Replace this block with the Skill’s mission statement and any guardrails agents must observe.

## Quick start
- Step-by-step procedure the agent should follow when the Skill activates.
- Reference other files with relative links (e.g., `[See resources](resources/REFERENCE.md)`).
- Keep this section under ~5k tokens to avoid context bloat.

## Examples
- Example task → expected approach.
- Include success/failure patterns to guide agent decisions.

## Resources
- List Markdown files, datasets, or scripts bundled with the Skill.
- Note any prerequisites or environment assumptions.

## Script usage
- Describe when to run scripts under `scripts/` and the arguments they expect.
- Ensure each script is registered in `skills/ALLOWLIST.txt` with sha256 hashes before enabling execution.
