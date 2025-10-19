"""PromptSAG integration stage."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Sequence

from . import common
from .codex_mcp import CodexMCPTimeoutError, codex_usage_as_dict, get_codex_manager


_CODEX_OPTION_KEYS = {
    "sandbox",
    "approval_policy",
    "base_instructions",
    "config",
    "include_plan_tool",
    "model",
    "prompt_limit",
    "prompt_buffer",
    "timeout_s",
    "max_sessions",
}


def _resolve_codex_status(
    plan: dict[str, Any] | None, review: dict[str, Any] | None
) -> str | None:
    """Derive an aggregate status for Codex plan/review executions."""

    plan_status = (plan or {}).get("status")
    review_status = (review or {}).get("status")

    if plan_status == "failed":
        return "failed"
    if review_status == "failed":
        if plan_status == "completed":
            return "partial"
        return "failed"

    if plan_status is None:
        return review_status

    if plan_status == "completed":
        if review_status in (None, "completed", "skipped"):
            return "completed"
        return review_status

    if plan_status == "skipped":
        if review_status:
            if review_status == "completed":
                return "completed"
            return review_status
        return "skipped"

    return plan_status or review_status


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trigger PromptSAG stage for prompt package assembly.")
    parser.add_argument("--config", required=True, help="Workflow configuration path.")
    return parser.parse_args(argv)


def execute(config_path: str) -> Path:
    config = common.load_config(config_path)
    run_id = os.environ.get("MAG_RUN_ID", "local-run")
    runtime_ctx = common.build_runtime_context(config, run_id=run_id)
    output_dir = runtime_ctx.output_dir / "prompts"
    common.ensure_output_dir(output_dir)

    prompt_cfg = config.get("prompt", {})
    artifact = {
        "audience": prompt_cfg.get("audience", "unspecified"),
        "style": prompt_cfg.get("style", "structured"),
        "status": "awaiting PromptSAG",
        "messages": [],
    }
    artifact_path = output_dir / "prompt_package.json"
    artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    codex_cfg = prompt_cfg.get("codex")
    codex_details: dict[str, Any] = {}
    plan_summary: dict[str, Any] | None = None
    review_summary: dict[str, Any] | None = None

    def _collect_options(config: dict[str, Any] | None) -> dict[str, Any]:
        if not isinstance(config, dict):
            return {}
        return {key: config[key] for key in _CODEX_OPTION_KEYS if key in config}

    def _merged_options(base: dict[str, Any], override: dict[str, Any] | None) -> dict[str, Any]:
        options = dict(base)
        if isinstance(override, dict):
            for key in _CODEX_OPTION_KEYS:
                if key in override:
                    options[key] = override[key]
        return options

    def _to_int(value: Any, default: int) -> int:
        if value is None:
            return default
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def _to_float(value: Any, default: float | None) -> float | None:
        if value is None:
            return default
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return default
        if parsed <= 0:
            return default
        return parsed

    def _invoke_codex(
        prompt_text: str,
        *,
        options: dict[str, Any],
        artifact_name: str,
        artifact_key: str,
    ) -> dict[str, Any]:
        policy = runtime_ctx.resolve_codex_policy("PromptSAG")
        manager = get_codex_manager(max_sessions=options.get("max_sessions"))

        model = options.get("model") or policy.model

        token_limit = max(_to_int(options.get("prompt_limit"), policy.limit), 1)
        token_buffer = max(_to_int(options.get("prompt_buffer"), policy.buffer), 0)
        timeout_value = _to_float(options.get("timeout_s"), policy.timeout_s)

        try:
            result = manager.generate(
                prompt_text,
                sandbox=str(options.get("sandbox") or "read-only"),
                approval_policy=str(options.get("approval_policy") or "never"),
                base_instructions=options.get("base_instructions"),
                config=options.get("config"),
                include_plan_tool=options.get("include_plan_tool"),
                model=model,
                token_limit=token_limit,
                token_buffer=token_buffer,
                timeout=timeout_value,
            )
        except (CodexMCPTimeoutError, ValueError) as exc:
            return {"status": "failed", "error": str(exc)}

        codex_path = output_dir / artifact_name
        payload = {
            "prompt": prompt_text,
            "response": result.text,
            "content": result.content,
            "meta": result.meta,
            "token_usage": codex_usage_as_dict(result),
        }
        codex_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        runtime_ctx.register_artifacts({artifact_key: str(codex_path)})
        common.log("prompts", f"Codex output saved to {codex_path}")
        return {"status": "completed", "artifact": str(codex_path)}

    if isinstance(codex_cfg, dict):
        base_options = _collect_options(codex_cfg)
        prompt_text = codex_cfg.get("prompt")
        if prompt_text:
            plan_summary = _invoke_codex(
                prompt_text,
                options=base_options,
                artifact_name="prompt_codex_plan.json",
                artifact_key="prompt_codex_plan",
            )
        else:
            plan_summary = {"status": "skipped", "reason": "codex.prompt not provided"}

        review_cfg = codex_cfg.get("review")
        review_prompt: str | None = None
        review_options = base_options
        if isinstance(review_cfg, str):
            review_prompt = review_cfg
        elif isinstance(review_cfg, dict):
            review_prompt = review_cfg.get("prompt")
            review_options = _merged_options(base_options, review_cfg)

        if review_prompt:
            review_summary = _invoke_codex(
                review_prompt,
                options=review_options,
                artifact_name="prompt_codex_review.json",
                artifact_key="prompt_codex_review",
            )
        elif review_cfg is not None:
            review_summary = {"status": "skipped", "reason": "codex.review.prompt not provided"}
    else:
        plan_summary = {"status": "skipped", "reason": "codex config missing"}

    if plan_summary:
        codex_details["plan"] = plan_summary
    if review_summary:
        codex_details["review"] = review_summary

    if plan_summary or review_summary:
        overall_status = _resolve_codex_status(plan_summary, review_summary)
        if overall_status:
            codex_details["status"] = overall_status

    if codex_details:
        artifact["codex"] = codex_details
        artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")

    runtime_ctx.register_artifacts({"prompt_package": str(artifact_path)})
    runtime_ctx.record_step(
        agent="PromptSAG",
        results=[{"status": "scaffolded", "codex": codex_details or {}}],
        artifacts={"prompt_package": str(artifact_path)},
        metadata={"config_path": str(Path(config_path).resolve())},
    )
    common.log("prompts", f"Prompt package scaffold written to {artifact_path}")
    return artifact_path


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    execute(args.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
