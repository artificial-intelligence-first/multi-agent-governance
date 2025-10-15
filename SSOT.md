# Multi Agent Governance Single Source of Truth

This repository maintains agent-level terminology, contracts, and governance guidance under `agents/SSOT.md`. The top-level note clarifies how the specifications published by the artificial-intelligence-first **agents** and **flow-runner** projects are composed inside the Multi Agent Governance repository.

## Scope
- Applies to every agent under `agents/` (main, sub, and shared components).
- Covers JSON schemas, glossary entries, upstream/downstream integrations, and operational playbooks.

## Specification Baselines
- Agents Directory open specification: https://github.com/artificial-intelligence-first/agents-directory (repository layout, governance workflow, and vocabulary synchronized as of October 12, 2025).
- Flow Runner workflow specification: https://github.com/artificial-intelligence-first/flow-runner (YAML workflow schema and runtime behaviour mirrored via vendored packages in `src/flowrunner/` and `src/mcprouter/`, synced to commit 477db9c4ae364e30348de58acb29b95e0e5597fa on October 12, 2025).

## How to Use
1. Review `agents/SSOT.md` before editing prompts, workflows, or contracts.
2. Record any new terminology, schema versions, or dependency changes there as part of your change set.
3. Keep examples and validation scripts in sync (`make validate`), ensuring contracts stay compatible with Flow Runner executions.

For detailed change-management procedures and glossary definitions, consult `agents/SSOT.md` directly.
