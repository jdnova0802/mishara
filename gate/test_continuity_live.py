"""Tests for continuity_live inventions."""

from gate.continuity_live import INVENTIONS, continuity_live_manifest


def test_ten_inventions():
    assert len(INVENTIONS) == 10
    m = continuity_live_manifest("https://gate.example")
    assert m["invention_count"] == 10
    assert m["build_first"] == [
        "voice_is_not_may",
        "access_tomb",
        "agent_succession_receipt",
    ]
    assert m["spec"] == "gate/CONTINUITY_LIVE.md"
    titles = {i["title"] for i in m["inventions"]}
    assert "Obey Bit" in titles
    assert "Voice is Not May" in titles
    assert "Access Tomb" in titles
