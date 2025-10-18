from __future__ import annotations

from pathlib import Path

import pytest

from mcp_router.config import load_settings


@pytest.fixture()
def tmp_config_dir(tmp_path: Path) -> Path:
    config_dir = tmp_path / ".mcp"
    config_dir.mkdir()
    env_file = config_dir / ".env.mcp"
    env_file.write_text("", encoding="utf-8")
    config_file = config_dir / ".mcp-config.yaml"
    config_file.write_text(
        """
servers:
  context7:
    transport: http
    url: ${CONTEXT7_MCP_URL:-https://mcp.context7.com/mcp}
    headers:
      CONTEXT7_API_KEY: ${CONTEXT7_API_KEY:-}
    metadata:
      api_url: ${CONTEXT7_API_URL:-https://context7.com/api/v1}
""",
        encoding="utf-8",
    )
    return tmp_path


def test_context7_headers_pruned_when_missing(tmp_config_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONTEXT7_API_KEY", raising=False)
    settings = load_settings(base_dir=tmp_config_dir)
    headers = settings["servers"]["context7"].get("headers")
    assert headers == {}


def test_context7_headers_retained_when_set(tmp_config_dir: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CONTEXT7_API_KEY", "ctx-secret")
    settings = load_settings(base_dir=tmp_config_dir)
    headers = settings["servers"]["context7"].get("headers")
    assert headers == {"CONTEXT7_API_KEY": "ctx-secret"}
