"""Dynamic agent loader step."""

from __future__ import annotations

import asyncio
import inspect
from importlib import import_module
from typing import Any, Dict, cast

from flow_runner.models import AgentStepSpec

from .base import BaseStep, ExecutionContext, StepExecutionError


class AgentStep(BaseStep):
    """Loads an agent class via module:Class notation and executes it."""

    async def run(self, context: ExecutionContext) -> Dict[str, Any]:
        spec = cast(AgentStepSpec, self.spec)
        module_name, _, class_name = spec.uses.partition(":")
        if not module_name or not class_name:
            raise StepExecutionError(f"invalid agent specification: {spec.uses}")
        module = self._import_agent_module(module_name)
        cls = self._resolve_agent_class(module, class_name)
        config = dict(spec.config or {})
        agent, configured = self._instantiate_agent(cls, config)
        if not hasattr(agent, "run"):
            raise StepExecutionError(f"agent {class_name} does not define a run method")
        runner = agent.run
        if not callable(runner):
            raise StepExecutionError(f"agent {class_name} run attribute is not callable")
        kwargs = dict(spec.input or {})
        if config and not configured and "config" not in kwargs:
            kwargs["config"] = config
        signature = inspect.signature(runner)
        accepts_context = "context" in signature.parameters or any(
            param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values()
        )
        if accepts_context and "context" not in kwargs:
            kwargs["context"] = context
        if inspect.iscoroutinefunction(runner):
            result = await runner(**kwargs)
        else:
            result = await asyncio.to_thread(runner, **kwargs)
        if result is None:
            return {}
        if isinstance(result, dict):
            return result
        return {"result": result}

    @staticmethod
    def _import_agent_module(module_name: str):
        try:
            return import_module(module_name)
        except ModuleNotFoundError as exc:
            raise StepExecutionError(f"agent module not found: {module_name}") from exc

    @staticmethod
    def _resolve_agent_class(module: object, class_name: str):
        try:
            return getattr(module, class_name)
        except AttributeError as exc:
            raise StepExecutionError(f"agent class not found: {class_name}") from exc

    @staticmethod
    def _instantiate_agent(agent_cls: type, config: Dict[str, Any]) -> tuple[Any, bool]:
        if not config:
            return agent_cls(), False
        init_signature = inspect.signature(agent_cls.__init__)
        accepts_kwargs = any(
            param.kind == inspect.Parameter.VAR_KEYWORD
            for param in init_signature.parameters.values()
        )
        configurable_keys = {
            name
            for name, param in init_signature.parameters.items()
            if name != "self"
            and param.kind
            in {inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY}
        }
        can_instantiate_with_config = accepts_kwargs or set(config).issubset(configurable_keys)
        if can_instantiate_with_config:
            try:
                return agent_cls(**config), True
            except TypeError:
                # Fall back to default instantiation and pass config to run.
                return agent_cls(), False
        return agent_cls(), False
