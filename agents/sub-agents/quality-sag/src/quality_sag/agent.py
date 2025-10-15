"""QualitySAG stub."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class QualitySAG:
    """Return findings about plan consistency."""

    def run(self, issues: List[str] | None = None) -> Dict[str, Any]:
        issues = issues or []
        return {
            "agent": "quality-sag",
            "status": "reviewed",
            "issues": issues,
        }

    __call__ = run
