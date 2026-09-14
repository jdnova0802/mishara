"""Oracle Compiler + enterprise mouths tests."""
from __future__ import annotations

from gate.enterprise_mouths import manifest as mouths_manifest
from gate.oracle_compiler import classify, manifest


def test_fail_open():
    out = classify(claim_type="agent_tool", source="timeout_default_allow")
    assert out["oracle_class"] == "FAIL_OPEN"
    assert out["fail_closed_required"] is True


def test_stale_by_age():
    out = classify(
        claim_type="price",
        source="push_feed_fresh",
        age_seconds=7200,
        heartbeat_seconds=3600,
    )
    assert out["oracle_class"] == "STALE"


def test_webhook_soft():
    out = classify(claim_type="event", source="payment_succeeded")
    assert out["oracle_class"] == "LIVE_SOFT"


def test_manifest_on_card():
    m = manifest("https://gate.example")
    assert m["spec"] == "gate-oracle-compiler-v0"
    assert "sister" in " ".join(m["not"]).lower()


def test_microsoft_fail_open_ranked():
    m = mouths_manifest("https://gate.example")
    ms = m["targets"]["microsoft"]["verified_shaped"][0]
    assert ms["severity"] == "critical"
    assert "FAIL_OPEN" in ms["gap"] or "fail" in ms["gap"].lower()
