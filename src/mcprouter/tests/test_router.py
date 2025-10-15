import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import pytest
from mcp_router.providers.base import BaseProvider, ProviderError
from mcp_router.router import MCPRouter, PromptLimitExceeded
from mcp_router.schemas import ProviderRequest, ProviderResponse


class FlakyProvider(BaseProvider):
    """Provider that fails once before succeeding."""

    def __init__(self) -> None:
        self.calls = 0

    async def agenerate(self, payload: ProviderRequest) -> ProviderResponse:
        self.calls += 1
        if self.calls == 1:
            raise ProviderError("transient", retriable=True)
        return ProviderResponse(text="ok", meta={"provider": "flaky"})


@pytest.fixture(autouse=True)
def reset_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("MCP_MAX_SESSIONS", "1")


def _default_kwargs() -> dict[str, Any]:
    return {
        "prompt": "Describe the system briefly.",
        "model": "test-model",
        "prompt_limit": 8096,
        "prompt_buffer": 512,
        "sandbox": "read-only",
        "approval_policy": "never",
        "config": {"temperature": 0.0},
    }


def _read_json_lines(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_dummy_provider_roundtrip(tmp_path: Path) -> None:
    router = MCPRouter.from_env(log_dir=tmp_path)
    with router:
        result = router.generate(**_default_kwargs())
    assert "dummy-provider" in result.text
    assert "token_usage" in result.meta
    audit_path = tmp_path / "mcp_calls.jsonl"
    log_lines = audit_path.read_text(encoding="utf-8").strip().splitlines()
    assert log_lines, "expected audit log entries"
    entry = json.loads(log_lines[-1])
    assert entry["status"] == "ok"
    assert entry["worker"] == "worker-0"
    assert "token_usage" in entry


def test_prompt_limit_enforced(tmp_path: Path) -> None:
    router = MCPRouter.from_env(log_dir=tmp_path)
    with router:
        with pytest.raises(PromptLimitExceeded):
            router.generate(
                prompt="x" * 10_000,
                model="test-model",
                prompt_limit=100,
                prompt_buffer=10,
                sandbox="read-only",
                approval_policy="never",
            )
    log_entries = _read_json_lines(tmp_path / "mcp_calls.jsonl")
    assert any(entry["status"] == "prompt_limit_exceeded" for entry in log_entries)


def test_retry_and_success(tmp_path: Path) -> None:
    provider = FlakyProvider()
    router = MCPRouter(
        provider,
        max_sessions=1,
        request_timeout=1.0,
        max_retries=2,
        backoff_base=0.01,
        log_dir=tmp_path,
    )
    with router:
        result = router.generate(**_default_kwargs())
    assert result.text == "ok"
    assert provider.calls == 2
    entries = _read_json_lines(tmp_path / "mcp_calls.jsonl")
    statuses = [entry["status"] for entry in entries]
    assert "error" in statuses and "ok" in statuses


def test_multiple_workers_receive_load(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MCP_MAX_SESSIONS", "2")
    router = MCPRouter.from_env(log_dir=tmp_path)
    with router:
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [
                pool.submit(
                    router.generate,
                    prompt=f"prompt {i}",
                    model="test-model",
                    prompt_limit=8096,
                    prompt_buffer=512,
                    sandbox="read-only",
                    approval_policy="never",
                )
                for i in range(4)
            ]
            for future in futures:
                future.result()
    audit_path = tmp_path / "mcp_calls.jsonl"
    workers = {
        json.loads(line)["worker"]
        for line in audit_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    assert workers >= {"worker-0", "worker-1"}
