from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_DIR = REPO_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import flow_runner  # type: ignore  # noqa: E402

LOCAL_PACKAGE = SRC_DIR / "flow_runner"
if LOCAL_PACKAGE.exists():
    local_path = str(LOCAL_PACKAGE.resolve())
    if local_path not in flow_runner.__path__:
        flow_runner.__path__.append(local_path)


def _iter_flow_runner_candidates() -> list[str]:
    candidates: list[str] = []
    for entry in sys.path:
        candidate = Path(entry) / "flow_runner"
        if not candidate.exists():
            continue
        steps_dir = candidate / "steps"
        if not steps_dir.exists():
            continue
        resolved = str(candidate.resolve())
        candidates.append(resolved)
    return candidates


for candidate_path in _iter_flow_runner_candidates():
    if candidate_path not in flow_runner.__path__:
        flow_runner.__path__.append(candidate_path)
