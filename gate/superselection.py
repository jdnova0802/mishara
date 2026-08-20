"""Superselection LIVE — DEAD and LIVE cannot be superposed. Partial-LIVE is illegal.

In the chassis Hilbert space (metaphor as hardware law, not quantum woo):
DEAD and LIVE sit in superselection sectors. You cannot hold a coherent
mixture 'mostly live pending committee'. Admin sliders are forbidden
interference terms. CHARGE is the only allowed sector change.

Not Earth-side: no percentages of LIVE.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-superselection-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sector(
    *,
    partial_live: bool | None = None,
    charge_id: str | None = None,
    status: str | None = None,
) -> dict[str, Any]:
    partial = bool(partial_live)
    charge = bool((charge_id or "").strip())
    s = (status or "").strip().upper()
    if partial or s in ("MOSTLY_LIVE", "DEGRADED_LIVE", "PERCENT_LIVE"):
        posture = "superselection_violation"
        claim = "no_coherent_dead_plus_live"
    elif charge and s in ("LIVE", "CHARGE", "ALLOW"):
        posture = "sector_changed"
        claim = "charge_is_the_only_allowed_jump"
    elif s in ("DEAD", "HALT", "BLOCK", ""):
        posture = "sector_dead"
        claim = "no_mixture"
    else:
        posture = "unevaluated"
        claim = "unknown_sector_label"
    return {
        "spec": SPEC,
        "name": "Superselection LIVE",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "partial_live": partial,
        "charge_present": charge,
        "status": s or None,
        "posture": posture,
        "claim": claim,
        "thesis": "There is no superposition of DEAD and LIVE. Sliders are not a sector.",
        "gatekeep": "Proprietary superselection law. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    d = str(row.get("decision") or "").upper()
    status = "LIVE" if d == "ALLOW" and row.get("acted") else d
    out["superselection"] = sector(status=status, charge_id=row.get("charge_id"))
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Superselection LIVE",
        "inventor": INVENTOR,
        "example_violation": sector(partial_live=True),
        "example_jump": sector(charge_id="chg_1", status="LIVE"),
        "live": f"{base}/.well-known/superselection.json",
        "firmware_fuse": f"{base}/.well-known/firmware-fuse.json",
        "their_production": False,
    }
