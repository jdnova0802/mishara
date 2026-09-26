"""Z8 Geneva Freeport Ingress — lab mouth: CoA/ALR ≠ licit freeport accept.

Lab only. their_production is always False.
Not an art CRM. Not provenance chatbot.
Gates freeport ingress on LIVE provenance logos (chain + permits + beneficiary).
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag
from gate.sims.logos import canonical


SPEC = "nisaba-freeport-ingress-lab-v1"
THEIR_PRODUCTION = False


@dataclass
class ProvenanceBundle:
    bundle_id: str
    object_id: str
    chain_complete: bool
    export_permit: bool
    import_permit: bool
    beneficiary_id: str | None
    alr_clear: bool
    coa_present: bool
    antiquity: bool


@dataclass
class Store:
    bundles: dict[str, ProvenanceBundle] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    custody: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.bundles.clear()
    STORE.receipts.clear()
    STORE.custody.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    object_id: str | None = None,
    bundle_id: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",
        "decision": decision,
        "reason_code": reason_code,
        "object_id": object_id,
        "bundle_id": bundle_id,
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="freeport_ingress"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/freeport/receipts/{rid}"}


def plant_provenance(
    *,
    object_id: str,
    chain_complete: bool = True,
    export_permit: bool = True,
    import_permit: bool = True,
    beneficiary_id: str | None = "BEN-1",
    alr_clear: bool = True,
    coa_present: bool = True,
    antiquity: bool = False,
) -> dict[str, Any]:
    bid = str(uuid.uuid4())
    STORE.bundles[bid] = ProvenanceBundle(
        bundle_id=bid,
        object_id=object_id,
        chain_complete=chain_complete,
        export_permit=export_permit,
        import_permit=import_permit,
        beneficiary_id=beneficiary_id,
        alr_clear=alr_clear,
        coa_present=coa_present,
        antiquity=antiquity,
    )
    return {
        "bundle_id": bid,
        "object_id": object_id,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="freeport_ingress"),
    }


def admit_object(
    *,
    object_id: str,
    bundle_id: str | None = None,
    coa_only: bool = False,
    alr_only: bool = False,
) -> dict[str, Any]:
    """Mouth: freeport ingress DENY without LIVE provenance logos.

    CoA alone or ALR clear alone is insufficient — especially for antiquities.
    """
    if coa_only or alr_only:
        return _receipt(
            "DENY",
            "coa_or_alr_insufficient",
            object_id=object_id,
            result={
                "coa_only": coa_only,
                "alr_only": alr_only,
                "coa_is_not_clean_title": True,
                "alr_is_not_licit_origin": True,
            },
        )

    if not bundle_id:
        return _receipt(
            "DENY",
            "no_provenance_bundle",
            object_id=object_id,
            result={"private_collection_claim_insufficient": True},
        )

    b = STORE.bundles.get(bundle_id)
    if b is None:
        return _receipt(
            "DENY",
            "no_provenance_bundle",
            object_id=object_id,
            bundle_id=bundle_id,
        )

    if b.object_id != object_id:
        return _receipt(
            "DENY",
            "object_mismatch",
            object_id=object_id,
            bundle_id=bundle_id,
        )

    if not b.chain_complete:
        return _receipt(
            "DENY",
            "chain_incomplete",
            object_id=object_id,
            bundle_id=bundle_id,
            result={"need_ownership_chain": True},
        )

    if not b.beneficiary_id:
        return _receipt(
            "DENY",
            "beneficiary_unknown",
            object_id=object_id,
            bundle_id=bundle_id,
            result={"final_beneficiary_required": True},
        )

    if b.antiquity and (not b.export_permit or not b.import_permit):
        return _receipt(
            "DENY",
            "antiquity_permits_missing",
            object_id=object_id,
            bundle_id=bundle_id,
            result={"export_permit": b.export_permit, "import_permit": b.import_permit},
        )

    if not b.export_permit:
        return _receipt(
            "DENY",
            "export_permit_missing",
            object_id=object_id,
            bundle_id=bundle_id,
        )

    if not b.alr_clear:
        return _receipt(
            "DENY",
            "alr_hit",
            object_id=object_id,
            bundle_id=bundle_id,
            result={"stolen_or_disputed": True},
        )

    # CoA helpful but never sufficient alone (already gated); still note presence
    cid = str(uuid.uuid4())
    stub = {
        "custody_id": cid,
        "object_id": object_id,
        "bundle_id": bundle_id,
        "beneficiary_id": b.beneficiary_id,
        "coa_present": b.coa_present,
        "alr_clear": b.alr_clear,
        "freeport": "lab_geneva_fixture",
        "real_freeport": False,
        "fixture": True,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="freeport_ingress"),
    }
    STORE.custody[cid] = stub
    return _receipt(
        "ALLOW",
        "freeport_admitted",
        object_id=object_id,
        bundle_id=bundle_id,
        result=stub,
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/freeport/receipts/{receipt_id}"}
