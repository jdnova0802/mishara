#!/usr/bin/env python3
"""Prove Z5 ITU BIU/MIFR — paper filing ≠ recorded assignment. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import itu_biu_mifr as itu  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    itu.reset()

    # 1) API-only paper satellite → DENY record
    paper = itu.submit_filing(
        admin="USA",
        network_name="PAPER-SAT-1",
        orbital_slot="100.0E",
        freq_band="Ku",
        status="api",
    )
    r1 = itu.notify_and_record(paper["filing_id"])
    expect(r1["decision"] == "DENY" and r1["reason_code"] == "api_only_paper", f"r1 {r1}")
    expect(r1["result"]["paper_satellite"] is True, "r1 paper")
    expect(r1["result"]["filing_is_not_assignment"] is True, "r1 cut")
    expect(r1["receipt_class"] == "clearance", "r1 class")

    # 2) coordination incomplete → DENY
    f2 = itu.submit_filing(
        admin="FRA",
        network_name="COORD-WAIT",
        orbital_slot="10.0W",
        freq_band="Ka",
        status="coordination",
    )
    r2 = itu.notify_and_record(f2["filing_id"])
    expect(r2["reason_code"] == "coordination_incomplete", f"r2 {r2}")

    # 3) coordinated but BIU < 90 days → DENY
    itu.mark_coordinated(f2["filing_id"])
    itu.record_biu(f2["filing_id"], biu_days=30, evidence=True)
    r3 = itu.notify_and_record(f2["filing_id"])
    expect(r3["reason_code"] == "biu_period_insufficient", f"r3 {r3}")

    # 4) 90 days but no evidence → DENY
    itu.record_biu(f2["filing_id"], biu_days=90, evidence=False)
    r4 = itu.notify_and_record(f2["filing_id"])
    expect(r4["reason_code"] == "biu_evidence_missing", f"r4 {r4}")

    # 5) coordination + BIU 90 + evidence → MIFR ALLOW
    itu.record_biu(f2["filing_id"], biu_days=90, evidence=True)
    r5 = itu.notify_and_record(f2["filing_id"])
    expect(r5["decision"] == "ALLOW" and r5["reason_code"] == "mifr_recorded", f"r5 {r5}")
    expect(r5["result"]["real_itu"] is False, "r5 lab")
    expect(r5["result"]["protection"] is True, "r5 protection")
    expect(itu.get_receipt(r5["receipt_id"]) is not None, "r5 store")

    # 6) no filing → DENY
    r6 = itu.notify_and_record("missing")
    expect(r6["reason_code"] == "no_filing", f"r6 {r6}")

    with stranger_verify() as srv:
        http_paper = stranger_fetch(srv.base_url, r1["receipt_url"])
        expect(http_paper["reason_code"] == "api_only_paper", "http paper")
        http_ok = stranger_fetch(srv.base_url, r5["receipt_url"])
        expect(http_ok["reason_code"] == "mifr_recorded", "http mifr")

    assert_all_receipts_lab(itu)

    print("ITU_BIU_MIFR_PROVE_OK")
    print(
        {
            "denies": [
                r1["reason_code"],
                r2["reason_code"],
                r3["reason_code"],
                r4["reason_code"],
                r6["reason_code"],
            ],
            "mifr_receipt": r5["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
