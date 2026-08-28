"""Tests for gate_anatomy."""

from gate.gate_anatomy import gate_anatomy_manifest


def test_anatomy_formalized_protection_layers():
    m = gate_anatomy_manifest("https://gate.example")
    assert m["no_face"] is True
    assert "face" in m["organs_forbidden"]
    assert "eye" in m["organs_protection"]
    assert "hand" in m["organs_protection"]
    assert "mouth" in m["organs_core"]
    assert m["protection_layers"]["P1"]["name"] == "Facility Protect"
    assert m["protection_layers"]["P2"]["name"] == "Channel Protect"
    assert m["protection_layers"]["P3"]["name"] == "Lattice Protect"
    assert m["protection_layers"]["P3"]["enter"].startswith("mountain")
    assert "never equals LIVE" in m["protection_deal"]["eye"]["formal"]
    assert "Necessity Bar" in m["protection_deal"]["hand"]["formal"]
    assert len(m["protection_deal"]["hand"]["necessity_bar"]) == 5
    assert m["spec"] == "gate/GATE_ANATOMY.md"
