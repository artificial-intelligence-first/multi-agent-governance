"""DepsSAG helper utilities.

This package intentionally exports a minimal surface today. Runtime automation
imports `deps_sag.load_workflow()` to construct upgrade plans without repeating
path logic in multiple agents.
"""

from pathlib import Path
import yaml


WORKFLOW_ROOT = Path(__file__).resolve().parents[2] / "workflows"


def load_workflow(name: str) -> dict:
    """Return the parsed workflow YAML for the requested upgrade routine."""
    workflow_path = WORKFLOW_ROOT / name
    if not workflow_path.exists():
        raise FileNotFoundError(f"Missing workflow: {workflow_path}")
    with workflow_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)
