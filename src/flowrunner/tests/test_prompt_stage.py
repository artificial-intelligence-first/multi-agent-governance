import json

from flow_runner.tasks.workflow_mag import prompt_stage
from flow_runner.tasks.workflow_mag.codex_mcp import CodexMCPCallResult


class FakeCodexManager:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict]] = []

    def generate(self, prompt: str, **kwargs):  # type: ignore[override]
        self.calls.append((prompt, kwargs))
        return CodexMCPCallResult(
            prompt=prompt,
            text=f"response:{prompt}",
            content=[{"type": "text", "text": f"response:{prompt}"}],
            meta={"call_count": len(self.calls)},
        )


def test_prompt_stage_supports_codex_review(monkeypatch, tmp_path):
    run_id = "unit-test-run"
    monkeypatch.setenv("MAG_RUN_ID", run_id)

    output_root = tmp_path / "runs"
    config_path = tmp_path / "config.json"
    config = {
        "paths": {"output_dir": str(output_root)},
        "prompt": {
            "codex": {
                "prompt": "Create plan",
                "sandbox": "read-write",
                "approval_policy": "auto",
                "prompt_limit": 4096,
                "prompt_buffer": 128,
                "timeout_s": 9.5,
                "max_sessions": 4,
                "review": {
                    "prompt": "Review plan",
                    "sandbox": "audit",
                    "approval_policy": "manual",
                    "prompt_limit": 512,
                    "prompt_buffer": 16,
                    "timeout_s": 3.2,
                    "max_sessions": 2,
                },
            }
        },
    }
    config_path.write_text(json.dumps(config), encoding="utf-8")

    manager = FakeCodexManager()
    manager_calls: list[int | None] = []

    def fake_get_manager(*, max_sessions=None):
        manager_calls.append(max_sessions)
        return manager

    monkeypatch.setattr(prompt_stage, "get_codex_manager", fake_get_manager)

    artifact_path = prompt_stage.execute(str(config_path))

    prompt_package = json.loads(artifact_path.read_text(encoding="utf-8"))
    codex_summary = prompt_package["codex"]

    assert codex_summary["status"] == "completed"
    assert codex_summary["plan"]["status"] == "completed"
    assert codex_summary["review"]["status"] == "completed"

    prompts_dir = artifact_path.parent
    plan_path = prompts_dir / "prompt_codex_plan.json"
    review_path = prompts_dir / "prompt_codex_review.json"
    assert plan_path.exists()
    assert review_path.exists()

    plan_payload = json.loads(plan_path.read_text(encoding="utf-8"))
    review_payload = json.loads(review_path.read_text(encoding="utf-8"))
    assert plan_payload["prompt"] == "Create plan"
    assert review_payload["prompt"] == "Review plan"

    summary_path = output_root / "summary.json"
    assert summary_path.exists()
    summary_payload = json.loads(summary_path.read_text(encoding="utf-8"))
    artifacts = summary_payload["artifacts"]
    assert artifacts["prompt_codex_plan"] == str(plan_path.resolve())
    assert artifacts["prompt_codex_review"] == str(review_path.resolve())

    # Manager invoked twice with distinct overrides.
    assert [call[0] for call in manager.calls] == ["Create plan", "Review plan"]
    plan_kwargs = manager.calls[0][1]
    review_kwargs = manager.calls[1][1]
    assert plan_kwargs["sandbox"] == "read-write"
    assert review_kwargs["sandbox"] == "audit"
    assert plan_kwargs["approval_policy"] == "auto"
    assert review_kwargs["approval_policy"] == "manual"
    assert plan_kwargs["token_limit"] == 4096
    assert review_kwargs["token_limit"] == 512
    assert plan_kwargs["token_buffer"] == 128
    assert review_kwargs["token_buffer"] == 16

    # The codex manager honours per-call max session overrides.
    assert manager_calls == [4, 2]

    step_path = output_root / "steps" / "PromptSAG.json"
    assert step_path.exists()
    step_payload = json.loads(step_path.read_text(encoding="utf-8"))
    assert step_payload["results"][0]["codex"]["status"] == "completed"
