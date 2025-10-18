from __future__ import annotations

import pytest

pytest.importorskip("mcp")

from flow_runner.tasks.workflow_mag.codex_mcp import CodexMCPManager


def test_codex_manager_raises_when_command_missing() -> None:
    with pytest.raises(RuntimeError):
        CodexMCPManager(command="__codex_missing__", args=["mcp"])
