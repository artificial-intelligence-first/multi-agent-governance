# Multi Agent Governance Stack

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![CI: Validate SOP](https://img.shields.io/badge/CI-Validate%20SOP-blueviolet.svg)
![CI: Contracts Check](https://img.shields.io/badge/CI-Contracts%20Check-teal.svg)
![CI: Docs Link Check](https://img.shields.io/badge/CI-Docs%20Link%20Check-slateblue.svg)

Multi Agent Governance is an open-reference governance stack for orchestrating AI agent fleets. It provides opinionated documentation, schemas, workflows, and automation that keep human-readable guidance and machine-enforced guardrails aligned. The repository does **not** ship a runnable service; instead, it offers a blueprint for teams building their own agent operations platform.

## What’s Inside
- **Fleet governance** – Guardrails and playbooks live beside the agents that use them. See [`agents/AGENTS.md`](agents/AGENTS.md) for the fleet map.
- **Workflow automation** – Flow Runner pipelines under `src/automation/` and `runtime/automation/` model end-to-end orchestration.
- **Contracts & prompts** – JSON Schemas, sample payloads, and prompt templates ensure consistent hand-offs across roles.
- **Quality & compliance** – Shared SOPs and validation scripts make it easy to enforce testing before a release.

## Getting Started
```bash
git clone https://github.com/<your-org>/multi-agent-governance.git
cd multi-agent-governance
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make validate   # run the governance validators
make test       # execute pytest suites
```

Next steps:
1. Review the root guardrails in [`AGENTS.md`](AGENTS.md) and terminology in [`SSOT.md`](SSOT.md).
2. Inspect the fleet registry in [`agents/AGENT_REGISTRY.yaml`](agents/AGENT_REGISTRY.yaml) to understand default routing.
3. Configure Flow Runner by following `agents/docs/flow-runner.md`, then run `flowctl run --dry-run runtime/automation/flow_runner/flows/workflow_mag.flow.yaml`.

## Repository Layout
```
.
|-- AGENTS.md / SSOT.md     # Root governance and terminology
|-- agents/                 # Agent fleet (main, sub, shared) with docs/SOPs/tests
|-- docs/                   # Reference material mirrored from upstream sources
|-- runtime/                # Flow Runner assets and generated logs
|-- src/                    # Automation scripts, vendored flowrunner + mcprouter
|-- tests/                  # Repository-level regression tests
|-- LICENSE                 # MIT License
`-- Makefile                # Common validation / testing entry points
```

## Governance & Compliance
- **ExecPlan workflow** – Use `uv run -m automation.execplan --task-name "<Task>"` to generate `PLANS.md` before multi-step work. Keep every required section current with timestamped updates, and remove the file once the task closes (guidance: `docs/reference/files/PLANS.md/OpenAI.md`).
- **Changelog hygiene** – Document releases in `CHANGELOG.md` using Keep a Changelog structure so Openchangelog can parse updates (guidance: `docs/reference/files/CHANGELOG.md/overview.md`).
- **Pre-task check** – Run `uv run -m automation.compliance.pre --task-name "<Task>" --categories <labels>` to confirm required artefacts.
- **Testing** – Always run `make validate` and `make test` prior to PRs. Additional domain-specific validators live under `src/automation/scripts/`.

## Updating Agents
- Add new roles under `agents/main-agents/` or `agents/sub-agents/` and include README, docs, SOP, prompts, workflows, and tests.
- Register routes in `agents/AGENT_REGISTRY.yaml`, then document terminology updates in `agents/SSOT.md`.
- Re-run Flow Runner dry-runs plus `make validate` to ensure contracts stay compatible.

## Contributing
Issues and pull requests are welcome. Please:
1. Describe proposed changes and affected agents/directories.
2. Link to relevant sections in `AGENTS.md` / `SSOT.md`.
3. Attach output from `make validate`, `make test`, and any Flow Runner dry-runs to the PR description.

## License
This project is licensed under the [MIT License](LICENSE).
