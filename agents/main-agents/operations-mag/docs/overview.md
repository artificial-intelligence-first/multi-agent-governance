# OperationsMAG Overview

OperationsMAG coordinates observability for WorkFlowMAG runs. It ensures that:

1. Telemetry budgets across documentation, prompt, context, and QA stages remain within SSOT limits.
2. Logs adhere to the naming and retention policies documented in AGENTS.md.
3. Escalations are routed to the configured `escalation_channel` in `agents/AGENT_REGISTRY.yaml` when anomalies appear.
