"""S6 Deed Record Gate — lab mouth: instrument ≠ recorded title.

Lab only. their_production is always False.
Not title insurance / post-hoc alerts — this gates RECORD accept.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


SPEC = "nisaba-deed-record-gate-lab-v1"
THEIR_PRODUCTION = False


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def instrument_hash(instrument: dict[str, Any]) -> str:
    body = {
        "parcel_id": instrument.get("parcel_id"),
        "grantor": instrument.get("grantor"),
        "grantee": instrument.get("grantee"),
        "doc_hash": instrument.get("doc_hash"),
    }
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


@dataclass
class Instrument:
    instrument_id: str
    parcel_id: str
    grantor: str
    grantee: str
    doc_hash: str
    content_hash: str


@dataclass
class ParcelPolicy:
    parcel_id: str
    owner_lock: bool
    require_notary: bool


@dataclass
class Store:
    instruments: dict[str, Instrument] = field(default_factory=dict)
    parcels: dict[str, ParcelPolicy] = field(default_factory=dict)
    unlock_grants: dict[str, str] = field(default_factory=dict)  # parcel_id -> grant_id
    live_notary_seals: set[str] = field(default_factory=set)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    records: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.instruments.clear()
    STORE.parcels.clear()
    STORE.unlock_grants.clear()
    STORE.live_notary_seals.clear()
    STORE.receipts.clear()
    STORE.records.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    instrument_id: str | None = None,
    parcel_id: str | None = None,
    doc_hash: str | None = None,
    content_hash: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "decision": decision,
        "reason_code": reason_code,
        "instrument_id": instrument_id,
        "parcel_id": parcel_id,
        "doc_hash": doc_hash,
        "content_hash": content_hash,
        "result": result,
        "their_production": THEIR_PRODUCTION,
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/deed-record/receipts/{rid}"}


def set_parcel_policy(parcel_id: str, *, owner_lock: bool = False, require_notary: bool = False) -> None:
    STORE.parcels[parcel_id] = ParcelPolicy(
        parcel_id=parcel_id,
        owner_lock=owner_lock,
        require_notary=require_notary,
    )


def issue_unlock_grant(parcel_id: str) -> str:
    gid = str(uuid.uuid4())
    STORE.unlock_grants[parcel_id] = gid
    return gid


def register_notary_seal(seal_id: str) -> None:
    STORE.live_notary_seals.add(seal_id)


def create_instrument(
    *,
    parcel_id: str,
    grantor: str,
    grantee: str,
    doc_hash: str,
) -> dict[str, Any]:
    if not parcel_id or not grantor or not grantee or not doc_hash:
        return {
            "ok": False,
            "reason_code": "malformed_instrument",
            "their_production": THEIR_PRODUCTION,
        }
    iid = str(uuid.uuid4())
    body = {
        "parcel_id": parcel_id,
        "grantor": grantor,
        "grantee": grantee,
        "doc_hash": doc_hash,
    }
    ch = instrument_hash(body)
    STORE.instruments[iid] = Instrument(
        instrument_id=iid,
        parcel_id=parcel_id,
        grantor=grantor,
        grantee=grantee,
        doc_hash=doc_hash,
        content_hash=ch,
    )
    return {
        "instrument_id": iid,
        "content_hash": ch,
        "parcel_id": parcel_id,
        "their_production": THEIR_PRODUCTION,
    }


def record_instrument(
    instrument_id: str,
    *,
    id_assurance: str,
    unlock_grant: str | None = None,
    notary_seal_id: str | None = None,
) -> dict[str, Any]:
    inst = STORE.instruments.get(instrument_id)
    if inst is None:
        return _receipt("DENY", "no_instrument", instrument_id=instrument_id)

    if id_assurance in ("", "unknown") or id_assurance is None:
        return _receipt(
            "DENY",
            "id_assurance_unknown",
            instrument_id=instrument_id,
            parcel_id=inst.parcel_id,
            doc_hash=inst.doc_hash,
            content_hash=inst.content_hash,
        )
    if id_assurance == "inject_suspect":
        return _receipt(
            "DENY",
            "id_assurance_inject_suspect",
            instrument_id=instrument_id,
            parcel_id=inst.parcel_id,
            doc_hash=inst.doc_hash,
            content_hash=inst.content_hash,
        )
    if id_assurance != "live":
        return _receipt(
            "DENY",
            "id_assurance_not_live",
            instrument_id=instrument_id,
            parcel_id=inst.parcel_id,
            doc_hash=inst.doc_hash,
            content_hash=inst.content_hash,
        )

    policy = STORE.parcels.get(inst.parcel_id)
    if policy is None:
        # uncertainty about parcel policy → DENY
        return _receipt(
            "DENY",
            "parcel_policy_unknown",
            instrument_id=instrument_id,
            parcel_id=inst.parcel_id,
            doc_hash=inst.doc_hash,
            content_hash=inst.content_hash,
        )

    if policy.owner_lock:
        expected = STORE.unlock_grants.get(inst.parcel_id)
        if not unlock_grant or unlock_grant != expected:
            return _receipt(
                "DENY",
                "owner_lock_no_unlock",
                instrument_id=instrument_id,
                parcel_id=inst.parcel_id,
                doc_hash=inst.doc_hash,
                content_hash=inst.content_hash,
            )

    if policy.require_notary:
        if not notary_seal_id or notary_seal_id not in STORE.live_notary_seals:
            return _receipt(
                "DENY",
                "notary_seal_missing_or_revoked",
                instrument_id=instrument_id,
                parcel_id=inst.parcel_id,
                doc_hash=inst.doc_hash,
                content_hash=inst.content_hash,
            )

    rid = str(uuid.uuid4())
    record = {
        "record_id": rid,
        "instrument_id": instrument_id,
        "parcel_id": inst.parcel_id,
        "doc_hash": inst.doc_hash,
        "content_hash": inst.content_hash,
        "logos_epoch": "LIVE",
        "county_sim": f"SIM-RECORDER-{rid[:8]}",
        "their_production": THEIR_PRODUCTION,
    }
    STORE.records[rid] = record
    return _receipt(
        "ALLOW",
        "recorded",
        instrument_id=instrument_id,
        parcel_id=inst.parcel_id,
        doc_hash=inst.doc_hash,
        content_hash=inst.content_hash,
        result=record,
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/deed-record/receipts/{receipt_id}"}
