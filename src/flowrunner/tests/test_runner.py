import json
import os
import shlex
import subprocess
import sys
from pathlib import Path

import pytest
from flow_runner.cli import _extract_tokens, app
from flow_runner.models import McpStepSpec, RunEvent
from flow_runner.runner import FlowRunner, load_flow_from_path
from flow_runner.steps.base import ExecutionContext, StepExecutionError
from flow_runner.steps.mcp import McpStep
from typer.testing import CliRunner


@pytest.fixture(autouse=True)
def set_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("FLOWCTL_BASE_OUTPUT_DIR", str(tmp_path / ".runs"))
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def _write_flow(path: Path, data: dict) -> None:
    import yaml

    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle)


def _load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _cli_env() -> dict[str, str]:
    env = dict(os.environ)
    extras = [
        str(Path(__file__).resolve().parents[4] / "packages" / "flowrunner" / "src"),
        str(Path(__file__).resolve().parents[4] / "packages" / "mcprouter" / "src"),
    ]
    existing = env.get("PYTHONPATH")
    components = [path for path in extras if path]
    if existing:
        components.append(existing)
    env["PYTHONPATH"] = os.pathsep.join(components)
    return env


def test_load_flow_skip_schema_validation(tmp_path: Path) -> None:
    flow_path = tmp_path / "schema_skip.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "$schema": "./missing-schema.json",
            "steps": [],
        },
    )
    with pytest.raises(FileNotFoundError):
        load_flow_from_path(flow_path)
    flow = load_flow_from_path(flow_path, skip_schema_validation=True)
    assert flow.version == 1
    assert flow.steps.root == []


def test_flow_runner_respects_flush_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    flow_path = tmp_path / "flush.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "solo",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} -c \"print('ok')\"",
                }
            ],
        },
    )
    monkeypatch.setenv("FLOWCTL_LOG_FLUSH_EVERY", "25")
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    assert runner._log_flush_every == 25


def test_flow_runner_flush_default_buffers(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FLOWCTL_LOG_FLUSH_EVERY", raising=False)
    flow_path = tmp_path / "flush_default.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "solo",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} -c \"print('ok')\"",
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    assert runner._log_flush_every == 50


def test_flow_runner_dev_fast_forces_flush(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FLOWCTL_LOG_FLUSH_EVERY", "123")
    flow_path = tmp_path / "flush_fast.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "solo",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} -c \"print('ok')\"",
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path, dev_fast=True)
    assert runner._log_flush_every == 1


def test_flow_runner_creates_artifacts(tmp_path: Path) -> None:
    flow_path = tmp_path / "flow.yaml"
    script_path = tmp_path / "prepare.py"
    script_path.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "import json",
                "import os",
                "import pathlib",
                "out = pathlib.Path(os.environ['FLOW_ARTIFACTS_DIR']) / 'data.json'",
                "out.write_text(json.dumps({'hello': 'world'}), encoding='utf-8')",
            ]
        ),
        encoding="utf-8",
    )
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "prepare",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} {shlex.quote('prepare.py')}",
                    "timeout_sec": 10,
                },
                {
                    "id": "prompt",
                    "uses": "mcp",
                    "depends_on": ["prepare"],
                    "input": {
                        "prompt": "Summarize {artifacts_dir}/data.json",
                        "variables": {},
                    },
                    "policy": {
                        "model": "gpt-4o-mini",
                        "prompt_limit": 8192,
                        "prompt_buffer": 512,
                        "sandbox": "read-only",
                    },
                    "config": {"temperature": 0.0},
                    "save": {"text": "artifacts/prompt.txt"},
                    "timeout_sec": 10,
                },
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    run_id = runner.run()
    run_dir = runner.run_dir
    summary_path = run_dir / "summary.json"
    runs_log = run_dir / "runs.jsonl"
    artifact = run_dir / "artifacts" / "prompt.txt"
    assert run_id
    assert summary_path.exists()
    assert runs_log.exists()
    assert artifact.exists()
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    assert summary["steps"]["prompt"]["ok"] == 1
    mcp_log = json.loads((run_dir / "mcp_calls.jsonl").read_text(encoding="utf-8").splitlines()[-1])
    assert "token_usage" in mcp_log
    events = _load_jsonl(runs_log)
    prompt_end = next(
        entry
        for entry in events
        if entry["step"] == "prompt" and entry["event"] == "end"
    )
    assert prompt_end["extra"]["result"]["token_usage"] is not None


