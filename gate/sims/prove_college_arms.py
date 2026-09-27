#!/usr/bin/env python3
"""Prove Z10 College of Arms — petition ≠ letters patent. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import college_arms as ca  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    ca.reset()

    # 1) generative crest spam → DENY
    r1 = ca.grant_arms(None, generative_spam=True)
    expect(r1["decision"] == "DENY" and r1["reason_code"] == "generative_crest_refused", f"r1 {r1}")
    expect(r1["result"]["ai_crest_is_not_letters_patent"] is True, "r1 cut")
    expect(r1["receipt_class"] == "clearance", "r1 class")

    # 2) no petition → DENY
    r2 = ca.grant_arms(None)
    expect(r2["reason_code"] == "no_petition", f"r2 {r2}")

    # 3) ineligible → DENY
    p3 = ca.submit_petition(
        petitioner="Ineligible",
        blazon="Argent a gate sable",
        eligible=False,
    )
    r3 = ca.grant_arms(p3["petition_id"])
    expect(r3["reason_code"] == "ineligible_petitioner", f"r3 {r3}")

    # 4) honorary without pedigree → DENY
    p4 = ca.submit_petition(
        petitioner="US Citizen",
        blazon="Or a scroll azure",
        honorary=True,
        pedigree_recorded=False,
    )
    r4 = ca.grant_arms(p4["petition_id"])
    expect(r4["reason_code"] == "honorary_pedigree_missing", f"r4 {r4}")

    # 5) collision with prior arms → DENY
    p5 = ca.submit_petition(
        petitioner="Collider",
        blazon="Azure lion rampant or",  # seeded prior
    )
    r5 = ca.grant_arms(p5["petition_id"])
    expect(r5["reason_code"] == "arms_not_distinct", f"r5 {r5}")

    # 6) Kings of Arms refuse → DENY
    p6 = ca.submit_petition(
        petitioner="Refused",
        blazon="Vert a unique key argent numbered 42",
    )
    r6 = ca.grant_arms(p6["petition_id"], kings_of_arms_approve=False)
    expect(r6["reason_code"] == "kings_of_arms_refused", f"r6 {r6}")

    # 7) clean petition → letters patent ALLOW
    p7 = ca.submit_petition(
        petitioner="Grantee",
        blazon="Sable a mouth argent between three receipts or",
    )
    r7 = ca.grant_arms(p7["petition_id"])
    expect(r7["decision"] == "ALLOW" and r7["reason_code"] == "letters_patent_sealed", f"r7 {r7}")
    expect(r7["result"]["real_college"] is False, "r7 lab")
    expect(r7["result"]["sealed"] is True, "r7 sealed")
    expect(ca.get_receipt(r7["receipt_id"]) is not None, "r7 store")

    with stranger_verify() as srv:
        http_deny = stranger_fetch(srv.base_url, r1["receipt_url"])
        expect(http_deny["reason_code"] == "generative_crest_refused", "http spam")
        http_ok = stranger_fetch(srv.base_url, r7["receipt_url"])
        expect(http_ok["reason_code"] == "letters_patent_sealed", "http patent")

    assert_all_receipts_lab(ca)

    print("COLLEGE_ARMS_PROVE_OK")
    print(
        {
            "denies": [
                r1["reason_code"],
                r2["reason_code"],
                r3["reason_code"],
                r4["reason_code"],
                r5["reason_code"],
                r6["reason_code"],
            ],
            "grant_receipt": r7["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
