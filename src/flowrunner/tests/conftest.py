from __future__ import annotations

from pathlib import Path

import flow_runner

LOCAL_TASKS = Path(__file__).resolve().parents[3] / "src" / "flow_runner"
if str(LOCAL_TASKS) not in flow_runner.__path__:
    flow_runner.__path__.append(str(LOCAL_TASKS))
