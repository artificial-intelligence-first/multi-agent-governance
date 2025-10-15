"""WorkFlowMAG orchestration stub.

The concrete orchestration logic is executed via Flow Runner tasks under
`src/flow_runner/tasks/workflow_mag`. This agent exposes a lightweight entry
point for integrations that expect a callable class.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class WorkFlowMAG:
    """Minimal interface for orchestrating the Multi Agent Governance pipeline."""

    def run(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        payload = payload or {}
        return {
            "agent": "workflow-mag",
            "status": "delegated",
            "message": "Use Flow Runner to execute workflow_mag.flow.yaml.",
            "received_payload": payload,
        }

    def __call__(self, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
        return self.run(payload)


def artifact_path(run_id: str, relative_path: str) -> Path:
    """Utility exposed for tests to reference pipeline artefacts."""

    return Path(".runs") / run_id / relative_path
