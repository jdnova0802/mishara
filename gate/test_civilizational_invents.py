"""Tests for DENY Meter, Diplomatics, Documentary Protest invents."""
from __future__ import annotations

from gate.deny_meter import quote
from gate.diplomatics import challenge
from gate.documentary_protest import present, protest


def test_deny_meter_unit():
    q = quote(unit="DENY_HOLD")
    assert q["unit"] == "DENY_HOLD"
    assert q["flat_cents_indicative"] == 1750_00


def test_diplomatics_issuer_incomplete():
    c = challenge(receipt_hint="demo")
    assert c["issuer_incomplete"] is True
    assert c["challenge_id"]


def test_documentary_discrepant():
    out = present({"documents": {"ACT_DIGEST": "x"}})
    assert out["complying"] is False
    assert out["verdict"] == "DISCREPANT"


def test_documentary_protest_issues():
    out = protest({"documents": {"ACT_DIGEST": "x"}, "refused_act": "payout"})
    assert out["instrument"] == "PROTEST"
    assert out["deny_meter_unit"] == "PROTEST"
