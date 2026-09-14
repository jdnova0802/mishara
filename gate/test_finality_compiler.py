"""Finality Compiler v0 — on-card artifact tests."""
from __future__ import annotations

from gate.finality_compiler import CLASSES, classify, manifest, taxonomy_table


def test_hard_rtp():
    out = classify(rail="rtp", status="accepted")
    assert out["finality_class"] == "RAIL_FINAL_HARD"
    assert out["reversibility"] == "near_zero"


def test_soft_ach():
    out = classify(rail="ach", status="settled")
    assert out["finality_class"] == "NETWORK_SETTLED_SOFT"


def test_unknown_fail_closed_hint():
    out = classify(rail="mystery", status="banana")
    assert out["finality_class"] == "UNKNOWN"
    assert "Fail closed" in out["leave_risk"]


def test_manifest_on_card():
    m = manifest("https://gate.example")
    assert m["spec"] == "gate-finality-compiler-v0"
    assert m["firm"] == "Nisaba LLC"
    assert "sister" in " ".join(m["not"]).lower()
    assert set(CLASSES) == set(m["classes"])


def test_taxonomy_nonempty():
    rows = taxonomy_table()
    assert len(rows) >= 20
