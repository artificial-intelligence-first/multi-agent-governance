# Skill Template

Use this scaffold when creating a new Skill:

1. Copy this directory to `skills/<skill-name>/`.
2. Rename the frontmatter fields inside `SKILL.md` (`name`, `description`) to the canonical Skill identifier and trigger guidance.
3. Replace placeholders in the body with actionable procedures, examples, and references.
4. Add optional subdirectories as needed:
   - `resources/` for Markdown/data artefacts referenced in the instructions.
   - `scripts/` for executable helpers (register each script in `skills/ALLOWLIST.txt`).
5. Add an entry to `skills/registry.json` and set `enabled` to `false` until reviews complete.
6. Run `make validate-skills` before publishing.
