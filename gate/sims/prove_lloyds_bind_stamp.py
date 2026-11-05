#!/usr/bin/env python3
"""Prove Z4 Lloyd's Bind Stamp — paperwork ≠ registered bind. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import lloyds_bind_stamp as lb  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    lb.reset()

    # 1) stamp with no BAA → DENY
    r1 = lb.stamp_bind(
        baa_id=None,
        coverholder_id="CH-1",
        syndicate_id="33",
        class_of_business="cargo",
        limit_usd=1_000_000,
        risk_ref="RISK-1",
    )
    expect(r1["decision"] == "DENY" and r1["reason_code"] == "no_baa", f"r1 {r1}")
    expect(r1["result"]["stamp_without_authority"] is True, "r1 byelaw")
    expect(r1["receipt_class"] == "clearance", "r1 class")

    # 2) draft unregistered BAA → DENY
    draft = lb.create_baa(
        coverholder_id="CH-1",
        syndicate_ids=["33", "510"],
        classes=["cargo", "hull"],
        max_limit_usd=5_000_000,
        status="draft",
        registered=False,
    )
    r2 = lb.stamp_bind(
        baa_id=draft["baa_id"],
        coverholder_id="CH-1",
        syndicate_id="33",
        class_of_business="cargo",
        limit_usd=500_000,
        risk_ref="RISK-2",
    )
    expect(r2["reason_code"] == "baa_not_registered", f"r2 {r2}")

    # 3) register → LIVE; wrong syndicate → DENY
    reg = lb.register_baa(draft["baa_id"])
    expect(reg["reason_code"] == "baa_registered", f"reg {reg}")
    r3 = lb.stamp_bind(
        baa_id=draft["baa_id"],
        coverholder_id="CH-1",
        syndicate_id="999",
        class_of_business="cargo",
        limit_usd=500_000,
        risk_ref="RISK-3",
    )
    expect(r3["reason_code"] == "syndicate_not_on_baa", f"r3 {r3}")

    # 4) class out of scope → DENY
    r4 = lb.stamp_bind(
        baa_id=draft["baa_id"],
        coverholder_id="CH-1",
        syndicate_id="33",
        class_of_business="cyber",
        limit_usd=500_000,
        risk_ref="RISK-4",
    )
    expect(r4["reason_code"] == "class_out_of_scope", f"r4 {r4}")

    # 5) over limit → DENY
    r5 = lb.stamp_bind(
        baa_id=draft["baa_id"],
        coverholder_id="CH-1",
        syndicate_id="33",
        class_of_business="cargo",
        limit_usd=9_000_000,
        risk_ref="RISK-5",
    )
    expect(r5["reason_code"] == "over_authority_limit", f"r5 {r5}")

    # 6) clean LIVE registered → ALLOW
    r6 = lb.stamp_bind(
        baa_id=draft["baa_id"],
        coverholder_id="CH-1",
        syndicate_id="33",
        class_of_business="cargo",
        limit_usd=1_000_000,
        risk_ref="RISK-6",
    )
    expect(r6["decision"] == "ALLOW" and r6["reason_code"] == "bound_under_authority", f"r6 {r6}")
    expect(r6["result"]["real_lloyds"] is False, "r6 lab")
    expect(lb.get_receipt(r6["receipt_id"]) is not None, "r6 store")

    # 7) suspended → DENY
    lb.suspend_baa(draft["baa_id"])
    r7 = lb.stamp_bind(
        baa_id=draft["baa_id"],
        coverholder_id="CH-1",
        syndicate_id="33",
        class_of_business="cargo",
        limit_usd=100_000,
        risk_ref="RISK-7",
    )
    expect(r7["reason_code"] == "baa_suspended", f"r7 {r7}")

    with stranger_verify() as srv:
        http_deny = stranger_fetch(srv.base_url, r1["receipt_url"])
        expect(http_deny["reason_code"] == "no_baa", "http no baa")
        http_ok = stranger_fetch(srv.base_url, r6["receipt_url"])
        expect(http_ok["reason_code"] == "bound_under_authority", "http bound")

    assert_all_receipts_lab(lb)

    print("LLOYDS_BIND_STAMP_PROVE_OK")
    print(
        {
            "denies": [
                r1["reason_code"],
                r2["reason_code"],
                r3["reason_code"],
                r4["reason_code"],
                r5["reason_code"],
                r7["reason_code"],
            ],
            "bound_receipt": r6["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
