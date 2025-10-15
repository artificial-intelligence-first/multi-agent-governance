import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from qa_mag import agent


def test_qa_mag_returns_checklist():
    qa = agent.QAMAG()
    result = qa(["documentation completeness"])
    assert result["status"] == "review-pending"
    assert result["checklist"] == ["documentation completeness"]
