import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from quality_sag import agent


def test_quality_sag_returns_issues():
    q = agent.QualitySAG()
    result = q(["stale-progress"])
    assert result["issues"] == ["stale-progress"]
