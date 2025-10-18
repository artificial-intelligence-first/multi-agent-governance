# WorkFlowMAG Overview

WorkFlowMAG orchestrates the Multi Agent Governance pipeline. It ensures that:

1. Pre-task compliance (`automation.compliance.pre`) succeeds before any run.
2. Flow Runner executes the configured stages defined in `workflow_mag.flow.yaml`.
3. Each stage writes artefacts back to `telemetry/runs/<run_id>` for review by humans and downstream agents.
4. PLANS.md and `/docs/task_template.md` remain current with stage updates and findings.

Use this document as the quick primer when onboarding new operators.
