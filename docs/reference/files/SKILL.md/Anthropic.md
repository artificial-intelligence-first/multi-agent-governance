Source: https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview (last synced: 2025-10-19)
Source: https://github.com/anthropics/skills (last synced: 2025-10-19)
Source: https://github.com/anthropics/claude-cookbooks/tree/main/skills (last synced: 2025-10-19)
Source: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills (last synced: 2025-10-19)
Source: https://github.com/anthropics/claude-cookbooks/blob/main/skills/notebooks/01_skills_introduction.ipynb (last synced: 2025-10-19)
Source: https://github.com/anthropics/claude-cookbooks/blob/main/skills/notebooks/02_skills_financial_applications.ipynb (last synced: 2025-10-19)
Source: https://github.com/anthropics/claude-cookbooks/blob/main/skills/notebooks/03_skills_custom_development.ipynb (last synced: 2025-10-19)

# SKILL.md Overview

## Summary
- SKILL.md defines Anthropic’s Agent Skill package: a filesystem directory fronted by YAML metadata and Markdown instructions that let Claude load domain expertise on demand (sources: Claude docs, engineering blog).
- Skills deliver progressive disclosure in three tiers—metadata, SKILL.md body, and optional resources/scripts—so Claude only consumes relevant context while retaining access to large reference bundles (sources: Claude docs, engineering blog).
- Anthropic ships pre-built Skills for document workflows and publishes open-source examples plus templates in the `anthropics/skills` repository, alongside cookbook tutorials that walk through building and testing Skills end-to-end (sources: Claude docs, GitHub repo, Claude Cookbooks).

## Key Specifications
- **Required frontmatter**: only `name` (≤64 chars) and `description` (≤1024 chars); description must state capability plus trigger conditions so Claude can decide when to load the Skill (source: Claude docs).
- **Instruction body**: SKILL.md should outline procedures, examples, and links to auxiliary files (e.g., `FORMS.md`); Claude reads the body only after the description matches a task (sources: Claude docs, engineering blog).
- **Resources & scripts**: skills may bundle additional Markdown, data, or executable code (e.g., form-fill Python helpers); Claude accesses these via bash when referenced, and only script output—not source—enters context (sources: Claude docs, engineering blog).
- **Runtime**: Skills execute inside Claude’s code execution container with no outbound network, no ad-hoc package installs, and only pre-installed dependencies, so authors must rely on the shipped runtime (source: Claude docs).
- **Progressive disclosure model**: metadata loads at session start (~100 tokens), instructions remain under ~5k tokens per trigger, and bundled assets are effectively unlimited because they stay on disk until accessed (source: Claude docs).

## Platform Support & Distribution
- **Claude API**: supports pre-built and custom Skills; requests must send `code-execution-2025-08-25`, `skills-2025-10-02`, and `files-api-2025-04-14` headers plus a `skill_id` in the code execution container (source: Claude docs).
- **Claude Code**: discovers filesystem Skills automatically; developers can install curated packs (e.g., `document-skills`, `example-skills`) via the built-in plugin marketplace (sources: Claude docs, GitHub repo).
- **Claude.ai**: provides pre-built document Skills to all users and allows Pro/Max/Team/Enterprise accounts with code execution to upload custom zip packages per user (source: Claude docs).
- **Sharing models**: API Skills propagate workspace-wide, Claude.ai uploads remain per-user, Claude Code Skills live in `~/.claude/skills/` or project `.claude/skills/`, and surfaces do not sync automatically (source: Claude docs).

## Repository Notes
- Anthropic’s `skills` GitHub repo offers Apache-2.0 example Skills plus source-available document Skills that mirror production features (Source: GitHub repo).
- The repo includes a starter `template-skill` and strategy-focused examples spanning creative, technical, and enterprise use cases, highlighting reusable patterns for instruction design and tooling (source: GitHub repo).
- The Claude Cookbooks `skills/` directory provides step-by-step tutorials, debugging notes, and embeddings/prompting patterns for Skill development, complementing the raw examples in the main repository (source: Claude Cookbooks).
- Repository disclaimers emphasize validating behaviors before production use; examples may diverge from Claude’s managed Skills, underscoring the need for in-environment testing (source: GitHub repo).

## Security & Operational Guidance
- Install only trusted Skills; malicious bundles can misuse tools, leak data, or embed harmful scripts—treat Skills like third-party software and audit every file and dependency (sources: Claude docs, engineering blog).
- Watch for instructions that fetch external content or issue unexpected bash commands; Skills should align strictly with their described purpose before deployment (sources: Claude docs, engineering blog).
- Plan governance around lifecycle management: monitor usage, iterate on metadata, and evaluate performance gaps before expanding instruction scope (source: engineering blog).

## Update Log
- 2025-10-19: Initial Anthropic SKILL.md specification summary and repository notes.
- 2025-10-19: Added Claude Cookbooks reference and guidance on tutorial resources.
