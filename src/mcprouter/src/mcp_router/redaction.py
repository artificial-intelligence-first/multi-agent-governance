"""Utilities for masking sensitive fields in telemetry payloads."""

from __future__ import annotations

from typing import Any

SENSITIVE_KEYWORDS: tuple[str, ...] = (
    "api_key",
    "apikey",
    "authorization",
    "secret",
    "password",
    "bearer",
)


def mask_sensitive(value: Any) -> Any:
    """Recursively replace values for keys that appear sensitive."""

    if isinstance(value, dict):
        masked: dict[str, Any] = {}
        for key, item in value.items():
            if any(token in key.lower() for token in SENSITIVE_KEYWORDS):
                masked[key] = "***"
            else:
                masked[key] = mask_sensitive(item)
        return masked
    if isinstance(value, list):
        return [mask_sensitive(item) for item in value]
    return value


__all__ = ["mask_sensitive", "SENSITIVE_KEYWORDS"]
