from pathlib import Path

import pytest

from deps_sag import load_workflow, WORKFLOW_ROOT


def test_workflow_loader_reads_upgrade_file(tmp_path: Path) -> None:
    workflow = load_workflow("upgrade_deps.wf.yaml")
    assert workflow["version"] == 1
    assert any(step["id"] == "validation_suite" for step in workflow["steps"])


def test_workflow_loader_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        load_workflow("does-not-exist.wf.yaml")
