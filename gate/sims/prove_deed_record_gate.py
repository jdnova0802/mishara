#!/usr/bin/env python3
"""Prove S6 Deed Record Gate DENY paths. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import deed_record_gate as dr  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    dr.reset()
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

    print("DEED_RECORD_GATE_PROVE_OK")
    print(
        {
            "denies": [r1["reason_code"], r2["reason_code"], r3["reason_code"], r5["reason_code"]],
            "recorded_receipt": r4["receipt_id"],
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
