#!/usr/bin/env python3
"""Prove S1 Actus Fence DENY paths + P0 bank-send weld + stranger HTTP verify.

Lab only. Not Fidacy/Visa TAP.
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
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    af.reset()
    mw.reset()

    # 1) pay without mandate → DENY
    r1 = af.execute("pay", {"payee": "acme", "amount_cents": 100})
    expect(r1["decision"] == "DENY", f"r1 {r1}")
    expect(r1["reason_code"] == "no_mandate", f"r1 reason {r1}")
    expect(r1["their_production"] is False, "r1 production")
    expect(r1["receipt_class"] == "clearance", "r1 class")
    expect(af.get_receipt(r1["receipt_id"]) is not None, "r1 stranger receipt")

    # 2) mandate but no grant → DENY
    m = af.create_mandate(["pay"], max_amount_cents=5000, payee_allowlist=["acme"])
    r2 = af.execute(
        "pay",
        {"payee": "acme", "amount_cents": 100},
        mandate_id=m["mandate_id"],
    )
    expect(r2["decision"] == "DENY" and r2["reason_code"] == "no_grant", f"r2 {r2}")

    # 3) grant for digest A, execute digest B → DENY
    payload_a = {"payee": "acme", "amount_cents": 100}
    payload_b = {"payee": "acme", "amount_cents": 200}
    dig_a = af.action_digest("pay", payload_a)
    g = af.create_grant(m["mandate_id"], dig_a)
    expect("grant_id" in g, f"grant {g}")
    r3 = af.execute(
        "pay",
        payload_b,
        mandate_id=m["mandate_id"],
        grant_id=g["grant_id"],
    )
    expect(r3["decision"] == "DENY" and r3["reason_code"] == "digest_mismatch", f"r3 {r3}")

    # 4) valid grant → ALLOW + receipt links
    g2 = af.create_grant(m["mandate_id"], dig_a)
    r4 = af.execute(
        "pay",
        payload_a,
        mandate_id=m["mandate_id"],
        grant_id=g2["grant_id"],
    )
    expect(r4["decision"] == "ALLOW", f"r4 {r4}")
    expect(r4["mandate_id"] == m["mandate_id"], "r4 mandate link")
    expect(r4["digest"] == dig_a, "r4 digest link")
    expect(r4["result"]["executed"] is True, "r4 executed")
    expect(r4["their_production"] is False, "r4 production")

    # 5) expired grant → DENY
    g3 = af.create_grant(m["mandate_id"], dig_a, ttl_sec=-1)
    r5 = af.execute(
        "pay",
        payload_a,
        mandate_id=m["mandate_id"],
        grant_id=g3["grant_id"],
    )
    expect(r5["decision"] == "DENY" and r5["reason_code"] == "grant_expired", f"r5 {r5}")

    # bonus: non-pay actus still needs grant
    m2 = af.create_mandate(["prod_mutate", "delete"])
    r6 = af.execute("prod_mutate", {"resource": "db.users"}, mandate_id=m2["mandate_id"])
    expect(r6["reason_code"] == "no_grant", f"r6 {r6}")

    # ========== P0: FedNow/RTP-shaped bank-send DENYs ==========
    # bank_send without mandate → DENY
    bank_payload = {
        "rail": "fednow",
        "creditor": "acme",
        "amount_cents": 2500,
        "end_to_end_id": "E2E-LAB-001",
    }
    b0 = af.execute("bank_send", bank_payload)
    expect(b0["decision"] == "DENY" and b0["reason_code"] == "no_mandate", f"b0 {b0}")
    expect(b0["receipt_class"] == "clearance", "b0 class")

    # mandate without bank_send in scope → scope_mismatch
    m_pay_only = af.create_mandate(
        ["pay"],
        max_amount_cents=10000,
        payee_allowlist=["acme"],
        allowed_rails=["fednow", "rtp"],
    )
    b1 = af.execute("bank_send", bank_payload, mandate_id=m_pay_only["mandate_id"])
    expect(b1["reason_code"] == "scope_mismatch", f"b1 {b1}")

    # bank_send in scope, rail not allowlisted → DENY
    m_rtp_only = af.create_mandate(
        ["bank_send", "fednow_push", "rtp_push"],
        max_amount_cents=10000,
        payee_allowlist=["acme"],
        allowed_rails=["rtp"],
    )
    b2 = af.execute("bank_send", bank_payload, mandate_id=m_rtp_only["mandate_id"])
    expect(b2["reason_code"] == "rail_not_allowlisted", f"b2 {b2}")

    # rail unknown → DENY
    bad_rail = {"rail": "wire_legacy", "creditor": "acme", "amount_cents": 100}
    b3 = af.execute("bank_send", bad_rail, mandate_id=m_rtp_only["mandate_id"])
    expect(b3["reason_code"] == "rail_unknown", f"b3 {b3}")

    # valid fednow_push path → ALLOW (fixture only)
    m_bank = af.create_mandate(
        ["bank_send", "fednow_push"],
        max_amount_cents=10000,
        payee_allowlist=["acme"],
        allowed_rails=["fednow"],
    )
    fed_payload = {"creditor": "acme", "amount_cents": 2500, "end_to_end_id": "E2E-LAB-002"}
    dig_fed = af.action_digest("fednow_push", fed_payload)
    g_fed = af.create_grant(m_bank["mandate_id"], dig_fed)
    b4 = af.execute(
        "fednow_push",
        fed_payload,
        mandate_id=m_bank["mandate_id"],
        grant_id=g_fed["grant_id"],
    )
    expect(b4["decision"] == "ALLOW", f"b4 {b4}")
    expect(b4["result"]["bank_send"]["rail"] == "fednow", f"b4 rail {b4}")
    expect(b4["result"]["bank_send"]["real_rail"] is False, "b4 not real rail")

    # ========== P0: stranger HTTP verify (clearance + linked threat) ==========
    with stranger_verify() as srv:
        cleared = stranger_fetch(srv.base_url, r4["receipt_url"])
        expect(cleared["receipt_id"] == r4["receipt_id"], "http clearance id")
        expect(cleared["receipt_class"] == "clearance", "http clearance class")
        expect(cleared["their_production"] is False, "http clearance lab")
        expect(cleared["decision"] == "ALLOW", "http clearance decision")

        bank_deny = stranger_fetch(srv.base_url, b2["receipt_url"])
        expect(bank_deny["reason_code"] == "rail_not_allowlisted", "http bank deny")
        expect(bank_deny["receipt_class"] == "clearance", "http bank class")

        # S9 hostile → clearance DENY linking threat; stranger fetches BOTH
        blocked = af.execute(
            "pay",
            payload_a,
            mandate_id=m["mandate_id"],
            grant_id=g2["grant_id"],
            watch_session={
                "appearance": "synthetic_suspect",
                "device_trust": "known",
                "network_risk": "low",
            },
        )
        expect(blocked["decision"] == "DENY", f"blocked {blocked}")
        expect(blocked["watch_block"] is True, "blocked watch")
        expect(blocked["threat_receipt_id"], "blocked threat id")
        expect(blocked["threat_class"] == "session_integrity", "blocked class")

        http_clearance = stranger_fetch(srv.base_url, blocked["receipt_url"])
        expect(http_clearance["receipt_class"] == "clearance", "http watch clearance")
        expect(http_clearance["threat_receipt_id"] == blocked["threat_receipt_id"], "link")

        threat_url = blocked["result"]["threat_receipt_url"]
        http_threat = stranger_fetch(srv.base_url, threat_url)
        expect(http_threat["receipt_class"] == "threat", "http threat class")
        expect(http_threat["threat_class"] == "session_integrity", "http threat kind")
        expect(http_threat["their_production"] is False, "http threat lab")
        expect(http_threat["effect"]["deny_this_actus"] is True, "trip effect")
        expect(http_threat["effect"]["session_lockout"] is False, "no lockout")

    assert_all_receipts_lab(af)
    assert_all_receipts_lab(mw)

    print("ACTUS_FENCE_PROVE_OK")
    print(
        {
            "denies": [
                r1["reason_code"],
                r2["reason_code"],
                r3["reason_code"],
                r5["reason_code"],
                b0["reason_code"],
                b1["reason_code"],
                b2["reason_code"],
                b3["reason_code"],
            ],
            "bank_send_allow": b4["receipt_id"],
            "allow_receipt": r4["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
