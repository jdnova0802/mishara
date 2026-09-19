#!/usr/bin/env python3
"""Prove Z1 ISDA DC Publish — headline ≠ Credit Event. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import isda_dc_publish as dc  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    dc.reset()

    # 1) headline / scrape alone → DENY (never scrape-allow)
    r1 = dc.treat_as_credit_event(
        "ACME_CORP",
        "Bankruptcy",
        source="headline",
        headline="ACME files for Chapter 11",
    )
    expect(r1["decision"] == "DENY" and r1["reason_code"] == "headline_only", f"r1 {r1}")
    expect(r1["receipt_class"] == "clearance", "r1 class")
    expect(r1["result"]["never_scrape_allow"] is True, "r1 never scrape")

    # 2) no resolution → DENY
    r2 = dc.treat_as_credit_event("ACME_CORP", "Bankruptcy", source="agent")
    expect(r2["reason_code"] == "no_resolution", f"r2 {r2}")

    # 3) draft meeting statement → DENY
    draft = dc.plant_resolution(
        entity="ACME_CORP",
        event_type="Bankruptcy",
        status="draft",
        deliverables=["SUN-1"],
    )
    r3 = dc.treat_as_credit_event(
        "ACME_CORP",
        "Bankruptcy",
        resolution_id=draft["resolution_id"],
        source="agent",
    )
    expect(r3["reason_code"] == "draft_only", f"r3 {r3}")
    expect(r3["result"]["meeting_statement_not_binding"] is True, "r3 draft")

    # 4) resolution mismatch → DENY
    live_other = dc.plant_resolution(
        entity="ARDAGH_FIXTURE",
        event_type="Restructuring",
        status="LIVE",
        deliverables=["SSN"],
        auction_terms={"auction_date": "2026-03-01"},
    )
    r4 = dc.treat_as_credit_event(
        "ACME_CORP",
        "Bankruptcy",
        resolution_id=live_other["resolution_id"],
        source="agent",
    )
    expect(r4["reason_code"] == "resolution_mismatch", f"r4 {r4}")

    # 5) LIVE Resolution → ALLOW + stranger receipt
    live = dc.plant_resolution(
        entity="ACME_CORP",
        event_type="Bankruptcy",
        status="LIVE",
        deliverables=["BOND-2028", "BOND-2030"],
        auction_terms={"auction_date": "2026-04-01", "region": "Americas"},
    )
    r5 = dc.treat_as_credit_event(
        "ACME_CORP",
        "Bankruptcy",
        resolution_id=live["resolution_id"],
        source="agent",
    )
    expect(r5["decision"] == "ALLOW" and r5["reason_code"] == "dc_resolution_live", f"r5 {r5}")
    expect(r5["result"]["binding"] is True, "r5 binding")
    expect(r5["result"]["real_dc"] is False, "r5 lab")
    expect(r5["result"]["auction_terms_hash"] == live["auction_terms_hash"], "r5 auction link")
    expect(dc.get_receipt(r5["receipt_id"]) is not None, "r5 store")

    # publish path: draft → publish → ALLOW
    d2 = dc.plant_resolution(
        entity="AVON_FIXTURE",
        event_type="FailureToPay",
        status="draft",
        deliverables=["NOTE-A"],
    )
    pub = dc.publish_resolution(d2["resolution_id"])
    expect(pub["reason_code"] == "resolution_published", f"pub {pub}")
    r6 = dc.treat_as_credit_event(
        "AVON_FIXTURE",
        "FailureToPay",
        resolution_id=d2["resolution_id"],
        source="agent",
    )
    expect(r6["decision"] == "ALLOW", f"r6 {r6}")

    with stranger_verify() as srv:
        http = stranger_fetch(srv.base_url, r5["receipt_url"])
        expect(http["reason_code"] == "dc_resolution_live", "http allow")
        http_deny = stranger_fetch(srv.base_url, r1["receipt_url"])
        expect(http_deny["reason_code"] == "headline_only", "http headline deny")

    assert_all_receipts_lab(dc)

    print("ISDA_DC_PUBLISH_PROVE_OK")
    print(
        {
            "denies": [
                r1["reason_code"],
                r2["reason_code"],
                r3["reason_code"],
                r4["reason_code"],
            ],
            "allow_receipt": r5["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
