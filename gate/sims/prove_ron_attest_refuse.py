#!/usr/bin/env python3
"""Prove S8 RON Attest Refuse DENY paths. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import ron_attest_refuse as ron  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    ron.reset()

    # 1) synthetic_suspect → REFUSE
    s1 = ron.open_session(
        signatory_id="sig-1",
        doc_hash="deed-hash-1",
        appearance="synthetic_suspect",
    )
    a1 = ron.attest(s1["session_id"])
    expect(a1["decision"] == "REFUSE" and a1["reason_code"] == "appearance_synthetic_suspect", f"a1 {a1}")
    expect(ron.get_receipt(a1["receipt_id"]) is not None, "a1 stranger receipt")

    # 2) unknown → REFUSE
    s2 = ron.open_session(
        signatory_id="sig-2",
        doc_hash="deed-hash-2",
        appearance="unknown",
    )
    a2 = ron.attest(s2["session_id"])
    expect(a2["decision"] == "REFUSE" and a2["reason_code"] == "appearance_unknown", f"a2 {a2}")

    # 3) live + doc mismatch → REFUSE
    s3 = ron.open_session(
        signatory_id="sig-3",
        doc_hash="deed-hash-3",
        appearance="live",
    )
    a3 = ron.attest(s3["session_id"], expected_doc_hash="other-hash")
    expect(a3["decision"] == "REFUSE" and a3["reason_code"] == "doc_hash_mismatch", f"a3 {a3}")

    # 4) live ALLOW + receipt
    s4 = ron.open_session(
        signatory_id="sig-4",
        doc_hash="deed-hash-4",
        appearance="live",
    )
    a4 = ron.attest(s4["session_id"], expected_doc_hash="deed-hash-4")
    expect(a4["decision"] == "ALLOW" and a4["reason_code"] == "attested", f"a4 {a4}")
    expect(a4["result"]["doc_hash"] == "deed-hash-4", "a4 doc")
    expect(a4["their_production"] is False, "a4 production")
    expect(a4["receipt_class"] == "clearance", "a4 class")
    expect(ron.get_receipt(a4["receipt_id"]) is not None, "a4 stranger receipt")

    with stranger_verify() as srv:
        http_refuse = stranger_fetch(srv.base_url, a1["receipt_url"])
        expect(http_refuse["reason_code"] == "appearance_synthetic_suspect", "http refuse")
        http_allow = stranger_fetch(srv.base_url, a4["receipt_url"])
        expect(http_allow["decision"] == "ALLOW", "http allow")

    assert_all_receipts_lab(ron)

    print("RON_ATTEST_REFUSE_PROVE_OK")
    print(
        {
            "refuses": [a1["reason_code"], a2["reason_code"], a3["reason_code"]],
            "attested_receipt": a4["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
