"""Custody Chain — chain of custody for mouth evidence.

Digital evidence practice: identification → acquisition hash → transfers →
verification hash. Gate receipts already chain via prev_receipt_hash.

This invention names the custody stages for a hop event so auditors can
cite a FRE-adjacent authenticity *process* — without claiming courtroom
admissibility or human authorship.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-custody-v1"
INVENTOR = "Nisaba LLC / Gate"

STAGES = (
    "identify",
    "acquire",
    "hash",
    "sign",
    "chain",
    "publish",
    "verify",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def trail(
    *,
    event_id: str | None = None,
    receipt_hash: str | None = None,
    receipt_signature: str | None = None,
    prev_receipt_hash: str | None = None,
    created_at: str | None = None,
    verify_url: str | None = None,
    public_receipt_url: str | None = None,
) -> dict[str, Any]:
    steps = [
        {
            "stage": "identify",
            "reached": bool(event_id),
            "artifact": event_id,
            "meaning": "Unique event id assigned at hop",
        },
        {
            "stage": "acquire",
            "reached": bool(created_at),
            "artifact": created_at,
            "meaning": "UTC capture time of decision",
        },
        {
            "stage": "hash",
            "reached": bool(receipt_hash),
            "artifact": receipt_hash,
            "meaning": "SHA-256 of canonical receipt (acquisition hash)",
        },
        {
            "stage": "sign",
            "reached": bool(receipt_signature),
            "artifact": "receipt_signature" if receipt_signature else None,
            "meaning": "Ed25519 over receipt_hash when keys configured",
        },
        {
            "stage": "chain",
            "reached": bool(prev_receipt_hash) or bool(receipt_hash),
            "artifact": prev_receipt_hash,
            "meaning": "Append-only link to prior receipt",
        },
        {
            "stage": "publish",
            "reached": bool(public_receipt_url),
            "artifact": public_receipt_url,
            "meaning": "Well-known receipt URL for stranger fetch",
        },
        {
            "stage": "verify",
            "reached": bool(verify_url),
            "artifact": verify_url,
            "meaning": "External attestor / Velaru verify surface",
        },
    ]
    return {
        "spec": SPEC,
        "name": "Custody Chain",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Digital evidence chain of custody — identify, hash, transfer, verify",
            "FRE 901 process authentication (adjacent framing; not legal advice)",
            "NIST IR 8387 — hash at collection; store hashes securely",
            "Gate receipt chain — prev_receipt_hash + stranger verify",
        ],
        "stages": steps,
        "stages_reached": sum(1 for s in steps if s["reached"]),
        "spoliation_note": (
            "Reinterpreting HALT as ALLOW without CHARGE would break monotonic "
            "custody of the permission regime — epoch lock is anti-spoliation."
        ),
        "not_legal_advice": True,
        "thesis": "Evidence of the no is a custody trail, not a screenshot.",
        "gatekeep": "Proprietary custody-stage naming for mouth evidence. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: dict, row: dict, public_url: str | None = None) -> dict:
    base = (public_url or "").rstrip("/")
    eid = row.get("id")
    pub = f"{base}/.well-known/receipt/{eid}.json" if base and eid else None
    payload["custody"] = trail(
        event_id=eid,
        receipt_hash=row.get("receipt_hash"),
        receipt_signature=row.get("receipt_signature"),
        prev_receipt_hash=row.get("prev_receipt_hash"),
        created_at=row.get("created_at"),
        verify_url=row.get("verify_url"),
        public_receipt_url=pub,
    )
    return payload


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Custody Chain",
        "inventor": INVENTOR,
        "example": trail(
            event_id="evt_example",
            receipt_hash="0" * 64,
            receipt_signature="sig",
            prev_receipt_hash="1" * 64,
            created_at=_now(),
            verify_url="https://velaru.xyz/verify",
            public_receipt_url=f"{base}/.well-known/receipt/evt_example.json",
        ),
        "live": f"{base}/.well-known/custody.json",
        "their_production": False,
    }
