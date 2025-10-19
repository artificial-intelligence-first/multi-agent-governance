# Skills Directory

Shared Skills live in this directory so Codex-led agents can reuse domain knowledge via filesystem bundles. Agent-specific overrides sit under `agents/<agent>/skills/` and take precedence when metadata names collide.

## Layout
- `registry.json` — canonical registry (owner, tags, enablement, execution policy) consumed by GovernanceSAG and MCPSAG.
- `ALLOWLIST.txt` — newline-delimited list of executable scripts (absolute repo paths + sha256 + arg pattern) permitted for Flow Runner.
- `_template/` — scaffold for authoring new Skills without immediately exposing them to the router.
- `PILOT_PLAN.md` — archived pilot rollout checklist with metrics, participants, and safeguards.
- `<skill-name>/` — each production Skill gets its own folder containing at minimum a `SKILL.md`; optional subdirectories (`resources/`, `scripts/`, etc.) hang beneath it.

Directories or files prefixed with `_` or `.` are ignored by MCPSAG discovery logic; keep temporary drafts or templates there.

## Authoring workflow
1. Copy `_template/SKILL.md` into a new `<skill-name>/SKILL.md`.
2. Update the YAML frontmatter (`name`, `description`) to describe capability + trigger conditions (≤64 / ≤1024 chars respectively).
3. Fill in procedural guidance, examples, and links to supporting resources. Keep the body under ~5k tokens and reference large artefacts indirectly.
4. Add any executable scripts under `scripts/` and register them in `ALLOWLIST.txt` with sha256 hashes before enabling execution.
5. Declare the Skill in `registry.json` (owner, tags, enabled=false default).
6. Run `make validate-skills` locally to verify lint checks before opening a PR.

## Governance
- GovernanceSAG leads the Skills program; MCPSAG operates routing. Update both `AGENTS.md` and `agents/SSOT.md` if you modify these conventions.
- Keep registry entries and allowlist hashes consistent with the committed filesystem state.
- Archive retired Skills by moving them to `archive/` with an accompanying Decision Log entry.

## Steady-state operations
- **Cadence**: Review `skills/registry.json` / `skills/ALLOWLIST.txt` every 30 days with GovernanceSAG + MCPSAG; record outcomes in `collab/skills-adoption/notes.md`.
- **Telemetry**: Export `telemetry/skills/events.jsonl` snapshots weekly into `telemetry/reports/skills_<phase>_<date>.json` and monitor guardrail KPIs (precision/recall, allow_exec accuracy).
- **Escalation**: Route guardrail breaches to GovernanceSAG within one business day; include analyzer output and relevant Skill diffs.
- **Change control**: Require `make validate-skills` + targeted pytest (`src/flowrunner/tests/test_skills_guard.py`) before merging Skill or allowlist updates.
