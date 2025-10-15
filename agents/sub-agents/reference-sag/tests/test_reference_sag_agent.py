import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2] / "src"))

from reference_sag import agent


def test_reference_sag_stub():
    ref = agent.ReferenceSAG()
    result = ref([{"id": "doc-1", "status": "ok"}])
    assert result["status"] == "audited"
    assert result["references"][0]["id"] == "doc-1"
