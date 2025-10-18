Source: https://keepachangelog.com/en/1.1.0/ (last synced: 2025-10-15)
Source: https://openchangelog.com/docs/getting-started/keep-a-changelog/ (last synced: 2025-10-15)

# CHANGELOG.md Guidance

## Summary
- Capture all notable changes in a root-level `CHANGELOG.md` using the Keep a Changelog format so humans can scan releases without reading commit logs.
- Use structured sections (Unreleased + dated releases) with clear categories so tooling and Openchangelog can parse updates for publication.
- Keep entries reader-focused: describe behaviour changes, link to tickets or PRs when helpful, and note anything requiring follow-up action.

## Key Details
- **Structure**: Start with an `## [Unreleased]` section, then list released versions in reverse chronological order (`## [x.y.z] - YYYY-MM-DD`).
- **Categories**: Group bullet points under the standard headings (`### Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`). Add others only when justified.
- **SemVer alignment**: Release headings should match the Semantic Versioning tags used in Git; link headings to compare URLs when possible.
- **Plain language**: Write entries in human-first prose (what changed, why it matters, any migration steps) rather than raw commit messages or diffs.
- **Housekeeping**: Remove empty subsection headings, keep ISO-8601 dates, and carry forward unreleased bullets into a dated section when a release ships.

## Workflow in this repository
- Keep `CHANGELOG.md` in sync with ExecPlan outcomes: when major work closes, summarise the externally visible change before archiving the plan.
- Before cutting a release, move completed items from `Unreleased` into a new version block and cross-link to the release tag or PR bundle.
- After publishing, reset the `Unreleased` section to placeholders (or leave it absent) so the next round of changes start cleanly.
- If the changelog feeds automated tooling (DocsSAG, deployment notes), ensure entries include any required metadata (e.g., component names) without sacrificing readability.
- Avoid dumping CI output or test logs into the changelog; link to supporting artefacts stored elsewhere when necessary.

## Openchangelog usage
- Openchangelog auto-detects the Keep a Changelog structure when you point it to a single Markdown file; set the source to the repository `CHANGELOG.md`.
- The service parses sections and categories to render a hosted changelog site—stay consistent with headings so parsing succeeds.
- To republish quickly, run Openchangelog after each release commit so the hosted view mirrors the Markdown file.

## Update Log
- 2025-10-15: Initial capture combining Keep a Changelog 1.1.0 guidance with Openchangelog ingestion notes.
