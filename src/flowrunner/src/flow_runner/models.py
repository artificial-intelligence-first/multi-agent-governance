"""Data models for flow definitions and runtime artifacts."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator


class RunConfig(BaseModel):
    """Per-run configuration extracted from the flow file."""

    output_dir: str = Field(default="./.runs/${RUN_ID}")


class StepBase(BaseModel):
    """Shared attributes for all step types."""

    id: str
    uses: str
    continue_on_error: bool = False
    timeout_sec: int = 60
    retries: int = 0
    depends_on: List[str] = Field(default_factory=list)


class ShellStepSpec(StepBase):
    """Shell execution step."""

    uses: Literal["shell"]
    run: str


class McpInputSpec(BaseModel):
    """Input configuration for MCP steps."""

    prompt: Optional[str] = None
    prompt_from: Optional[str] = None
    variables: Dict[str, str] = Field(default_factory=dict)


class McpPolicySpec(BaseModel):
    """Policy block for MCP steps."""

    model: str
    prompt_limit: int
    prompt_buffer: int
    sandbox: Literal["read-only", "read-write"]


class McpSaveSpec(BaseModel):
    """Artifact persistence options for MCP steps."""

    text: Optional[str] = None


class McpStepSpec(StepBase):
    """MCP invocation step."""

    uses: Literal["mcp"]
    input: McpInputSpec
    policy: McpPolicySpec
    config: Dict[str, Any] = Field(default_factory=dict)
    save: Optional[McpSaveSpec] = None


class AgentStepSpec(StepBase):
    """Dynamically loaded agent step using module:Class syntax."""

    uses: str
    input: Dict[str, Any] = Field(default_factory=dict)
    config: Dict[str, Any] = Field(default_factory=dict)
    model_config = ConfigDict(extra="allow")

    @field_validator("uses")
    @classmethod
    def _validate_uses(cls, value: str) -> str:
        if ":" not in value:
            raise ValueError('external agent steps must declare uses as "module:ClassName"')
        return value


StepSpec = RootModel[List[ShellStepSpec | McpStepSpec | AgentStepSpec]]


class FlowDefinition(BaseModel):
    """Top-level flow document."""

    version: Literal[1]
    run: RunConfig = Field(default_factory=RunConfig)
    agent_paths: List[str] = Field(default_factory=list)
    steps: StepSpec


class RunEvent(BaseModel):
    """Structure persisted to runs.jsonl."""

    ts: datetime
    run_id: str
    step: str
    event: Literal["start", "end", "error"]
    status: Literal["ok", "fail"]
    latency_ms: Optional[float] = None
    retries: int
    attempt: int
    extra: Dict[str, Any] = Field(default_factory=dict)


class StepSummary(BaseModel):
    """Aggregated metrics for a single step."""

    ok: int = 0
    fail: int = 0
    p50_ms: float = 0.0
    p95_ms: float = 0.0


class StepFailure(BaseModel):
    """Details about a step failure recorded during execution."""

    error: str = ""
    fatal: bool = True


class RunSummary(BaseModel):
    """Aggregated metrics persisted to summary.json."""

    run_id: str
    steps: Dict[str, StepSummary]
    started_at: datetime
    finished_at: datetime
    failures: Dict[str, StepFailure] = Field(default_factory=dict)


def compute_percentile(samples: List[float], percentile: float) -> float:
    """Compute a percentile using the nearest-rank strategy."""

    if not samples:
        return 0.0
    ordered = sorted(samples)
    rank = max(1, int(round(percentile / 100 * len(ordered))))
    index = min(rank - 1, len(ordered) - 1)
    return float(ordered[index])
