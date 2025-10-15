"""Implementation of the mcp step."""

from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, cast

from flow_runner.models import McpStepSpec

from .base import BaseStep, ExecutionContext, StepExecutionError


class McpStep(BaseStep):
    """Invokes MCPRouter synchronously through a background thread."""

    def _resolve_prompt(self, context: ExecutionContext) -> str:
        spec = cast(McpStepSpec, self.spec)
        assert hasattr(spec, "input")
        input_block = spec.input
        if input_block.prompt is not None:
            template = input_block.prompt
        elif input_block.prompt_from is not None:
            configured_path = Path(input_block.prompt_from).expanduser()
            candidates = []
            if configured_path.is_absolute():
                candidates.append(configured_path)
            else:
                candidates.append((context.flow_dir / configured_path).resolve())
                candidates.append((context.workspace_dir / configured_path).resolve())
            prompt_path = next((candidate for candidate in candidates if candidate.exists()), None)
            if prompt_path is None:
                raise StepExecutionError(f"prompt template not found: {configured_path}")
            template = prompt_path.read_text(encoding="utf-8")
        else:
            raise StepExecutionError("either prompt or prompt_from must be provided")
        variables: Dict[str, Any] = {
            "run_id": context.run_id,
            "run_dir": str(context.run_dir),
            "artifacts_dir": str(context.artifacts_dir),
        }
        for key, value in input_block.variables.items():
            variables[key] = self._resolve_variable(context, value)
        try:
            return template.format(**variables)
        except KeyError as exc:
            missing_key = exc.args[0]
            raise StepExecutionError(
                f"missing variable for prompt template: {missing_key}"
            ) from exc

    async def run(self, context: ExecutionContext) -> Dict[str, Any]:
        if context.mcp_router is None:
            raise StepExecutionError("mcp router is not initialized")
        spec = cast(McpStepSpec, self.spec)
        prompt = self._resolve_prompt(context)

        def _call_generate() -> Any:
            provider_config = dict(spec.config)
            router_retries = provider_config.pop("router_retries", None)
            kwargs: Dict[str, Any] = {
                "prompt": prompt,
                "model": spec.policy.model,
                "prompt_limit": spec.policy.prompt_limit,
                "prompt_buffer": spec.policy.prompt_buffer,
                "sandbox": spec.policy.sandbox,
                "approval_policy": "never",
                "config": provider_config,
                "timeout_sec": spec.timeout_sec,
            }
            if isinstance(router_retries, int) and router_retries >= 0:
                kwargs["retries"] = router_retries
            return context.mcp_router.generate(**kwargs)

        result = await asyncio.to_thread(_call_generate)
        save_meta: Dict[str, Any] = {}
        if spec.save and spec.save.text:
            target = Path(spec.save.text)
            if not target.is_absolute():
                target = (context.run_dir / target).resolve()
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(result.text, encoding="utf-8")
            save_meta["saved_text"] = str(target)
        return {
            "provider": result.meta.get("provider"),
            "token_usage": result.meta.get("token_usage"),
            "latency_ms": result.meta.get("latency_ms"),
            "save": save_meta,
        }

    @staticmethod
    def _resolve_variable(context: ExecutionContext, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        if McpStep._is_path_like(value):
            candidate = Path(value).expanduser()
            if candidate.is_absolute():
                return str(candidate)
            # Prefer run directory; fall back to flow/workspace if explicitly available
            run_candidate = (context.run_dir / candidate).resolve()
            if run_candidate.exists():
                return str(run_candidate)
            flow_candidate = (context.flow_dir / candidate).resolve()
            if flow_candidate.exists():
                return str(flow_candidate)
            workspace_candidate = (context.workspace_dir / candidate).resolve()
            if workspace_candidate.exists():
                return str(workspace_candidate)
            return str(run_candidate)
        return value

    @staticmethod
    def _is_path_like(raw: str) -> bool:
        if not raw:
            return False
        raw = raw.strip()
        if not raw:
            return False
        lowered = raw.lower()
        if lowered.startswith(("http://", "https://")):
            return False
        if lowered.startswith(("~", "./", "../")):
            return True
        if raw.startswith(os.sep) or raw.startswith("\\"):
            return True
        if len(raw) >= 2 and raw[1] == ":" and raw[0].isalpha():
            return True
        if raw.startswith(".") and len(raw) > 1 and raw[1].isalpha():
            return True
        if any(sep in raw for sep in (os.sep, "/", "\\")):
            return True
        suffix = Path(raw).suffix
        if suffix:
            stem = Path(raw).stem
            normalized = stem.replace("-", "").replace("_", "")
            if stem and any(ch.isalpha() for ch in stem):
                return True
            if normalized and not normalized.isdigit():
                return True
        return False
