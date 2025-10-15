"""QAMAG stub for testability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class QAMAG:
    """Return basic QA findings structure."""

    def run(self, checklist: List[str] | None = None) -> Dict[str, Any]:
        checklist = checklist or []
        return {
            "agent": "qa-mag",
            "status": "review-pending",
            "checklist": checklist,
            "findings": [],
        }

    __call__ = run
