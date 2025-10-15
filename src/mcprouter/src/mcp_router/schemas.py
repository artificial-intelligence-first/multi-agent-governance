"""Shared schemas used by the MCP router."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Result(BaseModel):
    """Normalized response returned to synchronous callers."""

    text: str
    content: List[Dict[str, Any]] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)


class ProviderRequest(BaseModel):
    """Payload that workers forward to providers."""

    prompt: str
    model: str
    sandbox: str
    approval_policy: str
    config: Dict[str, Any] = Field(default_factory=dict)
    timeout_sec: float


class ProviderResponse(BaseModel):
    """Simplified provider output."""

    text: str
    content: List[Dict[str, Any]] = Field(default_factory=list)
    meta: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: Optional[float] = None
    token_usage: Optional[Dict[str, Any]] = None


class AuditRecord(BaseModel):
    """JSONL structure persisted in mcp_calls.jsonl."""

    ts: datetime
    model: str
    worker: Optional[str] = None
    latency_ms: float
    prompt_chars: int
    token_usage: Dict[str, Any] = Field(default_factory=dict)
    status: str
    error: Optional[str] = None


class QueueItem(BaseModel):
    """Work item stored in the in-memory queue."""

    request: ProviderRequest
    prompt_limit: int
    prompt_buffer: int
    retries: int
    prompt_chars: int
    token_estimate: Dict[str, Any] = Field(default_factory=dict)
