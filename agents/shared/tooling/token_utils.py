"""Token counting helpers used by Codex-aware stages.

These utilities keep Codex / MCP prompts within budget so Flow Runner
can reject oversized plans before handing them to the runtime.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from functools import lru_cache

import tiktoken

_FALLBACK_ENCODING = "cl100k_base"


@lru_cache(maxsize=32)
def _encoding_for(model: str) -> tiktoken.Encoding:
    """Return a cached encoding object for the given model name."""

    try:
        return tiktoken.encoding_for_model(model)
    except KeyError:
        return tiktoken.get_encoding(_FALLBACK_ENCODING)


def count_tokens(text: str, *, model: str) -> int:
    """Count tokens for a piece of text using the specified model."""

    encoding = _encoding_for(model)
    return len(encoding.encode(text, disallowed_special=()))


def count_messages(messages: Sequence[str], *, model: str) -> int:
    """Return total tokens for concatenated message strings."""

    return sum(count_tokens(message, model=model) for message in messages)


@dataclass(slots=True)
class TokenUsage:
    """Simple structure capturing token counts and remaining budget."""

    tokens: int
    limit: int
    buffer: int = 0

    @property
    def effective_limit(self) -> int:
        return max(self.limit - self.buffer, 0)

    @property
    def remaining(self) -> int:
        return max(self.effective_limit - self.tokens, 0)

    @property
    def exceeded(self) -> bool:
        return self.tokens > self.effective_limit


def ensure_within_limit(text: str, *, model: str, limit: int, buffer: int = 0) -> TokenUsage:
    """Return token usage information applying an optional safety buffer."""

    usage = count_tokens(text, model=model)
    return TokenUsage(tokens=usage, limit=limit, buffer=max(buffer, 0))


def chunk_text(
    text: str,
    *,
    model: str,
    limit: int,
    overlap: int = 0,
) -> list[str]:
    """Split text into token-safe chunks preserving order."""

    if limit <= 0:
        raise ValueError("limit must be positive")
    if overlap < 0:
        raise ValueError("overlap must be zero or positive")
    if overlap >= limit:
        raise ValueError("overlap must be smaller than limit")

    encoding = _encoding_for(model)
    tokens = encoding.encode(text, disallowed_special=())
    if not tokens:
        return [""]

    chunks: list[str] = []
    start = 0
    step = limit - overlap
    while start < len(tokens):
        end = min(start + limit, len(tokens))
        chunk = encoding.decode(tokens[start:end])
        chunks.append(chunk)
        if end == len(tokens):
            break
        start += step
    return chunks


def summarise_usage(messages: Iterable[str], *, model: str, limit: int) -> tuple[int, TokenUsage]:
    """Aggregate token counts for multiple messages and return summary info."""

    total_tokens = count_messages(list(messages), model=model)
    usage = TokenUsage(tokens=total_tokens, limit=limit)
    return total_tokens, usage


__all__ = [
    "TokenUsage",
    "chunk_text",
    "count_messages",
    "count_tokens",
    "ensure_within_limit",
    "summarise_usage",
]
