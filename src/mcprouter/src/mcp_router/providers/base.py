"""Abstract provider interface."""

from __future__ import annotations

import abc
from typing import Dict

from ..schemas import ProviderRequest, ProviderResponse


class BaseProvider(abc.ABC):
    """Common interface for all providers."""

    name: str = "base"

    @abc.abstractmethod
    async def agenerate(self, payload: ProviderRequest) -> ProviderResponse:
        """Perform the asynchronous completion call."""

    @staticmethod
    def approx_token_usage(prompt: str) -> Dict[str, int]:
        """Estimate token usage with a conservative heuristic."""

        ascii_chars = sum(1 for ch in prompt if ord(ch) < 128)
        other_chars = len(prompt) - ascii_chars
        approx_tokens = (ascii_chars + 3) // 4 + ((other_chars * 2) + 3) // 4
        approx_tokens = max(1, approx_tokens)
        return {"tokens": approx_tokens}


class ProviderError(RuntimeError):
    """Error raised when a provider cannot fulfill a request."""

    def __init__(self, message: str, *, retriable: bool = False) -> None:
        super().__init__(message)
        self.retriable = retriable
