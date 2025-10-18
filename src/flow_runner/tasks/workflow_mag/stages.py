"""Flow Runner stage stubs compatible with `uses` syntax."""

from __future__ import annotations

import os
from typing import Any, Dict

from . import (
    orchestrate,
    browser_stage,
    docs_stage,
    prompt_stage,
    context_stage,
    qa_stage,
    operations_stage,
    governance_stage,
    finalize_stage,
)


class _BaseStage:
    """Provide Flow Runner agent-compatible interface."""

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        return self.__call__(**kwargs)


def _config_from_kwargs(kwargs: Dict[str, Any]) -> str:
    return kwargs.get("config") or os.environ.get("WORKFLOW_CONFIG", "runtime/automation/workflows/configs/workflow-mag/base.json")


class PlanStage(_BaseStage):
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        config = _config_from_kwargs(kwargs)
        path = orchestrate.execute(config)
        return {"stage": "plan", "status": "completed", "artifact": str(path)}


class DocsStage(_BaseStage):
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        config = _config_from_kwargs(kwargs)
        path = docs_stage.execute(config)
        return {"stage": "docs", "status": "completed", "artifact": str(path)}


class PromptsStage(_BaseStage):
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        config = _config_from_kwargs(kwargs)
        path = prompt_stage.execute(config)
        return {"stage": "prompts", "status": "completed", "artifact": str(path)}


class ContextStage(_BaseStage):
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        config = _config_from_kwargs(kwargs)
        path = context_stage.execute(config)
        return {"stage": "context", "status": "completed", "artifact": str(path)}


class QAStage(_BaseStage):
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        config = _config_from_kwargs(kwargs)
        path = qa_stage.execute(config)
        return {"stage": "qa", "status": "completed", "artifact": str(path)}


class OperationsStage(_BaseStage):
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        config = _config_from_kwargs(kwargs)
        path = operations_stage.execute(config)
        return {"stage": "operations", "status": "completed", "artifact": str(path)}


class GovernanceStage(_BaseStage):
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        config = _config_from_kwargs(kwargs)
        path = governance_stage.execute(config)
        return {"stage": "governance", "status": "completed", "artifact": str(path)}


class FinalizeStage(_BaseStage):
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        config = _config_from_kwargs(kwargs)
        path = finalize_stage.execute(config)
        return {"stage": "finalize", "status": "completed", "artifact": str(path)}
class BrowserStage(_BaseStage):
    def __call__(self, **kwargs: Any) -> Dict[str, Any]:
        config = _config_from_kwargs(kwargs)
        path = browser_stage.execute(config)
        return {"stage": "browser", "status": "completed", "artifact": str(path)}