def test_workflow_mag_flow_parallelization_graph() -> None:
    flow_path = Path(__file__).resolve().parents[3] / "runtime/automation/flow_runner/flows/workflow_mag.flow.yaml"
    flow = load_flow_from_path(flow_path)
    dependencies = {
        step.id: set(step.model_extra.get("needs", []))
        for step in flow.steps.root
    }

    assert "translate" not in dependencies
    assert dependencies["docs"] == {"plan"}
    assert dependencies["prompts"] == {"plan"}
    assert "localization" not in dependencies
    assert dependencies["context"] == {"prompts"}
    assert dependencies["qa"] == {"docs", "context"}


def test_flow_runner_emits_events(tmp_path: Path) -> None:
    flow_path = tmp_path / "events.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "echo",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} -c \"print('hey')\"",
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    events: list[RunEvent] = []
    runner = FlowRunner(
        flow,
        flow_path=flow_path,
        workspace_dir=tmp_path,
        event_handler=events.append,
    )
    runner.run()
    assert [event.event for event in events if event.step == "echo"] == ["start", "end"]
    assert events[-1].status == "ok"


def test_cli_progress_renders_live_table(tmp_path: Path) -> None:
    flow_path = tmp_path / "progress.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "echo",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} -c \"print('progress')\"",
                }
            ],
        },
    )
    runner = CliRunner()
    env = _cli_env()
    env["RICH_FORCE_TERMINAL"] = "1"
    result = runner.invoke(
        app,
        ["run", "--progress", str(flow_path)],
        env=env,
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert "Flow Progress" in result.stdout
    assert "echo" in result.stdout
    assert "Completed" in result.stdout


def test_prompt_limit_failure_is_logged(tmp_path: Path) -> None:
    flow_path = tmp_path / "flow_limit.yaml"
    tail_script = tmp_path / "tail.py"
    tail_script.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "import os",
                "import pathlib",
                "base = pathlib.Path(os.environ['FLOW_ARTIFACTS_DIR'])",
                "(base / 'done.txt').write_text('ok', encoding='utf-8')",
            ]
        ),
        encoding="utf-8",
    )
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "prompt",
                    "uses": "mcp",
                    "continue_on_error": True,
                    "input": {
                        "prompt": "x" * 200,
                        "variables": {},
                    },
                    "policy": {
                        "model": "gpt-4o-mini",
                        "prompt_limit": 32,
                        "prompt_buffer": 8,
                        "sandbox": "read-only",
                    },
                    "config": {},
                    "timeout_sec": 5,
                },
                {
                    "id": "tail",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} {shlex.quote('tail.py')}",
                    "timeout_sec": 5,
                    "depends_on": ["prompt"],
                },
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    runner.run()
    run_dir = runner.run_dir
    runs_log = run_dir / "runs.jsonl"
    entries = _load_jsonl(runs_log)
    prompt_errors = [
        entry for entry in entries if entry["step"] == "prompt" and entry["event"] == "error"
    ]
    assert prompt_errors, "expected prompt limit to be logged as error"
    has_prompt_error = any(
        "prompt" in extra.get("error", "")
        for extra in (entry["extra"] for entry in prompt_errors)
    )
    assert has_prompt_error
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["steps"]["prompt"]["fail"] == 1
    assert (run_dir / "artifacts" / "done.txt").exists()


