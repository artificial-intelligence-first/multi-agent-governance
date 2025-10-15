from pathlib import Path

from automation.execplan import main as execplan_main, render_plan


def test_render_plan_uses_default_template() -> None:
    content = render_plan(task_name="Demo Task")
    assert content.startswith("# ExecPlan — Demo Task")
    assert "## Big Picture" in content
    assert "## To-do" in content
    assert "- [ ] Break down actionable steps." in content


def test_cli_generates_plan(tmp_path: Path) -> None:
    path = tmp_path / "PLANS.md"
    rc = execplan_main([
        "--task-name",
        "CLI Task",
        "--output",
        str(path),
        "--overwrite",
    ])
    assert rc == 0
    content = path.read_text(encoding="utf-8")
    assert "# ExecPlan — CLI Task" in content
