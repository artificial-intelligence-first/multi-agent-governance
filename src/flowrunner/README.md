# Flowrunner Package

`flowrunner` ships the Typer-based `flowctl` CLI and supports the following step types:

- Shell steps (`uses: shell`)
- MCP steps (`uses: mcp`)
- Dynamic agents (`uses: "module:Class"`)

## Core commands

```bash
flowctl run <flow.yaml>
flowctl logs <run_id>
flowctl gc --keep 100
flowctl run --progress <flow.yaml>
```

Key options:

- `--dry-run` previews the execution order without running.
- `--only <step>` executes a specific step and automatically includes its dependencies.
- `--continue-from <step>` treats earlier steps as completed and resumes from the given step.
- `gc` prunes old run directories (combine with `--dry-run` to preview deletions).

## agent_paths

Add `agent_paths` to a flow definition to push directories onto `sys.path` before step instantiation. `examples/prompt_flow_with_agent.yaml` demonstrates the pattern while `examples/prompt_flow.yaml` remains agent-free.

## Validation

When a flow declares `$schema`, `flowctl` validates the document against the referenced JSON Schema before execution. Validation errors surface with clear messages prior to running any steps.

## Performance tips

- Run logs flush every 50 writes by default; set `FLOWCTL_LOG_FLUSH_EVERY` to customise the cadence or drop to `1` when you need immediate persistence.
- MCP router cadence and concurrency come from `.mcp/.mcp-config.yaml` (`router.log_flush_every`, `router.max_sessions`). Adjust those values—or their environment overrides—so Codex, Cursor, and Flow Runner stay aligned.
- Pass `--progress` while running longer flows to stream step status updates in-place. The toolkit is validated on Python 3.12–3.14 (CI runs 3.14.x); avoid prerelease interpreters until upstream Typer regressions are resolved.

## Tests

```bash
PYTHONPATH=src/flowrunner/src:src/mcprouter/src uv run python -m pytest src/flowrunner/tests
```

Tests run offline; the MCP router falls back to the dummy provider by default.
