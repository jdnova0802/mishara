"""PAL CHARGE — two-key / Permissive Action Link pattern for LIVE.

Nuclear NC2: never one operator with both ability and authority.
CHARGE is the second key. Soft-yes is not a PAL.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-pal-charge-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def arm(
    *,
    ability_present: bool | None = None,
    authority_charge: bool | None = None,
    same_identity: bool | None = None,
) -> dict[str, Any]:
    ability = bool(ability_present)
    auth = bool(authority_charge)
    same = bool(same_identity)
    if ability and auth and same:
        posture = "pal_violation"
        claim = "split_identities_required"
        armed = False
    elif ability and auth and not same:
        posture = "pal_armed"
        claim = "two_key_live"
        armed = True
    elif ability and not auth:
        posture = "ability_without_authority"
        claim = "dead_until_charge"
        armed = False
    else:
        posture = "unarmed"
        claim = "no_execute"
        armed = False
    return {
        "spec": SPEC,
        "name": "PAL CHARGE",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Permissive Action Link / two-person rule",
            "Feaver always/never NC2 property",
            "Gate CHARGE-only resurrection",
        ],
        "ability_present": ability,
        "authority_charge": auth,
        "same_identity": same,
        "posture": posture,
        "claim": claim,
        "armed": armed,
        "thesis": "Ability ≠ authority. CHARGE is the second key.",
        "gatekeep": "Proprietary PAL CHARGE. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "PAL CHARGE",
        "inventor": INVENTOR,
        "example_violation": arm(ability_present=True, authority_charge=True, same_identity=True),
        "example_armed": arm(ability_present=True, authority_charge=True, same_identity=False),
        "live": f"{base}/.well-known/pal-charge.json",
        "hardest": f"{base}/.well-known/hardest.json",
        "their_production": False,
    }
