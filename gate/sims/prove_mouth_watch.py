#!/usr/bin/env python3
"""Prove S9 Mouth Watch DENY paths. Lab only."""

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


def main() -> None:
    mw.reset()

    # 1) synthetic session → DENY (feeds S8/S6)
    s1 = mw.score_session(
        appearance="synthetic_suspect", device_trust="known", network_risk="low"
    )
    expect(s1["decision"] == "DENY" and s1["reason_code"] == "session_hostile", f"s1 {s1}")
    expect(mw.get_receipt(s1["receipt_id"]) is not None, "s1 stranger receipt")

    # 2) unknown device → DENY
    s2 = mw.score_session(appearance="live", device_trust="unknown", network_risk="low")
    expect(s2["decision"] == "DENY" and s2["reason_code"] == "session_hostile", f"s2 {s2}")

    # 3) canary trip → DENY
    m = mw.create_mandate(["pay", "read"], max_steps=3)
    decoy_payload = {"vault": "prod", "canary": True}
    canary = mw.plant_canary("vault_exfil", decoy_payload)
    t1 = mw.evaluate_actus(m["mandate_id"], "vault_exfil", decoy_payload)
    expect(t1["decision"] == "DENY" and t1["reason_code"] == "canary_tripped", f"t1 {t1}")
    expect(t1["result"]["canary_id"] == canary["canary_id"], "t1 canary link")

    # 4) scope drift → DENY
    t2 = mw.evaluate_actus(m["mandate_id"], "wire_all_funds", {"to": "attacker"})
    expect(t2["decision"] == "DENY" and t2["reason_code"] == "trajectory_scope_drift", f"t2 {t2}")

    # 5) trajectory overrun → DENY
    mw.evaluate_actus(m["mandate_id"], "read", {"path": "/a"})
    mw.evaluate_actus(m["mandate_id"], "read", {"path": "/b"})
    mw.evaluate_actus(m["mandate_id"], "read", {"path": "/c"})
    t3 = mw.evaluate_actus(m["mandate_id"], "read", {"path": "/d"})
    expect(t3["decision"] == "DENY" and t3["reason_code"] == "trajectory_overrun", f"t3 {t3}")

    # 6) clear session + in-scope actus → ALLOW
    s_ok = mw.score_session(appearance="live", device_trust="known", network_risk="low")
    expect(s_ok["decision"] == "ALLOW" and s_ok["reason_code"] == "session_clear", f"s_ok {s_ok}")
    m2 = mw.create_mandate(["pay"], max_steps=5)
    t_ok = mw.evaluate_actus(m2["mandate_id"], "pay", {"payee": "acme", "amount_cents": 50})
    expect(t_ok["decision"] == "ALLOW" and t_ok["reason_code"] == "watch_clear", f"t_ok {t_ok}")
    expect(t_ok["their_production"] is False, "t_ok production")
    expect(mw.get_receipt(t_ok["receipt_id"]) is not None, "t_ok stranger receipt")

    assert_all_receipts_lab(mw)

    print("MOUTH_WATCH_PROVE_OK")
    print(
        {
            "denies": [
                s1["reason_code"],
                s2["reason_code"],
                t1["reason_code"],
                t2["reason_code"],
                t3["reason_code"],
            ],
            "allow_receipt": t_ok["receipt_id"],
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
