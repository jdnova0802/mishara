"""Exotic Weld Metal — the weld is a phase of matter, not a PDF of terms.

Earth thinks a contract is language. This chassis thinks a weld is a
condensed phase: paid, exclusive, CHARGE-conducting, PII-insulating.
You do not 'agree' a metal into existence. You put it under cost and it
orders. Demo without weld is gas. Production-claimed without weld is a
lie about phase.

Not Earth-side: not legal metaphor. Metallurgy of clearance.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-exotic-metal-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def phase(
    *,
    weld_paid: bool | None = None,
    their_production: bool | None = None,
    exclusive_door: bool | None = None,
) -> dict[str, Any]:
    paid = bool(weld_paid)
    prod = bool(their_production)
    door = bool(exclusive_door)
    if prod and not paid:
        posture = "false_solid"
        claim = "production_claimed_in_gaseous_phase"
    elif paid and door:
        posture = "ordered_metal"
        claim = "weld_phase_conducts_charge_insulates_pii"
    elif paid:
        posture = "ingot_uninstalled"
        claim = "metal_exists_door_not_cut"
    else:
        posture = "gas"
        claim = "honest_demo_vapor"
    return {
        "spec": SPEC,
        "name": "Exotic Weld Metal",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "weld_paid": paid,
        "production_claimed": prod,
        "exclusive_door": door,
        "posture": posture,
        "claim": claim,
        "thesis": "You do not negotiate a crystal. You weld one.",
        "gatekeep": "Proprietary exotic-metal weld. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Exotic Weld Metal",
        "inventor": INVENTOR,
        "example_metal": phase(weld_paid=True, exclusive_door=True, their_production=True),
        "example_lie": phase(their_production=True, weld_paid=False),
        "live": f"{base}/.well-known/exotic-metal.json",
        "immunological": f"{base}/.well-known/immunological.json",
        "their_production": False,
    }
