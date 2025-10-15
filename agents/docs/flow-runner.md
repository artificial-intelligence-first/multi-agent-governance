# Flow Runner Integration

WorkFlowMAG orchestrates Multi Agent System workflows using [flow-runner](https://github.com/artificial-intelligence-first/flow-runner). Vendored packages live in `src/flowrunner/` and `src/mcprouter/`, and `make setup-flow-runner` installs them into the Python user site so `flowctl` is available.

## Bootstrap

```bash
make setup-flow-runner
```

The helper script (`src/automation/scripts/setup_flow_runner.sh`) ensures the vendored packages are up to date. Add the user-site bin directory (`python -m site --user-base`) to your `PATH` so `flowctl` and `mcpctl` resolve.

## Running WorkFlowMAG flows

The primary orchestration flow is `runtime/automation/flow_runner/flows/workflow_mag.flow.yaml`. It models parallel execution by letting the Docs and Prompts stages start immediately after the Plan stage. Context follows Prompts, QA waits on Docs and Context, Operations reviews QA output, and Finalize closes the run.

```bash
flowctl run runtime/automation/flow_runner/flows/workflow_mag.flow.yaml --dry-run
```

`--dry-run` prints the resolved execution order without invoking external agents. Real runs emit artifacts under `.runs/<RUN_ID>/` and are now English-only—user deliverables are no longer localized automatically.

## Extending flows

- Add or modify stages by editing `workflow_mag.flow.yaml` and, if needed, implementing new stubs in `src/flow_runner/tasks/workflow_mag/`.
- Keep `agent_paths` aligned with available packages; remove unused entries to avoid stale imports.
- Update parallelization logic carefully—ensure stage dependencies reflect the actual data flow so Flow Runner can execute safely.

## Validation

Use `make validate`, `make test`, and `flowctl run --dry-run runtime/automation/flow_runner/flows/workflow_mag.flow.yaml` to confirm contracts, tests, and the orchestration graph stay healthy after changes.
