"""Repository-wide pre-task compliance checks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, TextIO


@dataclass
class CheckResults:
    task_name: str
    categories: str
    passes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)

    @property
    def has_failures(self) -> bool:
        return bool(self.failures)

    @property
    def has_warnings(self) -> bool:
        return bool(self.warnings)


_ROOT_SENTINELS = ("pyproject.toml", "uv.lock", ".git")


def _find_repo_root(start: Path) -> Optional[Path]:
    """Walk upward from ``start`` until a sentinel file is found."""
    for candidate in [start, *start.parents]:
        if any((candidate / sentinel).exists() for sentinel in _ROOT_SENTINELS):
            return candidate
    return None


def _repo_root() -> Path:
    """Return repository root regardless of whether the package is installed or run in-place."""
    cwd_root = _find_repo_root(Path.cwd())
    if cwd_root:
        return cwd_root

    module_root = _find_repo_root(Path(__file__).resolve().parent)
    if module_root:
        return module_root

    # Fallback to historical behaviour; should only trigger in unusual packaging layouts.
    return Path(__file__).resolve().parents[4]


def _record(
    results: CheckResults,
    stream: TextIO,
    status: str,
    message: str,
) -> None:
    stream.write(f"[{status}] {message}\n")
    stream.flush()
    if status == "PASS":
        results.passes.append(message)
    elif status == "WARN":
        results.warnings.append(message)
    else:
        results.failures.append(message)


def run_pre_task_check(
    task_name: str,
    categories: str,
    strict: bool = False,
    stream: TextIO | None = None,
) -> CheckResults:
    """Execute baseline compliance checks and return aggregated results."""
    stream = stream or Path("/dev/null").open("w")
    results = CheckResults(task_name=task_name, categories=categories)

    root = _repo_root()
    plans_path = root / "PLANS.md"
    if plans_path.exists():
        _record(results, stream, "PASS", f"PLANS.md located at {plans_path.relative_to(root)}")
    else:
        _record(results, stream, "FAIL", "PLANS.md missing; initialise ExecPlan before proceeding.")

    task_template = root / "docs" / "task_template.md"
    if task_template.exists():
        _record(
            results,
            stream,
            "PASS",
            f"Task template found at {task_template.relative_to(root)}",
        )
    else:
        severity = "FAIL" if strict else "WARN"
        _record(
            results,
            stream,
            severity,
            "Task template docs/task_template.md not found; create from shared outline.",
        )

    logs_dir = root / "runtime" / "automation" / "logs"
    if logs_dir.exists():
        _record(results, stream, "PASS", f"Logging directory present at {logs_dir.relative_to(root)}")
    else:
        severity = "FAIL" if strict else "WARN"
        _record(
            results,
            stream,
            severity,
            "Logging directory runtime/automation/logs missing; establish before executions.",
        )

    references = [
        root / "docs" / "reference" / "files" / "AGENTS.md" / "OpenAI.md",
        root / "docs" / "reference" / "files" / "SSOT.md" / "overview.md",
        root / "docs" / "reference" / "files" / "PLANS.md" / "OpenAI.md",
        root / "docs" / "reference" / "files" / "PNPM.md" / "overview.md",
    ]
    missing_references = [path for path in references if not path.exists()]
    if missing_references:
        for missing in missing_references:
            severity = "FAIL" if strict else "WARN"
            _record(
                results,
                stream,
                severity,
                f"Reference file missing: {missing.relative_to(root)}",
            )
    else:
        _record(results, stream, "PASS", "All required reference files present under docs/reference/files.")

    stream.write(
        "\nSummary: "
        f"{len(results.passes)} pass, "
        f"{len(results.warnings)} warning, "
        f"{len(results.failures)} failure(s)\n"
    )
    stream.flush()
    return results
