"""OpenAI provider implementation."""

from __future__ import annotations

import httpx

from ..schemas import ProviderRequest, ProviderResponse
from .base import BaseProvider, ProviderError

OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider(BaseProvider):
    """Lightweight wrapper around the OpenAI responses endpoint."""

    name = "openai"

    def __init__(self, api_key: str) -> None:
        if not api_key:
            raise ValueError("api_key must be provided for OpenAIProvider")
        self._api_key = api_key
        self._client = httpx.AsyncClient()

    async def agenerate(self, payload: ProviderRequest) -> ProviderResponse:
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        request_body = {
            "model": payload.model,
            "messages": [{"role": "user", "content": payload.prompt}],
            "temperature": payload.config.get("temperature", 0.0),
        }
        try:
            response = await self._client.post(
                OPENAI_ENDPOINT,
                headers=headers,
                json=request_body,
                timeout=payload.timeout_sec,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:  # pragma: no cover - network not exercised in tests
            raise ProviderError(str(exc), retriable=True) from exc

        data = response.json()
        choices = data.get("choices") or []
        text = ""
        if choices:
            message = choices[0].get("message") or {}
            candidate = message.get("content")
            if isinstance(candidate, str):
                text = candidate
        usage = data.get("usage") or {}
        latency_ms = None
        if response.elapsed is not None:
            latency_ms = response.elapsed.total_seconds() * 1000
        return ProviderResponse(
            text=text,
            content=choices,
            meta={"provider": self.name, "raw": data},
            latency_ms=latency_ms,
            token_usage=usage,
        )

    async def aclose(self) -> None:
        await self._client.aclose()
