#!/usr/bin/env python3
"""Prove S1 Actus Fence DENY paths. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import actus_fence as af  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    af.reset()

    # 1) pay without mandate → DENY
    r1 = af.execute("pay", {"payee": "acme", "amount_cents": 100})
    expect(r1["decision"] == "DENY", f"r1 {r1}")
    expect(r1["reason_code"] == "no_mandate", f"r1 reason {r1}")
    expect(r1["their_production"] is False, "r1 production")
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

    assert_all_receipts_lab(af)

    print("ACTUS_FENCE_PROVE_OK")
    print(
        {
            "denies": [r1["reason_code"], r2["reason_code"], r3["reason_code"], r5["reason_code"]],
            "allow_receipt": r4["receipt_id"],
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
