#!/usr/bin/env python3
"""Prove Z9 Peerage Roll — claimed title ≠ Crown recognition. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import peerage_roll as pr  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    pr.reset()

    # 1) self-style only → DENY
    r1 = pr.enter_roll(None, self_style_only=True)
    expect(r1["decision"] == "DENY" and r1["reason_code"] == "self_style_insufficient", f"r1 {r1}")
    expect(r1["result"]["claimed_title_is_not_roll_entry"] is True, "r1 cut")
    expect(r1["receipt_class"] == "clearance", "r1 class")

    # 2) no claim → DENY
    r2 = pr.enter_roll(None)
    expect(r2["reason_code"] == "no_claim", f"r2 {r2}")

    # 3) short-form / no long-form → DENY
    c3 = pr.submit_claim(
        dignity="Baron Fixture of Lab",
        claimant="A. Claimant",
        long_form_certs=False,
        senior_lines_extinct=True,
        petition_filed=True,
    )
    r3 = pr.enter_roll(c3["claim_id"], short_form_certs=True)
    expect(r3["reason_code"] == "evidence_insufficient", f"r3 {r3}")

    # 4) senior line unproven → DENY
    c4 = pr.submit_claim(
        dignity="Viscount Fixture",
        claimant="B. Claimant",
        long_form_certs=True,
        senior_lines_extinct=False,
        petition_filed=True,
    )
    r4 = pr.enter_roll(c4["claim_id"])
    expect(r4["reason_code"] == "senior_line_unproven", f"r4 {r4}")

    # 5) petition missing → DENY
    c5 = pr.submit_claim(
        dignity="Earl Fixture",
        claimant="C. Claimant",
        long_form_certs=True,
        senior_lines_extinct=True,
        petition_filed=False,
    )
    r5 = pr.enter_roll(c5["claim_id"])
    expect(r5["reason_code"] == "petition_missing", f"r5 {r5}")

    # 6) full package → ALLOW on Roll
    c6 = pr.submit_claim(
        dignity="Baron Nisaba of Concrescence",
        claimant="D. Claimant",
        long_form_certs=True,
        senior_lines_extinct=True,
        petition_filed=True,
    )
    r6 = pr.enter_roll(c6["claim_id"])
    expect(r6["decision"] == "ALLOW" and r6["reason_code"] == "entered_on_roll", f"r6 {r6}")
    expect(r6["result"]["real_crown"] is False, "r6 lab")
    expect(pr.get_receipt(r6["receipt_id"]) is not None, "r6 store")

    with stranger_verify() as srv:
        http_deny = stranger_fetch(srv.base_url, r1["receipt_url"])
        expect(http_deny["reason_code"] == "self_style_insufficient", "http self-style")
        http_ok = stranger_fetch(srv.base_url, r6["receipt_url"])
        expect(http_ok["reason_code"] == "entered_on_roll", "http roll")

    assert_all_receipts_lab(pr)

    print("PEERAGE_ROLL_PROVE_OK")
    print(
        {
            "denies": [
                r1["reason_code"],
                r2["reason_code"],
                r3["reason_code"],
                r4["reason_code"],
                r5["reason_code"],
            ],
            "roll_receipt": r6["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
