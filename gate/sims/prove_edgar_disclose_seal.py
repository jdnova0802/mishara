#!/usr/bin/env python3
"""Prove S7 EDGAR Disclose Seal DENY paths + EDGAR gateway weld + stranger HTTP."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import edgar_disclose_seal as ed  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    ed.reset()

    # 1) hallucinated revenue → seal DENY → submit DENY
    fake = ed.create_filing(
        "10-K",
        [
            {
                "claim_id": "c1",
                "text": "Revenue was $9,999,999,999",
                "fact_ref": "FY2025_REVENUE_USD",
                "asserted_value": 9_999_999_999,
            }
        ],
    )
    s1 = ed.seal_filing(fake["filing_id"])
    expect(s1["decision"] == "DENY" and s1["reason_code"] == "seal_failed", f"s1 {s1}")
    expect(s1["receipt_class"] == "clearance", "s1 class")
    expect(any(f["reason"] == "hallucinated_quantity" for f in s1["failures"]), f"s1 fail {s1}")
    sub1 = ed.submit_filing(fake["filing_id"], seal_id=s1.get("seal_id"))
    expect(sub1["decision"] == "DENY", f"sub1 {sub1}")
    gw1 = ed.submit_edgar_gateway(fake["filing_id"], seal_id=s1.get("seal_id"))
    expect(gw1["reason_code"] == "edgar_block_no_seal", f"gw1 {gw1}")
    expect(ed.get_receipt(s1["receipt_id"]) is not None, "s1 stranger receipt")

    # 2) number in text with no fact_ref → DENY
    ungrounded = ed.create_filing(
        "8-K",
        [
            {
                "claim_id": "c2",
                "text": "Cash on hand reached 999000000 dollars",
            }
        ],
    )
    s2 = ed.seal_filing(ungrounded["filing_id"])
    expect(s2["decision"] == "DENY", f"s2 {s2}")
    expect(any(f["reason"] == "ungrounded_claim" for f in s2["failures"]), f"s2 {s2}")

    # 3) grounded → seal ALLOW → submit ALLOW + receipt
    good = ed.create_filing(
        "10-K",
        [
            {
                "claim_id": "c3",
                "text": "FY2025 revenue was 1250000000 USD",
                "fact_ref": "FY2025_REVENUE_USD",
                "asserted_value": 1_250_000_000,
            },
            {
                "claim_id": "c4",
                "text": "Net income was 180000000 USD",
                "fact_ref": "FY2025_NET_INCOME_USD",
                "asserted_value": 180_000_000,
            },
        ],
    )
    s3 = ed.seal_filing(good["filing_id"])
    expect(s3["decision"] == "ALLOW" and s3["seal_id"], f"s3 {s3}")
    sub3 = ed.submit_filing(good["filing_id"], seal_id=s3["seal_id"])
    expect(sub3["decision"] == "ALLOW" and sub3["reason_code"] == "submitted", f"sub3 {sub3}")
    expect(sub3["result"]["seal_id"] == s3["seal_id"], "sub3 seal link")
    expect(sub3["their_production"] is False, "sub3 production")
    expect(ed.get_receipt(sub3["receipt_id"]) is not None, "sub3 stranger receipt")

    gw3 = ed.submit_edgar_gateway(good["filing_id"], seal_id=s3["seal_id"])
    expect(gw3["decision"] == "ALLOW" and gw3["reason_code"] == "edgar_submitted", f"gw3 {gw3}")
    expect(gw3["result"]["real_edgar"] is False, "gw3 lab")
    expect(gw3["result"]["edgar_gateway"] == "lab_fixture", "gw3 fixture")

    # 4) submit without seal → DENY
    bare = ed.create_filing(
        "10-Q",
        [
            {
                "claim_id": "c5",
                "text": "Cash was 420000000",
                "fact_ref": "Q1_2026_CASH_USD",
                "asserted_value": 420_000_000,
            }
        ],
    )
    sub4 = ed.submit_filing(bare["filing_id"])
    expect(sub4["decision"] == "DENY" and sub4["reason_code"] == "no_seal", f"sub4 {sub4}")
    gw4 = ed.submit_edgar_gateway(bare["filing_id"])
    expect(gw4["decision"] == "DENY" and gw4["reason_code"] == "edgar_block_no_seal", f"gw4 {gw4}")
    expect(gw4["result"]["edgar_block"] is True, "gw4 block flag")

    with stranger_verify() as srv:
        http_deny = stranger_fetch(srv.base_url, s1["receipt_url"])
        expect(http_deny["reason_code"] == "seal_failed", "http seal deny")
        http_gw = stranger_fetch(srv.base_url, gw3["receipt_url"])
        expect(http_gw["reason_code"] == "edgar_submitted", "http gw allow")
        http_block = stranger_fetch(srv.base_url, gw4["receipt_url"])
        expect(http_block["reason_code"] == "edgar_block_no_seal", "http gw block")

    assert_all_receipts_lab(ed)

    print("EDGAR_DISCLOSE_SEAL_PROVE_OK")
    print(
        {
            "denies": [s1["reason_code"], s2["reason_code"], sub4["reason_code"], gw4["reason_code"]],
            "submitted_receipt": sub3["receipt_id"],
            "edgar_gateway_receipt": gw3["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
