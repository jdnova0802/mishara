"""Non-Repudiation Ladder — integrity · origin · time · not authorship cosplay.

ISO/IEC 13888-shaped services productized for irreversible-spend evidence:
  - NRO: non-repudiation of origin (mouth decision originated here)
  - NRI: non-repudiation of integrity (receipt hash / chain)
  - NRT: non-repudiation of time (UTC created_at + linked chain)
  - NOT: proof of human authorship or legal signature alone

Hash proves existence/integrity. Signature proves Gate key held the hash.
Neither alone proves a named human intended the spend — Gate is honest.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-nonrepudiation-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ladder(
    *,
    decision: str | None = None,
    event_id: str | None = None,
    receipt_hash: str | None = None,
    receipt_signature: str | None = None,
    prev_receipt_hash: str | None = None,
    created_at: str | None = None,
    verify_url: str | None = None,
) -> dict[str, Any]:
    d = (decision or "").upper()
    has_hash = bool(receipt_hash)
    has_sig = bool(receipt_signature)
    has_time = bool(created_at)
    has_chain = bool(prev_receipt_hash) or (has_hash and bool(event_id))

    rungs = [
        {
            "service": "NRI",
            "name": "integrity",
            "claim": "receipt_bytes_tamper_evident",
            "reached": has_hash,
            "artifact": "receipt_hash",
        },
        {
            "service": "NRO",
            "name": "origin",
            "claim": "decision_originated_at_this_mouth",
            "reached": has_sig or (has_hash and bool(d)),
            "artifact": "receipt_signature | mouth decision fields",
        },
        {
            "service": "NRT",
            "name": "time",
            "claim": "utc_timestamp_bound_to_event",
            "reached": has_time,
            "artifact": "created_at (ISO-8601 UTC)",
        },
        {
            "service": "NRC",
            "name": "chain",
            "claim": "append_only_prev_hash_linkage",
            "reached": has_chain,
            "artifact": "prev_receipt_hash",
        },
    ]
    reached = sum(1 for r in rungs if r["reached"])
    return {
        "spec": SPEC,
        "name": "Non-Repudiation Ladder",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "ISO/IEC 13888 — non-repudiation services (origin, delivery, …)",
            "FRE 901 / 902(13)(14) — authenticity via process + hash (adjacent, not legal advice)",
            "Gate receipts — Ed25519 over hash + stranger verify URL",
        ],
        "rungs": rungs,
        "rungs_reached": reached,
        "decision": d or None,
        "event_id": event_id,
        "verify_url": verify_url,
        "honest_limits": {
            "hash_is_not_authorship": True,
            "signature_is_mouth_key_not_named_human": True,
            "not_legal_advice": True,
        },
        "thesis": "Partners get citeable non-repudiation of mouth acts — without fake human-authorship theater.",
        "gatekeep": "Proprietary NR ladder for irreversible-spend evidence. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: dict, row: dict) -> dict:
    payload["nonrepudiation"] = ladder(
        decision=row.get("decision"),
        event_id=row.get("id"),
        receipt_hash=row.get("receipt_hash"),
        receipt_signature=row.get("receipt_signature"),
        prev_receipt_hash=row.get("prev_receipt_hash"),
        created_at=row.get("created_at"),
        verify_url=row.get("verify_url"),
    )
    return payload


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Non-Repudiation Ladder",
        "inventor": INVENTOR,
        "example": ladder(
            decision="HALT",
            event_id="evt_example",
            receipt_hash="0" * 64,
            receipt_signature="sig_example",
            prev_receipt_hash="1" * 64,
            created_at=_now(),
            verify_url="https://velaru.xyz/verify",
        ),
        "live": f"{base}/.well-known/nonrepudiation.json",
        "receipt": f"{base}/.well-known/receipt/{{event_id}}.json",
        "their_production": False,
    }
