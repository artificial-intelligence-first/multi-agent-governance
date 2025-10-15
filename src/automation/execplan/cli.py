from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional, Sequence


@dataclass(frozen=True)
class PlanTemplate:
    big_picture_heading: str
    todo_heading: str
    progress_heading: str
    decision_heading: str
    surprises_heading: str
    outcomes_heading: str
    big_picture_placeholder: str
    todo_placeholder: list[str]
    progress_placeholder: str
    decision_placeholder: str
    surprises_placeholder: str
    outcomes_placeholder: str

    def render(self, *, task_name: str, timestamp: datetime) -> str:
        """Render an ExecPlan document using a single-language template."""

        todo_lines = "\n".join(self.todo_placeholder)
        ts = timestamp.isoformat().replace("+00:00", "Z")
        return (
            f"# ExecPlan — {task_name}\n\n"
            f"## {self.big_picture_heading}\n"
            f"- {self.big_picture_placeholder}\n\n"
            f"## {self.todo_heading}\n"
            f"{todo_lines}\n\n"
            f"## {self.progress_heading}\n"
            f"- {ts} — {self.progress_placeholder}\n\n"
            f"## {self.decision_heading}\n"
            f"- {ts} — {self.decision_placeholder}\n\n"
            f"## {self.surprises_heading}\n"
            f"- {self.surprises_placeholder}\n\n"
            f"## {self.outcomes_heading}\n"
            f"- {self.outcomes_placeholder}\n"
        )


DEFAULT_TEMPLATE = PlanTemplate(
    big_picture_heading="Big Picture",
    todo_heading="To-do",
    progress_heading="Progress",
    decision_heading="Decision Log",
    surprises_heading="Surprises",
    outcomes_heading="Outcomes & Retrospectives",
    big_picture_placeholder="Document the objective for this task.",
    todo_placeholder=[
        "- [ ] Break down actionable steps.",
        "- [ ] Capture ownership or dependencies.",
        "- [ ] Note validation or review requirements.",
    ],
    progress_placeholder="Record major actions as they happen.",
    decision_placeholder="Explain why key decisions were made.",
    surprises_placeholder="Log unexpected findings or blockers.",
    outcomes_placeholder="Summarise the result and next steps.",
)


def render_plan(*, task_name: str, timestamp: Optional[datetime] = None) -> str:
    ts = timestamp or datetime.now(UTC)
    return DEFAULT_TEMPLATE.render(task_name=task_name, timestamp=ts)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate PLANS.md using the default template.")
    parser.add_argument("--task-name", required=True, help="Name of the task captured in the plan heading.")
    parser.add_argument(
        "--output",
        default="PLANS.md",
        help="Destination path for the plan (default: PLANS.md).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing plan file.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    output_path = Path(args.output)
    if output_path.exists() and not args.overwrite:
        parser.error(f"{output_path} already exists (use --overwrite to replace it)")

    content = render_plan(task_name=args.task_name)
    output_path.write_text(content, encoding="utf-8")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
