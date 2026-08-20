"""Landauer CHARGE — erasing HALT optionality has a minimum cost; badges are below it.

Rolf Landauer: erasing one bit of information has a thermodynamic cost.
Gate: CHARGE erases the HALT-option bit (complementarity). That erasure
must cost — weld, witness, named CHARGE. AI badges and dashboard greens
erase the bit for free, which is physically the cheat. Copycats sell
zero-cost erasure of restraint.

Gatekeep only to ourselves: Landauer's principle → CHARGE as erasure cost of optionality.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-landauer-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def erase(
    *,
    destroying_halt_option: bool | None = None,
    charge_id: str | None = None,
    cheap_badge: bool | None = None,
) -> dict[str, Any]:
    destroy = bool(destroying_halt_option)
    charge = bool((charge_id or "").strip())
    cheap = bool(cheap_badge)
    if destroy and cheap and not charge:
        posture = "below_landauer"
        claim = "free_erasure_of_optionality_is_the_cheat"
    elif destroy and charge:
        posture = "landauer_paid"
        claim = "charge_pays_erasure_cost_of_halt_bit"
    elif not destroy:
        posture = "bit_retained"
        claim = "halt_optionality_not_erased"
    else:
        posture = "unevaluated"
        claim = "insufficient_erasure_data"
    return {
        "spec": SPEC,
        "name": "Landauer CHARGE",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Rolf Landauer — erasure of information has a minimum energy cost",
            "Gate complementarity + costliness — CHARGE destroys HALT option",
        ],
        "destroying_halt_option": destroy,
        "charge_present": charge,
        "cheap_badge": cheap,
        "posture": posture,
        "claim": claim,
        "thesis": "You may not erase HALT for free. CHARGE is the Landauer payment.",
        "gatekeep": "Proprietary Landauer-CHARGE doctrine. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    d = str(row.get("decision") or "").upper()
    acted = bool(row.get("acted"))
    out["landauer"] = erase(
        destroying_halt_option=acted and d == "ALLOW",
        charge_id=row.get("charge_id"),
        cheap_badge=False,
    )
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Landauer CHARGE",
        "inventor": INVENTOR,
        "example_paid": erase(destroying_halt_option=True, charge_id="chg_1"),
        "example_cheat": erase(destroying_halt_option=True, cheap_badge=True),
        "live": f"{base}/.well-known/landauer.json",
        "complementarity": f"{base}/.well-known/complementarity.json",
        "their_production": False,
    }
