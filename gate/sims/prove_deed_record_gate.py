#!/usr/bin/env python3
"""Prove S6 Deed Record Gate DENY paths + S9 watch feed + stranger HTTP."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import deed_record_gate as dr  # noqa: E402
from gate.sims import mouth_watch as mw  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    dr.reset()
    mw.reset()
    dr.set_parcel_policy("PARCEL-A", owner_lock=False, require_notary=False)
    dr.set_parcel_policy("PARCEL-LOCKED", owner_lock=True, require_notary=False)
    dr.set_parcel_policy("PARCEL-NOTARY", owner_lock=False, require_notary=True)
    seal = "NOTARY-LIVE-1"
    dr.register_notary_seal(seal)

    # 1) inject_suspect → DENY
    i1 = dr.create_instrument(
        parcel_id="PARCEL-A",
        grantor="Alice",
        grantee="Bob",
        doc_hash="doc-a1",
    )
    r1 = dr.record_instrument(i1["instrument_id"], id_assurance="inject_suspect")
    expect(r1["decision"] == "DENY" and r1["reason_code"] == "id_assurance_inject_suspect", f"r1 {r1}")
    expect(r1["receipt_class"] == "clearance", "r1 class")
    expect(dr.get_receipt(r1["receipt_id"]) is not None, "r1 stranger receipt")

    # 2) locked parcel without unlock → DENY
    i2 = dr.create_instrument(
        parcel_id="PARCEL-LOCKED",
        grantor="Carol",
        grantee="Dave",
        doc_hash="doc-l1",
    )
    r2 = dr.record_instrument(i2["instrument_id"], id_assurance="live")
    expect(r2["decision"] == "DENY" and r2["reason_code"] == "owner_lock_no_unlock", f"r2 {r2}")

    # 3) require notary, missing seal → DENY
    i3 = dr.create_instrument(
        parcel_id="PARCEL-NOTARY",
        grantor="Eve",
        grantee="Frank",
        doc_hash="doc-n1",
    )
    r3 = dr.record_instrument(i3["instrument_id"], id_assurance="live")
    expect(r3["decision"] == "DENY" and r3["reason_code"] == "notary_seal_missing_or_revoked", f"r3 {r3}")

    # 4) clean LIVE ALLOW + receipt
    unlock = dr.issue_unlock_grant("PARCEL-LOCKED")
    i4 = dr.create_instrument(
        parcel_id="PARCEL-LOCKED",
        grantor="Carol",
        grantee="Grace",
        doc_hash="doc-l2",
    )
    r4 = dr.record_instrument(i4["instrument_id"], id_assurance="live", unlock_grant=unlock)
    expect(r4["decision"] == "ALLOW" and r4["reason_code"] == "recorded", f"r4 {r4}")
    expect(r4["result"]["parcel_id"] == "PARCEL-LOCKED", "r4 parcel")
    expect(r4["their_production"] is False, "r4 production")
    expect(dr.get_receipt(r4["receipt_id"]) is not None, "r4 stranger receipt")

    # 5) unknown appearance / assurance → DENY
    i5 = dr.create_instrument(
        parcel_id="PARCEL-A",
        grantor="Alice",
        grantee="Hank",
        doc_hash="doc-a2",
    )
    r5 = dr.record_instrument(i5["instrument_id"], id_assurance="unknown")
    expect(r5["decision"] == "DENY" and r5["reason_code"] == "id_assurance_unknown", f"r5 {r5}")

    # 6) S9 watch hostile → DENY + linked threat (id_assurance live)
    i6 = dr.create_instrument(
        parcel_id="PARCEL-A",
        grantor="Alice",
        grantee="Ivy",
        doc_hash="doc-a3",
    )
    r6 = dr.record_instrument(
        i6["instrument_id"],
        id_assurance="live",
        watch_session={
            "appearance": "synthetic_suspect",
            "device_trust": "known",
            "network_risk": "low",
        },
    )
    expect(r6["reason_code"] == "watch_blocked", f"r6 {r6}")
    expect(r6["watch_block"] is True, "r6 watch")
    expect(r6["threat_class"] == "session_integrity", "r6 threat class")
    expect(mw.get_receipt(r6["threat_receipt_id"])["receipt_class"] == "threat", "r6 threat obj")

    with stranger_verify() as srv:
        http_record = stranger_fetch(srv.base_url, r4["receipt_url"])
        expect(http_record["reason_code"] == "recorded", "http record")
        http_watch = stranger_fetch(srv.base_url, r6["receipt_url"])
        expect(http_watch["watch_block"] is True, "http watch deny")
        http_threat = stranger_fetch(srv.base_url, r6["result"]["threat_receipt_url"])
        expect(http_threat["receipt_class"] == "threat", "http threat")

    assert_all_receipts_lab(dr)
    assert_all_receipts_lab(mw)

    print("DEED_RECORD_GATE_PROVE_OK")
    print(
        {
            "denies": [r1["reason_code"], r2["reason_code"], r3["reason_code"], r5["reason_code"], r6["reason_code"]],
            "recorded_receipt": r4["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
