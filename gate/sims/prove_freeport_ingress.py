#!/usr/bin/env python3
"""Prove Z8 Freeport Ingress — CoA/ALR ≠ licit accept. Lab only."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gate.sims import freeport_ingress as fp  # noqa: E402
from gate.sims.lab_invariant import assert_all_receipts_lab  # noqa: E402
from gate.sims.verify_http import stranger_fetch, stranger_verify  # noqa: E402


def expect(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def main() -> None:
    fp.reset()

    # 1) CoA-only → DENY
    r1 = fp.admit_object(object_id="OBJ-1", coa_only=True)
    expect(r1["decision"] == "DENY" and r1["reason_code"] == "coa_or_alr_insufficient", f"r1 {r1}")
    expect(r1["result"]["coa_is_not_clean_title"] is True, "r1 coa")
    expect(r1["receipt_class"] == "clearance", "r1 class")

    # 2) ALR-only → DENY
    r2 = fp.admit_object(object_id="OBJ-2", alr_only=True)
    expect(r2["reason_code"] == "coa_or_alr_insufficient", f"r2 {r2}")
    expect(r2["result"]["alr_is_not_licit_origin"] is True, "r2 alr")

    # 3) no bundle → DENY
    r3 = fp.admit_object(object_id="OBJ-3")
    expect(r3["reason_code"] == "no_provenance_bundle", f"r3 {r3}")

    # 4) incomplete chain → DENY
    b4 = fp.plant_provenance(object_id="OBJ-4", chain_complete=False)
    r4 = fp.admit_object(object_id="OBJ-4", bundle_id=b4["bundle_id"])
    expect(r4["reason_code"] == "chain_incomplete", f"r4 {r4}")

    # 5) antiquity without permits → DENY
    b5 = fp.plant_provenance(
        object_id="OBJ-5",
        antiquity=True,
        export_permit=False,
        import_permit=False,
    )
    r5 = fp.admit_object(object_id="OBJ-5", bundle_id=b5["bundle_id"])
    expect(r5["reason_code"] == "antiquity_permits_missing", f"r5 {r5}")

    # 6) ALR hit → DENY
    b6 = fp.plant_provenance(object_id="OBJ-6", alr_clear=False)
    r6 = fp.admit_object(object_id="OBJ-6", bundle_id=b6["bundle_id"])
    expect(r6["reason_code"] == "alr_hit", f"r6 {r6}")

    # 7) beneficiary unknown → DENY
    b7 = fp.plant_provenance(object_id="OBJ-7", beneficiary_id=None)
    r7 = fp.admit_object(object_id="OBJ-7", bundle_id=b7["bundle_id"])
    expect(r7["reason_code"] == "beneficiary_unknown", f"r7 {r7}")

    # 8) clean provenance → ALLOW
    b8 = fp.plant_provenance(object_id="OBJ-8", antiquity=False)
    r8 = fp.admit_object(object_id="OBJ-8", bundle_id=b8["bundle_id"])
    expect(r8["decision"] == "ALLOW" and r8["reason_code"] == "freeport_admitted", f"r8 {r8}")
    expect(r8["result"]["real_freeport"] is False, "r8 lab")
    expect(fp.get_receipt(r8["receipt_id"]) is not None, "r8 store")

    with stranger_verify() as srv:
        http_deny = stranger_fetch(srv.base_url, r1["receipt_url"])
        expect(http_deny["reason_code"] == "coa_or_alr_insufficient", "http coa deny")
        http_ok = stranger_fetch(srv.base_url, r8["receipt_url"])
        expect(http_ok["reason_code"] == "freeport_admitted", "http admit")

    assert_all_receipts_lab(fp)

    print("FREEPORT_INGRESS_PROVE_OK")
    print(
        {
            "denies": [
                r1["reason_code"],
                r2["reason_code"],
                r3["reason_code"],
                r4["reason_code"],
                r5["reason_code"],
                r6["reason_code"],
                r7["reason_code"],
            ],
            "admit_receipt": r8["receipt_id"],
            "stranger_http_verify": True,
            "their_production": False,
        }
    )


if __name__ == "__main__":
    main()
