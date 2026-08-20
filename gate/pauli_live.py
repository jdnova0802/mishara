"""Pauli LIVE — two irreversible acts cannot occupy the same LIVE orbital.

A CHARGE-won LIVE is fermionic in this chassis: one occupied orbital per
married write. You cannot put two binds in the same LIVE seat by cloning
a flag. The next hop needs a new orbital (new mouth passage). Occupancy
violation is how Earth systems double-spend permission.

Not Earth-side: not 'idempotency best practice'. Exclusion principle.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-pauli-live-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def occupy(
    *,
    same_live_cloned: bool | None = None,
    distinct_mouth_passage: bool | None = None,
) -> dict[str, Any]:
    clone = bool(same_live_cloned)
    distinct = bool(distinct_mouth_passage)
    if clone and not distinct:
        posture = "exclusion_violation"
        claim = "two_acts_in_one_live_orbital"
    elif distinct:
        posture = "fermi_ok"
        claim = "new_hop_new_orbital"
    else:
        posture = "vacuum_orbital"
        claim = "unoccupied"
    return {
        "spec": SPEC,
        "name": "Pauli LIVE",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "same_live_cloned": clone,
        "distinct_mouth_passage": distinct,
        "posture": posture,
        "claim": claim,
        "thesis": "LIVE is occupied or empty. It is not a bus you share.",
        "gatekeep": "Proprietary Pauli-LIVE exclusion. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Pauli LIVE",
        "inventor": INVENTOR,
        "example_ok": occupy(distinct_mouth_passage=True),
        "example_bad": occupy(same_live_cloned=True),
        "live": f"{base}/.well-known/pauli-live.json",
        "linear_live": f"{base}/.well-known/linear-live.json",
        "their_production": False,
    }
