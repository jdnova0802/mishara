"""Tests for continuity_live inventions."""

from gate.continuity_live import INVENTIONS, continuity_live_manifest


def test_fifteen_inventions():
    assert len(INVENTIONS) == 15
    m = continuity_live_manifest("https://gate.example")
    assert m["invention_count"] == 15
    assert m["build_first"][:3] == [
        "voice_is_not_may",
        "war_grade_order_auth",
        "access_tomb",
    ]
    assert m["spec"] == "gate/CONTINUITY_LIVE.md"
    titles = {i["title"] for i in m["inventions"]}
    assert "Obey Bit" in titles
    assert "Voice is Not May" in titles
    assert "Access Tomb" in titles
    assert "Deflection May Bus" in titles
    assert "Seed Vault LIVE + Funeral" in titles
    assert "Bootstrap May" in titles
    assert "Emergency May Charter" in titles
    assert "War-Grade Order Auth" in titles


def test_evac_ceiling_honest():
    m = continuity_live_manifest()
    assert "ECLSS" in m["evac_still_above"][0]
    assert "oxygen" in m["evac_ceiling_note"]
