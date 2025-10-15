# Flowrunner Package Notes

- Entry point: `flow_runner/cli.py` exposes the `flowctl` Typer application.
- Update `docs/flow.schema.json` alongside any schema-affecting change.
- Run `uv run -m pytest packages/flowrunner/tests` before sending patches.
- Smoke test the sample flow with `flowctl run examples/prompt_flow.yaml --dry-run`.

Document any new CLI options or runtime behaviors in `packages/flowrunner/README.md`.
