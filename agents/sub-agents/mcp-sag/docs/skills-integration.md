# Skills Integration Design (MCPSAG)

Updated: 2025-10-19

## Goals
- Discover Skills metadata from `/skills/` and `agents/<agent>/skills/` without introducing Claude-specific dependencies.
- Provide deterministic matching so Codex agents load Skills progressively (frontmatter → body → optional resources).
- Respect security and governance requirements: offline embeddings, feature flag gating, telemetry, and allowlist enforcement.

## Components
1. **Metadata Loader**
   - Tree walk roots: `/skills/` and `agents/**/skills/`.
   - Ignore directories prefixed with `_` or `.` (drafts, templates).
   - Parse `SKILL.md` frontmatter (YAML) capturing `name`, `description`.
   - Cache file `mtime` and frontmatter hash to avoid unnecessary reloads.
   - Store metadata in `skills_metadata.json` (runtime cache) keyed by canonical path.

2. **Embedding Pipeline**
   - Model: `bge-large-en` via `uv run python src/automation/scripts/embed_skills.py` (offline sentence-transformer).
   - Cache path: `.mcp/cache/skills_embeddings.json` (map of skill path → vector).
   - Regenerate embeddings when metadata hash changes.
   - External APIs (OpenAI, Anthropic) prohibited unless GovernanceSAG grants exception and updates `.mcp/SSOT.md`.

3. **Matcher Workflow**
   1. Encode incoming task description with same local embedding model.
   2. Retrieve top-k (default 3) using cosine similarity.
   3. Apply BM25 keyword scoring on descriptions for tiebreaks.
   4. Enforce threshold (initial 0.75) and feature flag `skills_v1`.
   5. Return ordered candidates with metadata references.

4. **Staged Loader**
   - Level 1: inject frontmatter summary into MCPSAG system prompt at startup (minimal tokens).
   - Level 2: on match, read `SKILL.md` body and stream into Codex prompt (token cap enforcement).
   - Level 3+: follow references (e.g., `resources/*.md`) only upon Codex request.
   - Execution requests forwarded to Flow Runner; require allowlist approval before running scripts.

5. **Telemetry**
   - Emit structured events:
     - `skill_selected` (candidate list with scores).
     - `skill_loaded` (path, tokens, latency).
     - `skill_resource_requested` (resource path, reason).
     - `skill_exec_attempt` / `skill_exec_result` (script path, outcome).
   - Export to `telemetry/skills/` dashboards; keep 30-day retention.

6. **Feature Flags**
   - `skills_v1` toggled via `.mcp/.mcp-config.yaml`.
   - Additional flag `skills_exec` to control script execution separately from metadata loading.
   - Document activation in PLANS Decision Log; provide rollback instructions.

7. **Error Handling**
   - Missing frontmatter: log warning, skip Skill, surface in validation summary.
   - Embedding failure: fall back to keyword-only matching and emit `skill_embedding_fallback`.
   - Token overflow: truncate body to 5k tokens and set `truncated=true` in telemetry.

## Sequencing
1. Implement metadata loader and cache (feature flag off).
2. Integrate embedding pipeline + matcher; add unit tests in `src/mcprouter/tests`.
3. Enable read-only loading during Phase 1; monitor telemetry.
4. After Flow Runner guardrails ship, enable `skills_exec` per environment.

## Dependencies
- `skills/registry.json` (owner, tags, enablement) for governance checks; loader should respect `enabled=false`.
- `skills/ALLOWLIST.txt` for execution gating; Flow Runner cross-check, not MCPSAG.
- Lint (`validate_skills.py`) ensures consistent metadata before runtime loads.

## Open Questions
- Should we surface multiple Skills simultaneously when confidence scores cluster?
- How do we version embeddings when the model updates?
- Do we expose a manual override for operators to force-load a Skill via router CLI?
