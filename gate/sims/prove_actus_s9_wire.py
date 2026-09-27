#!/usr/bin/env python3
"""Prove S1↔S9 wire: canary trip and hostile session as SEPARATE scenarios.

Clearance DENY (receipt_class=clearance) must link to a distinct threat receipt
(receipt_class=threat). Ordinary no_mandate DENY must NOT carry threat fields.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import actus_fence as af  # noqa: E402
from gate.sims import mouth_watch as mw  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    af.reset()
    mw.reset()

    # --- baseline: ordinary clearance DENY is NOT a threat object ---
    r0 = af.execute("pay", {"payee": "acme", "amount_cents": 100})
    expect(r0["receipt_class"] == "clearance", f"r0 class {r0}")
    expect(r0["watch_block"] is False, "r0 no watch_block")
    expect(r0["threat_receipt_id"] is None, "r0 no threat link")
    expect(r0["threat_class"] is None, "r0 no threat_class")
    expect(r0["reason_code"] == "no_mandate", f"r0 {r0}")

    # ========== SCENARIO A: canary trip alone (clean session) ==========
    af.reset()
    mw.reset()
    watch_m = mw.create_mandate(["pay", "vault_exfil"], max_steps=5)
    decoy = {"vault": "prod", "canary": True}
    canary = mw.plant_canary("vault_exfil", decoy)

    m = af.create_mandate(
        ["pay", "vault_exfil"], max_amount_cents=5000, payee_allowlist=["acme"]
    )
    dig = af.action_digest("vault_exfil", decoy)
    g = af.create_grant(m["mandate_id"], dig)

    canary_block = af.execute(
        "vault_exfil",
        decoy,
        mandate_id=m["mandate_id"],
        grant_id=g["grant_id"],
        watch_session={"appearance": "live", "device_trust": "known", "network_risk": "low"},
        watch_mandate_id=watch_m["mandate_id"],
    )
    expect(canary_block["receipt_class"] == "clearance", "A clearance wrapper")
    expect(canary_block["decision"] == "DENY", "A DENY")
    expect(canary_block["reason_code"] == "watch_blocked", f"A reason {canary_block}")
    expect(canary_block["watch_block"] is True, "A watch_block")
    expect(canary_block["threat_class"] == "canary", f"A threat_class {canary_block}")
    tid = canary_block["threat_receipt_id"]
    expect(tid is not None, "A threat_receipt_id")
    threat = mw.get_receipt(tid)
    expect(threat is not None, "A stranger threat fetch")
    expect(threat["receipt_class"] == "threat", "A linked object is threat")
    expect(threat["threat_class"] == "canary", "A linked canary")
    expect(threat["reason_code"] == "canary_tripped", f"A threat reason {threat}")
    expect(threat["result"]["canary_id"] == canary["canary_id"], "A canary id")
    expect(threat["effect"]["session_lockout"] is False, "A no lockout")

    # After canary DENY, a different non-canary actus still ALLOWs
    # (deny-this-actus only — no session lockout)
    pay_payload = {"payee": "acme", "amount_cents": 50}
    pay_dig = af.action_digest("pay", pay_payload)
    g_pay = af.create_grant(m["mandate_id"], pay_dig)
    after = af.execute(
        "pay",
        pay_payload,
        mandate_id=m["mandate_id"],
        grant_id=g_pay["grant_id"],
        watch_session={"appearance": "live", "device_trust": "known", "network_risk": "low"},
        watch_mandate_id=watch_m["mandate_id"],
    )
    expect(after["decision"] == "ALLOW", f"A after canary still ALLOW {after}")
    expect(after["receipt_class"] == "clearance", "A after clearance")

    # ========== SCENARIO B: hostile session alone (no canary) ==========
    af.reset()
    mw.reset()
    watch_m2 = mw.create_mandate(["pay"], max_steps=5)
    m2 = af.create_mandate(["pay"], max_amount_cents=5000, payee_allowlist=["acme"])
    pay2 = {"payee": "acme", "amount_cents": 75}
    dig2 = af.action_digest("pay", pay2)
    g2 = af.create_grant(m2["mandate_id"], dig2)

    hostile = af.execute(
        "pay",
        pay2,
        mandate_id=m2["mandate_id"],
        grant_id=g2["grant_id"],
        watch_session={
            "appearance": "synthetic_suspect",
            "device_trust": "known",
            "network_risk": "low",
        },
        watch_mandate_id=watch_m2["mandate_id"],
    )
    expect(hostile["receipt_class"] == "clearance", "B clearance wrapper")
    expect(hostile["decision"] == "DENY", "B DENY")
    expect(hostile["reason_code"] == "watch_blocked", f"B reason {hostile}")
    expect(hostile["watch_block"] is True, "B watch_block")
    expect(hostile["threat_class"] == "session_integrity", f"B threat_class {hostile}")
    tid2 = hostile["threat_receipt_id"]
    expect(tid2 is not None, "B threat_receipt_id")
    threat2 = mw.get_receipt(tid2)
    expect(threat2 is not None and threat2["receipt_class"] == "threat", "B threat object")
    expect(threat2["threat_class"] == "session_integrity", "B session_integrity")
    expect(threat2["reason_code"] == "session_hostile", f"B threat reason {threat2}")
    expect(threat2["effect"]["deny_this_actus"] is True, "B deny this")
    expect(threat2["effect"]["session_lockout"] is False, "B no lockout")
    expect(threat2["effect"]["alert_fanout"] is False, "B no alert fanout")
    expect(tid2 != tid, "B threat id ≠ A threat id")
    expect(hostile["threat_class"] != "canary", "B not conflated with canary")

    # Control: clean session + valid grant → ALLOW
    af.reset()
    mw.reset()
    watch_m3 = mw.create_mandate(["pay"], max_steps=5)
    m3 = af.create_mandate(["pay"], max_amount_cents=5000, payee_allowlist=["acme"])
    pay3 = {"payee": "acme", "amount_cents": 25}
    dig3 = af.action_digest("pay", pay3)
    g3 = af.create_grant(m3["mandate_id"], dig3)
    ok = af.execute(
        "pay",
        pay3,
        mandate_id=m3["mandate_id"],
        grant_id=g3["grant_id"],
        watch_session={"appearance": "live", "device_trust": "known", "network_risk": "low"},
        watch_mandate_id=watch_m3["mandate_id"],
    )
    expect(ok["decision"] == "ALLOW", f"control ALLOW {ok}")
    expect(ok["watch_block"] is False, "control no watch_block")
    expect(ok["threat_receipt_id"] is None, "control no threat link")

    assert_all_receipts_lab(af)
    assert_all_receipts_lab(mw)

    print("ACTUS_S9_WIRE_PROVE_OK")
    print(
        {
            "scenario_a_canary": {
                "clearance_reason": canary_block["reason_code"],
                "threat_class": canary_block["threat_class"],
                "after_still_allow": True,
            },
            "scenario_b_hostile_session": {
                "clearance_reason": hostile["reason_code"],
                "threat_class": hostile["threat_class"],
            },
            "receipt_classes": {"clearance": "actus", "threat": "mouth_watch"},
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
