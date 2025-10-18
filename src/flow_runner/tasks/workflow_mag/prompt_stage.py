"""PromptSAG integration stage."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Sequence

from . import common
from .codex_mcp import CodexMCPTimeoutError, codex_usage_as_dict, get_codex_manager


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
    codex_summary: dict[str, str] | None = None

    codex_cfg = prompt_cfg.get("codex")
    if isinstance(codex_cfg, dict):
        prompt_text = codex_cfg.get("prompt")
        if prompt_text:
            policy = runtime_ctx.resolve_codex_policy("PromptSAG")
            manager = get_codex_manager(max_sessions=codex_cfg.get("max_sessions"))
            try:
                result = manager.generate(
                    prompt_text,
                    base_instructions=codex_cfg.get("base_instructions"),
                    config=codex_cfg.get("config"),
                    include_plan_tool=codex_cfg.get("include_plan_tool"),
                    model=codex_cfg.get("model") or policy.model,
                    token_limit=codex_cfg.get("prompt_limit") or policy.limit,
                    token_buffer=codex_cfg.get("prompt_buffer", policy.buffer),
                    timeout=codex_cfg.get("timeout_s") or policy.timeout_s,
                )
            except (CodexMCPTimeoutError, ValueError) as exc:
                codex_summary = {"status": "failed", "error": str(exc)}
            else:
                codex_plan_path = output_dir / "prompt_codex_plan.json"
                payload = {
                    "prompt": prompt_text,
                    "response": result.text,
                    "content": result.content,
                    "meta": result.meta,
                    "token_usage": codex_usage_as_dict(result),
                }
                codex_plan_path.write_text(
                    json.dumps(payload, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )
                runtime_ctx.register_artifacts({"prompt_codex_plan": str(codex_plan_path)})
                codex_summary = {"status": "completed", "artifact": str(codex_plan_path)}
        else:
            codex_summary = {"status": "skipped", "reason": "codex.prompt not provided"}
    else:
        codex_summary = {"status": "skipped", "reason": "codex config missing"}

    if codex_summary:
        artifact["codex"] = codex_summary
        artifact_path.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")

    runtime_ctx.register_artifacts({"prompt_package": str(artifact_path)})
    runtime_ctx.record_step(
        agent="PromptSAG",
        results=[{"status": "scaffolded", "codex": codex_summary or {}}],
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
