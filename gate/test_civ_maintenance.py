"""Tests for civ_maintenance market inventions."""

from gate.civ_maintenance import (
    INVENTIONS,
    TOP_THREE_IDS,
    civ_maintenance_manifest,
    get_invention,
    top_three,
)


def test_manifest_structure():
    m = civ_maintenance_manifest("https://gate.example")
    assert m["doctrine"] == "civ_maintenance"
    assert m["layer"] == "L4_maintenance"
    assert m["invention_count"] == 10
    assert m["top_three"] == list(TOP_THREE_IDS)
    assert m["spec"] == "gate/CIV_MAINTENANCE.md"
    assert "teeth_latch" in m["well_known"] or m["well_known"].endswith(
        "civ-maintenance.json"
    )


def test_ten_inventions_named():
    titles = {i.title for i in INVENTIONS}
    assert "Teeth Latch" in titles
    assert "Reality Root" in titles
    assert "Loss Deed" in titles
    assert "Telos Charter" in titles
    assert "Catechism Ordeal" in titles
    assert "Attested Exit" in titles
    assert "Joule Hostage Map" in titles
    assert "Unborn Seat" in titles
    assert "Domination Facing" in titles
    assert "Name Death" in titles


def test_top_three_order():
    t = top_three()
    assert [x.id for x in t] == ["teeth_latch", "reality_root", "loss_deed"]


def test_get_invention():
    teeth = get_invention("teeth_latch")
    assert teeth is not None
    assert "theater" in teeth.formal_rule.lower() or "theater" in teeth.formal_rule


def test_settlement_dependency_kpi():
    m = civ_maintenance_manifest()
    assert m["settlement_dependency"]["id"] == "settlement_dependency"
    assert "cannot settle" in m["settlement_dependency"]["definition"]
