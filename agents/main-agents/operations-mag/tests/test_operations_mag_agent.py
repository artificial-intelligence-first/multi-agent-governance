import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from operations_mag import agent


def test_operations_mag_returns_status():
    op = agent.OperationsMAG()
    assert op({"latency": 10})["status"] == "observing"
