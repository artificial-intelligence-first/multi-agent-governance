"""Deterministic provider used when no external key is available."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Any

from ..schemas import ProviderRequest, ProviderResponse
from .base import BaseProvider


class DummyProvider(BaseProvider):
    """Echo-based provider for offline execution and testing."""

    name = "dummy"

    async def agenerate(self, payload: ProviderRequest) -> ProviderResponse:
        await asyncio.sleep(0.01)
        prompt_preview = payload.prompt[:160]
        text = (
            "[dummy-provider]\n"
            f"model={payload.model}\n"
            f"sandbox={payload.sandbox}\n"
            f"approval_policy={payload.approval_policy}\n"
            f"generated_at={datetime.now(UTC).isoformat().replace('+00:00', 'Z')}\n"
            "--- prompt preview ---\n"
            f"{prompt_preview}"
        )
        token_usage = {"tokens": {"input": 0, "output": 0, "total": 0}}
        meta: dict[str, Any] = {
            "provider": self.name,
            "config": payload.config,
            "token_usage": token_usage,
        }
        return ProviderResponse(
            text=text,
            content=[],
            meta=meta,
            latency_ms=10.0,
            token_usage=token_usage,
        )