def test_agent_paths_loads_custom_agent(tmp_path: Path) -> None:
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    agent_file = agents_dir / "demo_agent.py"
    agent_file.write_text(
        "\n".join(
            [
                "class EchoAgent:",
                "    async def run(self, message: str, context=None):",
                "        context_dir = str(context.run_dir) if context else ''",
                "        return {'echo': message, 'context_dir': context_dir}",
            ]
        ),
        encoding="utf-8",
    )
    flow_path = tmp_path / "agent_flow.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "agent_paths": [str(agents_dir)],
            "steps": [
                {
                    "id": "echo",
                    "uses": "demo_agent:EchoAgent",
                    "input": {"message": "hello"},
                    "timeout_sec": 5,
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    runner.run()
    runs_log = runner.run_dir / "runs.jsonl"
    events = _load_jsonl(runs_log)
    echo_end = next(
        entry
        for entry in events
        if entry["step"] == "echo" and entry["event"] == "end"
    )
    assert echo_end["extra"]["result"]["echo"] == "hello"


def test_agent_paths_expand_user(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home_dir = tmp_path / "home"
    agents_dir = home_dir / "agents"
    agents_dir.mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home_dir))
    agent_file = agents_dir / "echo_agent.py"
    agent_file.write_text(
        "\n".join(
            [
                "class EchoAgent:",
                "    async def run(self, message: str, context=None):",
                "        context_dir = str(context.run_dir) if context else ''",
                "        return {'echo': message, 'run_dir': context_dir}",
            ]
        ),
        encoding="utf-8",
    )
    flow_path = tmp_path / "agent_home.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "agent_paths": ["~/agents"],
            "steps": [
                {
                    "id": "echo",
                    "uses": "echo_agent:EchoAgent",
                    "input": {"message": "hi"},
                    "timeout_sec": 5,
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    runner.run()
    summary = json.loads((runner.run_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["steps"]["echo"]["ok"] == 1
    events = _load_jsonl(runner.runs_log_path)
    echo_end = next(
        entry
        for entry in events
        if entry["event"] == "end" and entry["step"] == "echo"
    )
    assert echo_end["extra"]["result"]["run_dir"] == str(runner.run_dir)


def test_flow_runner_only_and_continue(tmp_path: Path) -> None:
    writer = tmp_path / "writer.py"
    writer.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "import argparse",
                "import os",
                "import pathlib",
                "parser = argparse.ArgumentParser()",
                "parser.add_argument('--out', required=True)",
                "args = parser.parse_args()",
                "base = pathlib.Path(os.environ['FLOW_ARTIFACTS_DIR'])",
                "base.mkdir(parents=True, exist_ok=True)",
                "(base / f'{args.out}.txt').write_text(args.out, encoding='utf-8')",
            ]
        ),
        encoding="utf-8",
    )
    flow_path = tmp_path / "filters.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "one",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} {shlex.quote('writer.py')} --out one",
                },
                {
                    "id": "two",
                    "uses": "shell",
                    "depends_on": ["one"],
                    "run": f"{shlex.quote(sys.executable)} {shlex.quote('writer.py')} --out two",
                },
                {
                    "id": "three",
                    "uses": "shell",
                    "depends_on": ["two"],
                    "run": f"{shlex.quote(sys.executable)} {shlex.quote('writer.py')} --out three",
                },
            ],
        },
    )
    flow = load_flow_from_path(flow_path)

    runner_only = FlowRunner(
        flow,
        flow_path=flow_path,
        workspace_dir=tmp_path,
        only={"three"},
    )
    plan_only = runner_only.plan()
    assert plan_only == ["one", "two", "three"]
    runner_only.run()
    summary_only = json.loads(
        (runner_only.run_dir / "summary.json").read_text(encoding="utf-8")
    )
    assert set(summary_only["steps"].keys()) == {"one", "two", "three"}

    runner_resume = FlowRunner(
        flow,
        flow_path=flow_path,
        workspace_dir=tmp_path,
        continue_from="two",
    )
    plan_resume = runner_resume.plan()
    assert plan_resume == ["two", "three"]
    runner_resume.run()
    summary_resume = json.loads(
        (runner_resume.run_dir / "summary.json").read_text(encoding="utf-8")
    )
    assert list(summary_resume["steps"].keys()) == ["two", "three"]


def test_run_raises_on_fatal_failure(tmp_path: Path) -> None:
    flow_path = tmp_path / "fatal_flow.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "fail_step",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} -c \"import sys; sys.exit(1)\"",
                    "timeout_sec": 5,
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    with pytest.raises(StepExecutionError) as exc_info:
        runner.run()
    message = str(exc_info.value)
    assert "fatal step failure" in message
    assert "fail_step" in message
    summary_path = runner.run_dir / "summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    failure = summary["failures"]["fail_step"]
    assert failure["fatal"] is True
    assert failure["error"]


