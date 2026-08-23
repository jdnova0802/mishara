"""Receipt Mirror — public /.well-known receipt + private carrier mirror.

Invention (NORTH_STAR applicable-now): stranger vs club — prove without leaking PII.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-receipt-mirror-v1"
INVENTION = "Receipt Mirror"
FAMILY = "applicable_now"


def mirror(
    *,
    event_id: str | None = None,
    job_id: str | None = None,
    decision: str | None = None,
    acted: bool | None = None,
    verify_url: str | None = None,
    receipt_hash: str | None = None,
    public_url: str = "",
    carrier_ref: str | None = None,
) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    eid = (event_id or "").strip() or None
    public = {
        "event_id": eid,
        "decision": (decision or "").upper() or None,
        "acted": bool(acted) if acted is not None else None,
        "verify_url": verify_url,
        "receipt_hash": receipt_hash,
        "job_id_present": bool(job_id),
        # Never put PII / named insured / premium on public face
        "pii": False,
    }
    if eid and base:
        public["well_known"] = f"{base}/.well-known/receipt/{eid}.json"
        public["page"] = f"{base}/inhabitant/{eid}" if False else f"{base}/.well-known/receipt/{eid}.json"
    private = {
        "carrier_ref": carrier_ref,
        "job_id": job_id,
        "event_id": eid,
        "club_only": True,
        "note": "Carrier mirror may hold internal refs — never required for stranger prove.",
    }
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "public": public,
        "private": private,
        "split": True,
        "rule": "Stranger gets receipt + verify_url. Club gets carrier mirror. No PII on public face.",
        "pairs_with": "Hop Tattoo · Receipt Stone · Inhabitant letter",
    }


def attach(plan: dict, *, public_url: str = "") -> dict:
    plan["receipt_mirror"] = mirror(
        event_id=plan.get("event_id"),
        job_id=plan.get("job_id"),
        decision=plan.get("decision"),
        acted=plan.get("acted"),
        verify_url=plan.get("verify_url"),
        receipt_hash=(plan.get("receipt") or {}).get("receipt_hash")
        if isinstance(plan.get("receipt"), dict)
        else plan.get("receipt_hash"),
        public_url=public_url,
        carrier_ref=plan.get("carrier_ref"),
    )
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Public /.well-known receipt + private carrier mirror — stranger vs club.",
        "receipt_template": f"{base}/.well-known/receipt/{{event_id}}.json",
        "demo": f"POST {base}/demo/pas/receipt-mirror",
        "well_known": f"{base}/.well-known/receipt-mirror.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Compliance seed — prove without PII.",
    }
