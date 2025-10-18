"""CLI entry point for the repository-wide pre-task compliance check."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from ..workflows.compliance import pre_task_check


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run repository pre-task compliance checks. "
            "Wraps automation.workflows.compliance.pre_task_check."
        )
    )
    parser.add_argument(
        "--task-name",
        required=True,
        help="Human-readable task name recorded in PLANS.md and task templates.",
    )
    parser.add_argument(
        "--categories",
        required=True,
        help="Comma-separated categories (e.g., docs,qa,operations).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail with non-zero exit when optional checks are missing.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    results = pre_task_check.run_pre_task_check(
        task_name=args.task_name,
        categories=args.categories,
        strict=args.strict,
        stream=sys.stdout,
    )

    if results.has_failures:
        return 1
    if results.has_warnings and args.strict:
        return 2
    return 0


def cli() -> None:
    """Console-script entry point wrapping :func:`main` with proper exit codes."""
    raise SystemExit(main())


if __name__ == "__main__":
    cli()