def test_logs_command_json_output(tmp_path: Path) -> None:
    flow_path = tmp_path / "flow.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "solo",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} -c \"print('ok')\"",
                    "timeout_sec": 5,
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    run_id = runner.run()

    cli_runner = CliRunner()
    env = dict(os.environ)
    result = cli_runner.invoke(
        app,
        ["logs", run_id, "--json", "--output-dir", str(runner.run_dir)],
        env=env,
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["run_id"] == run_id
    assert payload["metrics"]["ok"] == 1
    assert payload["metrics"]["fail"] == 0
    assert payload["steps"][0]["id"] == "solo"


def test_logs_command_accepts_base_output_dir(tmp_path: Path) -> None:
    flow_path = tmp_path / "flow_base.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "run": {
                "output_dir": str(tmp_path / "runs.2024" / "${RUN_ID}"),
            },
            "steps": [
                {
                    "id": "single",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} -c \"print('ok')\"",
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    run_id = runner.run()

    cli_runner = CliRunner()
    env = dict(os.environ)
    base_dir = runner.run_dir.parent
    result = cli_runner.invoke(
        app,
        ["logs", run_id, "--json", "--output-dir", str(base_dir)],
        env=env,
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["run_id"] == run_id
    assert Path(payload["summary_path"]) == runner.summary_path


def test_run_command_dev_fast_skips_schema(tmp_path: Path) -> None:
    flow_path = tmp_path / "dev_fast.yaml"
    script_path = tmp_path / "noop.py"
    script_path.write_text("print('ok')", encoding="utf-8")
    _write_flow(
        flow_path,
        {
            "version": 1,
            "$schema": "./does-not-exist.json",
            "steps": [
                {
                    "id": "noop",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} {shlex.quote(str(script_path))}",
                }
            ],
        },
    )
    cli_runner = CliRunner()
    env = _cli_env()
    failure = cli_runner.invoke(app, ["run", str(flow_path)], env=env)
    assert failure.exit_code != 0
    assert "schema" in failure.stderr.lower()

    fast_result = cli_runner.invoke(app, ["run", str(flow_path), "--dev-fast"], env=env)
    assert fast_result.exit_code == 0, fast_result.stderr


def test_run_command_trace_perf_emits_json(tmp_path: Path) -> None:
    flow_path = tmp_path / "trace_flow.yaml"
    script_path = tmp_path / "trace.py"
    script_path.write_text("print('trace')", encoding="utf-8")
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "trace",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} {shlex.quote(str(script_path))}",
                }
            ],
        },
    )
    cli_runner = CliRunner()
    env = _cli_env()
    result = cli_runner.invoke(app, ["run", str(flow_path), "--trace-perf"], env=env)
    assert result.exit_code == 0, result.stderr
    metric_lines = [line for line in result.stderr.splitlines() if line.strip()]
    assert metric_lines, "expected timing output on stderr"
    parsed = [json.loads(line) for line in metric_lines]
    assert any(entry.get("stage") == "execute" for entry in parsed)


def test_mcp_step_variable_resolution(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    (artifacts_dir / "context.json").write_text("{}", encoding="utf-8")
    monkeypatch.setenv("HOME", str(tmp_path))
    spec = McpStepSpec(
        id="prompt",
        uses="mcp",
        input={
            "prompt": "Topic: {topic}\nArtifact: {artifact}\nHome: {home_artifact}",
            "variables": {
                "topic": "Flow Runner",
                "artifact": "artifacts/context.json",
                "home_artifact": "~/artifacts/context.json",
            },
        },
        policy={
            "model": "gpt-4o-mini",
            "prompt_limit": 1024,
            "prompt_buffer": 128,
            "sandbox": "read-only",
        },
        config={},
        timeout_sec=5,
    )
    step = McpStep(spec)
    context = ExecutionContext(
        run_id="run",
        run_dir=tmp_path,
        artifacts_dir=artifacts_dir,
        workspace_dir=tmp_path,
        flow_dir=tmp_path,
        mcp_log_dir=tmp_path,
        mcp_router=None,
    )
    prompt = step._resolve_prompt(context)
    assert "Topic: Flow Runner" in prompt
    expected_path = str((tmp_path / "artifacts/context.json").resolve())
    assert f"Artifact: {expected_path}" in prompt
    assert f"Home: {expected_path}" in prompt


def test_stats_reports_actual_retries(tmp_path: Path) -> None:
    flow_path = tmp_path / "retry_flow.yaml"
    script_path = tmp_path / "flaky.py"
    script_path.write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "import os",
                "import pathlib",
                "import sys",
                "flag = pathlib.Path(os.environ['FLOW_ARTIFACTS_DIR']) / 'retry_flag.txt'",
                "if not flag.exists():",
                "    flag.write_text('set', encoding='utf-8')",
                "    sys.exit(1)",
                "print('retry succeeded')",
            ]
        ),
        encoding="utf-8",
    )
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "flaky",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} {shlex.quote(script_path.name)}",
                    "retries": 2,
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    runner.run()

    cli_runner = CliRunner()
    env = dict(os.environ)
    runs_dir = runner.run_dir.parent
    result = cli_runner.invoke(
        app,
        ["stats", "--runs-dir", str(runs_dir), "--json"],
        env=env,
    )
    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    group = next((item for item in payload["groups"] if item["group"] == "flaky"), None)
    assert group is not None
    assert group["retries"] == 1
    assert group["ok"] == 1


