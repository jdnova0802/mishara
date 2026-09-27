#!/usr/bin/env python3
"""Prove Z2 CLS Settle — matched trade ≠ settled PvP. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import cls_settle as cls  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    cls.reset()
    cls.register_member("MEM-A")
    cls.register_member("MEM-B")

    # 1) settle unmatched → DENY
    a = cls.submit_instruction(
        member_id="MEM-A",
        buy_ccy="EUR",
        sell_ccy="USD",
        buy_amount="1000000",
        sell_amount="1100000",
    )
    expect("instruction_id" in a, f"a {a}")
    s1 = cls.settle(a["instruction_id"])
    expect(s1["decision"] == "DENY" and s1["reason_code"] == "unmatched", f"s1 {s1}")
    expect(s1["result"]["matched_trade_is_not_settled"] is True, "s1 cut")
    expect(s1["receipt_class"] == "clearance", "s1 class")

    # 2) match + risk fail → DENY
    b = cls.submit_instruction(
        member_id="MEM-B",
        buy_ccy="USD",
        sell_ccy="EUR",
        buy_amount="1100000",
        sell_amount="1000000",
    )
    m = cls.match_instructions(a["instruction_id"], b["instruction_id"])
    expect(m["matched"] is True, f"m {m}")
    s2 = cls.settle(a["instruction_id"], risk_ok=False)
    expect(s2["reason_code"] == "risk_test_failed", f"s2 {s2}")

    # 3) pay-in shortage → DENY (Herstatt guard)
    s3 = cls.settle(a["instruction_id"], risk_ok=True, counterparty_funded=False)
    expect(s3["reason_code"] == "pay_in_shortage", f"s3 {s3}")
    expect(s3["result"]["herstatt_guard"] is True, "s3 herstatt")

    # 4) clean PvP → ALLOW final irrevocable
    s4 = cls.settle(a["instruction_id"], risk_ok=True, counterparty_funded=True)
    expect(s4["decision"] == "ALLOW" and s4["reason_code"] == "settled_pvp", f"s4 {s4}")
    expect(s4["result"]["final"] is True and s4["result"]["irrevocable"] is True, "s4 final")
    expect(s4["result"]["real_cls"] is False, "s4 lab")
    expect(cls.get_receipt(s4["receipt_id"]) is not None, "s4 store")

    # 5) suspended member → DENY
    cls.suspend_member("MEM-A")
    a2 = cls.submit_instruction(
        member_id="MEM-A",
        buy_ccy="GBP",
        sell_ccy="USD",
        buy_amount="1",
        sell_amount="1",
    )
    expect(a2["reason_code"] == "member_suspended", f"a2 {a2}")

    # 6) unsupported currency → DENY
    cls.register_member("MEM-C")
    bad = cls.submit_instruction(
        member_id="MEM-C",
        buy_ccy="XYZ",
        sell_ccy="USD",
        buy_amount="1",
        sell_amount="1",
    )
    expect(bad["reason_code"] == "currency_unsupported", f"bad {bad}")

    with stranger_verify() as srv:
        http_deny = stranger_fetch(srv.base_url, s1["receipt_url"])
        expect(http_deny["reason_code"] == "unmatched", "http unmatched")
        http_ok = stranger_fetch(srv.base_url, s4["receipt_url"])
        expect(http_ok["reason_code"] == "settled_pvp", "http settled")

    assert_all_receipts_lab(cls)

    print("CLS_SETTLE_PROVE_OK")
    print(
        {
            "denies": [
                s1["reason_code"],
                s2["reason_code"],
                s3["reason_code"],
                a2["reason_code"],
                bad["reason_code"],
            ],
            "settle_receipt": s4["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
