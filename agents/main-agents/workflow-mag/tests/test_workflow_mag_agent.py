import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from workflow_mag import agent


def test_workflow_mag_stub_returns_payload():
    wf = agent.WorkFlowMAG()
    result = wf.run({"sample": 1})
    assert result["agent"] == "workflow-mag"
    assert result["status"] == "delegated"
    assert result["received_payload"] == {"sample": 1}