def test_mcp_prompt_from_expands_user(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home_dir = tmp_path / "home"
    template_dir = home_dir / "templates"
    template_dir.mkdir(parents=True)
    template_path = template_dir / "prompt.txt"
    template_path.write_text("Hello {name}", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home_dir))
    spec = McpStepSpec(
        id="prompt",
        uses="mcp",
        input={
            "prompt_from": "~/templates/prompt.txt",
            "variables": {"name": "World"},
        },
        policy={
            "model": "gpt-4o-mini",
            "prompt_limit": 1024,
            "prompt_buffer": 128,
            "sandbox": "read-only",
        },
        config={},
        timeout_sec=5,
    )
    step = McpStep(spec)
    context = ExecutionContext(
        run_id="run",
        run_dir=tmp_path,
        artifacts_dir=tmp_path / "artifacts",
        workspace_dir=tmp_path,
        flow_dir=tmp_path,
        mcp_log_dir=tmp_path,
        mcp_router=None,
    )
    context.artifacts_dir.mkdir(exist_ok=True)
    prompt = step._resolve_prompt(context)
    assert prompt == "Hello World"


def test_flow_runner_expands_user_output_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    monkeypatch.setenv("HOME", str(home_dir))
    flow_path = tmp_path / "home_output.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "run": {"output_dir": "~/runs/${RUN_ID}"},
            "steps": [
                {
                    "id": "solo",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} -c \"print('ok')\"",
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    run_id = runner.run()
    expected_dir = (home_dir / "runs" / run_id).resolve()
    assert runner.run_dir == expected_dir
    assert runner.summary_path.exists()


def test_extract_tokens_understands_aliases() -> None:
    usage = {"prompt_tokens": 12, "completion_tokens": 4}
    assert _extract_tokens(usage, "input") == 12
    assert _extract_tokens(usage, "output") == 4
    nested_usage = {"tokens": {"input": 1, "output": 2}}
    assert _extract_tokens(nested_usage, "input") == 1
    assert _extract_tokens(nested_usage, "output") == 2
    # Non-matching structures should return zero without raising
    fallback_usage = {"total_tokens": 99}
    assert _extract_tokens(fallback_usage, "input") == 0


def test_runner_logs_non_serializable_results(tmp_path: Path) -> None:
    agents_dir = tmp_path / "agents_non_serializable"
    agents_dir.mkdir()
    agent_file = agents_dir / "path_agent.py"
    agent_file.write_text(
        "\n".join(
            [
                "from pathlib import Path",
                "",
                "class PathAgent:",
                "    def __init__(self, base: str):",
                "        self.base = Path(base)",
                "",
                "    def run(self, context=None):",
                "        return {",
                "            'path': self.base,",
                "            'context': context.run_dir if context else None,",
                "        }",
            ]
        ),
        encoding="utf-8",
    )
    flow_path = tmp_path / "path_flow.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "agent_paths": [str(agents_dir)],
            "steps": [
                {
                    "id": "path_step",
                    "uses": "path_agent:PathAgent",
                    "config": {"base": "artifacts"},
                    "timeout_sec": 5,
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    runner.run()
    events = _load_jsonl(runner.runs_log_path)
    path_end = next(
        entry
        for entry in events
        if entry["event"] == "end" and entry["step"] == "path_step"
    )
    assert path_end["extra"]["result"]["path"] == "artifacts"
    assert isinstance(path_end["extra"]["result"]["context"], str)


def test_agent_config_passed_to_constructor(tmp_path: Path) -> None:
    agents_dir = tmp_path / "agents_config"
    agents_dir.mkdir()
    agent_file = agents_dir / "config_agent.py"
    agent_file.write_text(
        "\n".join(
            [
                "class ConfigAgent:",
                "    def __init__(self, label: str):",
                "        self.label = label",
                "",
                "    async def run(self, *, message: str, context=None):",
                "        return {'label': self.label, 'message': message}",
            ]
        ),
        encoding="utf-8",
    )
    flow_path = tmp_path / "config_flow.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "agent_paths": [str(agents_dir)],
            "steps": [
                {
                    "id": "config_step",
                    "uses": "config_agent:ConfigAgent",
                    "config": {"label": "demo"},
                    "input": {"message": "hello"},
                    "timeout_sec": 5,
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    runner.run()
    events = _load_jsonl(runner.runs_log_path)
    config_end = next(
        entry
        for entry in events
        if entry["event"] == "end" and entry["step"] == "config_step"
    )
    assert config_end["extra"]["result"] == {"label": "demo", "message": "hello"}


def test_run_env_inherits_existing_values(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    flow_path = tmp_path / "env_inherit.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "run": {
                "env": {
                    "WORKFLOW_CONFIG": "${WORKFLOW_CONFIG}",
                    "WORKFLOW_LOG": "~/logs/${RUN_ID}",
                }
            },
            "steps": [],
        },
    )
    monkeypatch.setenv("WORKFLOW_CONFIG", "/tmp/config.json")
    monkeypatch.setenv("HOME", str(tmp_path))
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    runner._push_run_env()
    try:
        assert os.environ["WORKFLOW_CONFIG"] == "/tmp/config.json"
        assert runner._resolved_run_env["WORKFLOW_CONFIG"] == "/tmp/config.json"
        log_value = runner._resolved_run_env["WORKFLOW_LOG"]
        expected_path = (Path(tmp_path) / "logs" / runner.run_id).resolve()
        assert Path(log_value) == expected_path
    finally:
        runner._pop_run_env()


def test_run_env_skips_unresolved_placeholders(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    flow_path = tmp_path / "env_skip.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "run": {
                "env": {
                    "WORKFLOW_CONFIG": "${WORKFLOW_CONFIG}",
                    "WORKFLOW_LOG": "~/logs/${RUN_ID}",
                }
            },
            "steps": [],
        },
    )
    monkeypatch.delenv("WORKFLOW_CONFIG", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    runner._push_run_env()
    try:
        assert "WORKFLOW_CONFIG" not in runner._resolved_run_env
        assert "WORKFLOW_CONFIG" not in os.environ
        log_value = runner._resolved_run_env["WORKFLOW_LOG"]
        assert "${" not in log_value
    finally:
        runner._pop_run_env()


def test_resolve_workflow_config_path_expands_user(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    home_dir = tmp_path / "home"
    config_dir = home_dir / "workflow"
    config_dir.mkdir(parents=True)
    config_path = config_dir / "config.json"
    config_path.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("HOME", str(home_dir))
    flow_path = tmp_path / "env_home.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "run": {
                "env": {
                    "WORKFLOW_CONFIG": "~/workflow/config.json",
                }
            },
            "steps": [],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    resolved = runner._resolve_workflow_config_path()
    assert resolved == config_path.resolve()


def test_pre_task_prologue_invokes_cli(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config_path = tmp_path / "workflow" / "config.json"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        json.dumps({"task": {"name": "Demo", "categories": ["docs"]}}),
        encoding="utf-8",
    )

    flow_path = tmp_path / "pre_flow.yaml"
    _write_flow(
        flow_path,
        {
            "version": 1,
            "run": {
                "env": {
                    "WORKFLOW_CONFIG": str(config_path),
                }
            },
            "steps": [],
        },
    )

    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)

    captured: list[list[str]] = []

    class StubResult:
        def __init__(self) -> None:
            self.stdout = ""
            self.stderr = ""
            self.returncode = 0

    def fake_run(cmd, capture_output, text, check):  # type: ignore[override]
        captured.append(list(cmd))
        return StubResult()

    monkeypatch.setattr(subprocess, "run", fake_run)
    runner._run_pre_task_prologue()

    assert captured, "expected subprocess.run to be invoked"
    command = captured[0]
    assert command[2] == "automation.compliance.pre"
    assert "--accept-all" not in command
    assert "--categories" in command


@pytest.mark.asyncio
async def test_runner_run_inside_event_loop(tmp_path: Path) -> None:
    flow_path = tmp_path / "loop_flow.yaml"
    script = tmp_path / "echo.py"
    script.write_text("print('async-ok')", encoding="utf-8")
    _write_flow(
        flow_path,
        {
            "version": 1,
            "steps": [
                {
                    "id": "echo",
                    "uses": "shell",
                    "run": f"{shlex.quote(sys.executable)} {shlex.quote(str(script.name))}",
                    "timeout_sec": 5,
                }
            ],
        },
    )
    flow = load_flow_from_path(flow_path)
    runner = FlowRunner(flow, flow_path=flow_path, workspace_dir=tmp_path)
    run_id = runner.run()
    assert run_id
