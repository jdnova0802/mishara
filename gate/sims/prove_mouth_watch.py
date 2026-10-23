#!/usr/bin/env python3
"""Prove S9 Mouth Watch — threat receipts distinct from clearance; trip = DENY-this-only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import mouth_watch as mw  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def assert_threat(r: dict, *, threat_class: str, reason: str) -> None:
    expect(r["receipt_class"] == "threat", f"receipt_class threat: {r}")
    expect(r["threat_class"] == threat_class, f"threat_class {threat_class}: {r}")
    expect(r["decision"] == "DENY", f"decision DENY: {r}")
    expect(r["reason_code"] == reason, f"reason {reason}: {r}")
    expect(r["effect"]["deny_this_actus"] is True, "deny_this_actus")
    expect(r["effect"]["session_lockout"] is False, "no session_lockout")
    expect(r["effect"]["alert_fanout"] is False, "no alert_fanout")
    expect(r["effect"]["quarantine"] is False, "no quarantine")
    expect("threat_class" in r and r["threat_class"] is not None, "threat_class present")
    fetched = mw.get_receipt(r["receipt_id"])
    expect(fetched is not None, "stranger fetch")
    expect(fetched["receipt_class"] == "threat", "fetched is threat object")


def main() -> None:
    mw.reset()

    # 1) hostile session → threat (session_integrity), not clearance-shaped
    s1 = mw.score_session(
        appearance="synthetic_suspect", device_trust="known", network_risk="low"
    )
    assert_threat(s1, threat_class="session_integrity", reason="session_hostile")

    # 2) unknown device → same threat class
    s2 = mw.score_session(appearance="live", device_trust="unknown", network_risk="low")
    assert_threat(s2, threat_class="session_integrity", reason="session_hostile")

    # 3) canary → threat_class canary
    m = mw.create_mandate(["pay", "read"], max_steps=3)
    decoy = {"vault": "prod", "canary": True}
    canary = mw.plant_canary("vault_exfil", decoy)
    t1 = mw.evaluate_actus(m["mandate_id"], "vault_exfil", decoy)
    assert_threat(t1, threat_class="canary", reason="canary_tripped")
    expect(t1["result"]["canary_id"] == canary["canary_id"], "canary link")

    # 4) scope drift → trajectory threat
    t2 = mw.evaluate_actus(m["mandate_id"], "wire_all_funds", {"to": "attacker"})
    assert_threat(t2, threat_class="trajectory", reason="trajectory_scope_drift")

    # 5) overrun → trajectory threat
    mw.evaluate_actus(m["mandate_id"], "read", {"path": "/a"})
    mw.evaluate_actus(m["mandate_id"], "read", {"path": "/b"})
    mw.evaluate_actus(m["mandate_id"], "read", {"path": "/c"})
    t3 = mw.evaluate_actus(m["mandate_id"], "read", {"path": "/d"})
    assert_threat(t3, threat_class="trajectory", reason="trajectory_overrun")

    # 6) clear → watch_clear (NOT threat, NOT clearance)
    s_ok = mw.score_session(appearance="live", device_trust="known", network_risk="low")
    expect(s_ok["receipt_class"] == "watch_clear", f"s_ok class {s_ok}")
    expect(s_ok["threat_class"] is None, "s_ok no threat_class")
    expect(s_ok["decision"] == "ALLOW", f"s_ok {s_ok}")
    m2 = mw.create_mandate(["pay"], max_steps=5)
    t_ok = mw.evaluate_actus(m2["mandate_id"], "pay", {"payee": "acme", "amount_cents": 50})
    expect(t_ok["receipt_class"] == "watch_clear", f"t_ok class {t_ok}")
    expect(t_ok["their_production"] is False, "production")

    # 7) threat ≠ clearance by schema (bank can branch without parsing reason text)
    expect(s1["receipt_class"] != "clearance", "threat is not clearance")
    expect("threat_class" in s1 and s1["threat_class"] == "session_integrity", "machine field")

    assert_all_receipts_lab(mw)

    print("MOUTH_WATCH_PROVE_OK")
    print(
        {
            "threats": [
                (s1["threat_class"], s1["reason_code"]),
                (s2["threat_class"], s2["reason_code"]),
                (t1["threat_class"], t1["reason_code"]),
                (t2["threat_class"], t2["reason_code"]),
                (t3["threat_class"], t3["reason_code"]),
            ],
            "trip_effect": mw.TRIP_EFFECT,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
