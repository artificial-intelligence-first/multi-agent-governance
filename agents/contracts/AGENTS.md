# Contracts Directory Guide

## Dev environment tips
- Edit schema files (`*.schema.json`) with a JSON-aware editor and keep formatting compact.
- Use the repository venv; validations depend on `jsonschema` and helper scripts under `src/automation/scripts/`.
- Examples live under `examples/`; mirror every schema update with matching sample payloads.

## Testing instructions
- Run `make validate-knowledge`, `make validate-docs-sag`, `make validate-prompt`, or `make validate-context` after touching relevant schemas.
- For quick checks, execute the matching validator script under `src/automation/scripts/` to confirm required fields and examples.
- If schemas add new fields, update unit tests in each agent to assert the new keys.

## PR instructions
- Bump schema versions when you introduce breaking changes.
- Document schema updates in the PR description and link to affected agents or workflows.
- Keep `agents/SSOT.md` aligned with new terminology or contract ownership notes.
