"""Holographic Receipt — the antenna boundary encodes the spent bulk.

Holographic principle: bulk information is encoded on the boundary.
Gate: stranger antenna + receipt hash + restraint leaf encode the hop
without shipping the inhabitant bulk (PII). If the boundary cannot
reconstruct that a no or a CHARGE happened, the holograph is broken.
Copycats keep the bulk in a private warehouse and call it 'source of truth'.

Gatekeep only to ourselves: holography → public boundary is the product evidence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-holographic-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def encode(
    *,
    verify_url: str | None = None,
    receipt_hash: str | None = None,
    pii_in_bulk_only: bool | None = None,
    boundary_fetchable: bool | None = None,
) -> dict[str, Any]:
    url = bool((verify_url or "").strip())
    rh = bool((receipt_hash or "").strip())
    pii_ok = True if pii_in_bulk_only is None else bool(pii_in_bulk_only)
    fetch = True if boundary_fetchable is None else bool(boundary_fetchable)
    if url and rh and pii_ok and fetch:
        posture = "holograph_intact"
        claim = "boundary_encodes_occasion_without_pii_bulk"
    elif not url or not fetch:
        posture = "bulk_without_boundary"
        claim = "private_warehouse_is_not_a_holograph"
    else:
        posture = "thin_boundary"
        claim = "missing_hash_or_pii_leak_on_boundary"
    return {
        "spec": SPEC,
        "name": "Holographic Receipt",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Holographic principle — bulk encoded on the boundary",
            "Gate stranger antenna + galvanic isolation",
        ],
        "verify_present": url,
        "receipt_hash_present": rh,
        "pii_in_bulk_only": pii_ok,
        "boundary_fetchable": fetch,
        "posture": posture,
        "claim": claim,
        "thesis": "If a stranger cannot read the boundary, you did not encode the spend. You hid it.",
        "gatekeep": "Proprietary holographic-receipt doctrine. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["holographic"] = encode(
        verify_url=row.get("verify_url"),
        receipt_hash=row.get("receipt_hash"),
        pii_in_bulk_only=True,
        boundary_fetchable=True,
    )
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Holographic Receipt",
        "inventor": INVENTOR,
        "example_ok": encode(verify_url="https://velaru.xyz/verify", receipt_hash="abc"),
        "example_hidden": encode(verify_url=None, receipt_hash="abc", boundary_fetchable=False),
        "live": f"{base}/.well-known/holographic.json",
        "stranger_antenna": f"{base}/.well-known/stranger-antenna.json",
        "their_production": False,
    }
