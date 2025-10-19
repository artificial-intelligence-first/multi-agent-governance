# Skills Telemetry

This directory stores reference material for Skills-related telemetry emitted by MCPSAG and Flow Runner integrations.

- `events.schema.json` — JSON schema describing events such as `skill_selected`, `skill_loaded`, `skill_exec_attempt`, `skill_exec_result`, and `skill_embedding_fallback`.
- `events.jsonl` — optional staging log for ad-hoc inspection (not committed).

Update this schema whenever new events or fields are introduced, and keep PLANS/Decision Log entries aligned with telemetry changes.
