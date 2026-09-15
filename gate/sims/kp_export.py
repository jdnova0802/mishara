"""Z7 Kimberley Process Export — lab mouth: parcel present ≠ KP-certified export.

Lab only. their_production is always False.
Not a diamond CRM. Not De Beers marketplace.
Gates export/import on LIVE KP certificate + seal integrity.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag
from gate.sims.logos import canonical


SPEC = "nisaba-kp-export-lab-v1"
THEIR_PRODUCTION = False

KP_PARTICIPANTS = frozenset({"ZA", "BW", "CA", "BE", "IN", "US", "AE", "AU"})


@dataclass
class Certificate:
    certificate_id: str
    exporting_country: str
    importing_country: str
    carat: str
    value_usd: str
    parcels: int
    seal_intact: bool
    status: str  # issued | authenticated | revoked
    serial: str


@dataclass
class Store:
    certificates: dict[str, Certificate] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    shipments: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.certificates.clear()
    STORE.receipts.clear()
    STORE.shipments.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    certificate_id: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",
        "decision": decision,
        "reason_code": reason_code,
        "certificate_id": certificate_id,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="kp_export"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/kp-export/receipts/{rid}"}


def issue_certificate(
    *,
    exporting_country: str,
    importing_country: str,
    carat: str,
    value_usd: str,
    parcels: int = 1,
) -> dict[str, Any]:
    exp = exporting_country.upper()
    imp = importing_country.upper()
    if exp not in KP_PARTICIPANTS or imp not in KP_PARTICIPANTS:
        return _receipt(
            "DENY",
            "non_participant",
            result={"exporting": exp, "importing": imp},
        )
    cid = str(uuid.uuid4())
    serial = f"{exp}-{cid[:8].upper()}"
    STORE.certificates[cid] = Certificate(
        certificate_id=cid,
        exporting_country=exp,
        importing_country=imp,
        carat=str(carat),
        value_usd=str(value_usd),
        parcels=int(parcels),
        seal_intact=True,
        status="issued",
        serial=serial,
    )
    return {
        "certificate_id": cid,
        "serial": serial,
        "status": "issued",
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="kp_export"),
    }


def break_seal(certificate_id: str) -> None:
    c = STORE.certificates.get(certificate_id)
    if c:
        c.seal_intact = False


def revoke_certificate(certificate_id: str) -> None:
    c = STORE.certificates.get(certificate_id)
    if c:
        c.status = "revoked"


def export_rough(
    *,
    certificate_id: str | None,
    exporting_country: str,
    importing_country: str,
    carat: str,
    value_usd: str,
) -> dict[str, Any]:
    """Mouth: rough export DENY without LIVE KP certificate matching shipment + intact seal."""
    if not certificate_id:
        return _receipt(
            "DENY",
            "no_certificate",
            result={"parcel_present_is_not_certified": True, "kpcs_shaped": True},
        )

    c = STORE.certificates.get(certificate_id)
    if c is None:
        return _receipt(
            "DENY",
            "no_certificate",
            certificate_id=certificate_id,
            result={"unknown_or_forged": True},
        )

    if c.status == "revoked":
        return _receipt("DENY", "certificate_revoked", certificate_id=certificate_id)

    if not c.seal_intact:
        return _receipt(
            "DENY",
            "seal_tampered",
            certificate_id=certificate_id,
            result={"tamper_proof_container_required": True},
        )

    if c.exporting_country != exporting_country.upper():
        return _receipt(
            "DENY",
            "export_country_mismatch",
            certificate_id=certificate_id,
            result={"cert": c.exporting_country, "claimed": exporting_country.upper()},
        )

    if c.importing_country != importing_country.upper():
        return _receipt(
            "DENY",
            "import_country_mismatch",
            certificate_id=certificate_id,
        )

    if c.carat != str(carat) or c.value_usd != str(value_usd):
        return _receipt(
            "DENY",
            "shipment_mismatch",
            certificate_id=certificate_id,
            result={
                "cert_carat": c.carat,
                "cert_value": c.value_usd,
                "claimed_carat": str(carat),
                "claimed_value": str(value_usd),
            },
        )

    sid = str(uuid.uuid4())
    stub = {
        "shipment_id": sid,
        "certificate_id": certificate_id,
        "serial": c.serial,
        "exporting_country": c.exporting_country,
        "importing_country": c.importing_country,
        "carat": c.carat,
        "value_usd": c.value_usd,
        "real_kp": False,
        "fixture": True,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="kp_export"),
    }
    STORE.shipments[sid] = stub
    c.status = "authenticated"
    return _receipt(
        "ALLOW",
        "kp_export_authenticated",
        certificate_id=certificate_id,
        result=stub,
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/kp-export/receipts/{receipt_id}"}
