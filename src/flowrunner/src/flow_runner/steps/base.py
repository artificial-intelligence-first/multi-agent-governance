"""Base primitives for flow steps."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from flow_runner.models import StepBase

if TYPE_CHECKING:  # pragma: no cover
    from mcp_router import MCPRouter


@dataclass
class ExecutionContext:
    """Runtime context passed to each step."""

    run_id: str
    run_dir: Path
    artifacts_dir: Path
    workspace_dir: Path
    flow_dir: Path
    mcp_log_dir: Path
    run_env: Dict[str, str] = field(default_factory=dict)
    mcp_router: Optional["MCPRouter"] = None


class StepExecutionError(RuntimeError):
    """Raised when a step fails irrecoverably."""


class BaseStep:
    """Interface implemented by all concrete steps."""

    def __init__(self, spec: StepBase) -> None:
        self.spec = spec

    async def run(self, context: ExecutionContext) -> Dict[str, Any]:
        """Execute the step and return metadata for logging."""

        raise NotImplementedError

    @property
    def id(self) -> str:
        return self.spec.id

    @property
    def retries(self) -> int:
        return self.spec.retries

    @property
    def timeout(self) -> int:
        return self.spec.timeout_sec

    @property
    def continue_on_error(self) -> bool:
        return self.spec.continue_on_error

    @property
    def dependencies(self) -> list[str]:
        return list(self.spec.depends_on)
