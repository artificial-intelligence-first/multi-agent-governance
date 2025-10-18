from __future__ import annotations

import json
from pathlib import Path

from flow_runner.tasks.workflow_mag import browser_stage


def test_browser_stage_generates_plan(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "task": {"name": "workflow-mag-browser"},
                "paths": {
                    "output_dir": str(tmp_path / "runs/${RUN_ID}"),
                    "logs_dir": str(tmp_path / "logs/${RUN_ID}"),
                },
                "browser": {
                    "targets": ["https://example.com"],
                    "mcp_servers": [
                        "chrome-devtools",
                        "playwright",
                        "markitdown",
                    ],
                    "expected_artifacts": ["screenshots", "markdown_exports"],
                    "instructions": ["Capture homepage and convert summary."],
                },
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("MAG_RUN_ID", "browser-test")
    artifact_path = browser_stage.execute(str(config_path))

    payload = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert payload["run_id"] == "browser-test"
    assert payload["mcp_servers"] == [
        "chrome-devtools",
        "playwright",
        "markitdown",
    ]
    assert payload["targets"] == ["https://example.com"]
    assert payload["expected_artifacts"] == ["screenshots", "markdown_exports"]

    run_dir = tmp_path / "runs" / "browser-test"
    step_log = run_dir / "steps" / "BrowserSAG.json"
    assert step_log.exists()

    with step_log.open(encoding="utf-8") as handle:
        step_payload = json.load(handle)
    assert step_payload["agent"] == "BrowserSAG"
    assert step_payload["artifacts"]["browser_plan"] == str(artifact_path.resolve())
