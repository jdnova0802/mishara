"""Tests for gate_anatomy."""

from gate.gate_anatomy import gate_anatomy_manifest


def test_anatomy_no_face_protection_only():
    m = gate_anatomy_manifest("https://gate.example")
    assert m["no_face"] is True
    assert "face" in m["organs_forbidden"]
    assert "eye" in m["organs_protection"]
    assert "hand" in m["organs_protection"]
    assert "mouth" in m["organs_core"]
    assert m["forbidden_flow"] == ["Eye sees enemy", "Hand shoots"]
    assert "classical" in m["protection_deal"]["eye"]["tiers"]
    assert "cosmic" in m["protection_deal"]["hand"]["tiers"]
    assert "never equals LIVE" in m["protection_deal"]["eye"]["formal"]
    assert "without Mouth" in m["protection_deal"]["hand"]["formal"]
    assert "Protection ≠ disabled" in m["lockheed_rule"]
    assert m["spec"] == "gate/GATE_ANATOMY.md"
