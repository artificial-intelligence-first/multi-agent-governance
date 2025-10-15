"""Legacy localization agent shim retained for compatibility imports."""

from __future__ import annotations

from typing import Any, Dict


class LocalizationSAG:
    """Localization is no longer supported; invoking this class raises an error."""

    def __init__(self, locale: str | None = None) -> None:
        self.locale = locale or "en-US"

    def run(self, summary: str, **kwargs: Any) -> Dict[str, Any]:  # pragma: no cover - legacy path
        raise RuntimeError(
            "LocalizationSAG has been retired; translation workflows are no longer available."
        )

    __call__ = run
