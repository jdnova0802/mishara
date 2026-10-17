#!/usr/bin/env python3
"""Prove Z7 KP Export — parcel ≠ KP-certified export. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import kp_export as kp  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    kp.reset()

    # 1) no certificate → DENY
    r1 = kp.export_rough(
        certificate_id=None,
        exporting_country="ZA",
        importing_country="BE",
        carat="100.5",
        value_usd="500000",
    )
    expect(r1["decision"] == "DENY" and r1["reason_code"] == "no_certificate", f"r1 {r1}")
    expect(r1["result"]["parcel_present_is_not_certified"] is True, "r1 cut")
    expect(r1["receipt_class"] == "clearance", "r1 class")

    # 2) non-participant → DENY at issue
    bad = kp.issue_certificate(
        exporting_country="XX",
        importing_country="BE",
        carat="10",
        value_usd="1000",
    )
    expect(bad["decision"] == "DENY" and bad["reason_code"] == "non_participant", f"bad {bad}")

    # 3) seal tampered → DENY
    cert = kp.issue_certificate(
        exporting_country="ZA",
        importing_country="BE",
        carat="100.5",
        value_usd="500000",
    )
    kp.break_seal(cert["certificate_id"])
    r3 = kp.export_rough(
        certificate_id=cert["certificate_id"],
        exporting_country="ZA",
        importing_country="BE",
        carat="100.5",
        value_usd="500000",
    )
    expect(r3["reason_code"] == "seal_tampered", f"r3 {r3}")

    # 4) shipment mismatch → DENY
    cert2 = kp.issue_certificate(
        exporting_country="BW",
        importing_country="IN",
        carat="50",
        value_usd="200000",
    )
    r4 = kp.export_rough(
        certificate_id=cert2["certificate_id"],
        exporting_country="BW",
        importing_country="IN",
        carat="99",
        value_usd="200000",
    )
    expect(r4["reason_code"] == "shipment_mismatch", f"r4 {r4}")

    # 5) revoked → DENY
    cert3 = kp.issue_certificate(
        exporting_country="CA",
        importing_country="US",
        carat="12",
        value_usd="80000",
    )
    kp.revoke_certificate(cert3["certificate_id"])
    r5 = kp.export_rough(
        certificate_id=cert3["certificate_id"],
        exporting_country="CA",
        importing_country="US",
        carat="12",
        value_usd="80000",
    )
    expect(r5["reason_code"] == "certificate_revoked", f"r5 {r5}")

    # 6) clean → ALLOW
    cert4 = kp.issue_certificate(
        exporting_country="ZA",
        importing_country="BE",
        carat="77.7",
        value_usd="333000",
    )
    r6 = kp.export_rough(
        certificate_id=cert4["certificate_id"],
        exporting_country="ZA",
        importing_country="BE",
        carat="77.7",
        value_usd="333000",
    )
    expect(r6["decision"] == "ALLOW" and r6["reason_code"] == "kp_export_authenticated", f"r6 {r6}")
    expect(r6["result"]["real_kp"] is False, "r6 lab")
    expect(kp.get_receipt(r6["receipt_id"]) is not None, "r6 store")

    with stranger_verify() as srv:
        http_deny = stranger_fetch(srv.base_url, r1["receipt_url"])
        expect(http_deny["reason_code"] == "no_certificate", "http no cert")
        http_ok = stranger_fetch(srv.base_url, r6["receipt_url"])
        expect(http_ok["reason_code"] == "kp_export_authenticated", "http ok")

    assert_all_receipts_lab(kp)

    print("KP_EXPORT_PROVE_OK")
    print(
        {
            "denies": [
                r1["reason_code"],
                bad["reason_code"],
                r3["reason_code"],
                r4["reason_code"],
                r5["reason_code"],
            ],
            "export_receipt": r6["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
