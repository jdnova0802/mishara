"""Cosmotechnics of Clearance — Yuk Hui: this is not generic 'tech'; it is a local cosmotechnics.

Yuk Hui: technics is always cosmotechnics — a unification of moral order
and cosmic order through technical activity. Gate is not 'AI governance
software'. It is a cosmotechnics of irreversible spend: CHARGE, weld,
licensed interior, published nos. Copycats ship generic tech and hope
morals arrive later.

Gatekeep only to ourselves: cosmotechnics → clearance as situated moral-technical order.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-cosmotechnics-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def situate(
    *,
    generic_ai_governance: bool | None = None,
    licensed_weld: bool | None = None,
    charge_only_live: bool | None = None,
) -> dict[str, Any]:
    generic = bool(generic_ai_governance)
    weld = bool(licensed_weld)
    charge = True if charge_only_live is None else bool(charge_only_live)
    if generic:
        posture = "generic_tech"
        claim = "morals_deferred_is_not_cosmotechnics"
    elif weld and charge:
        posture = "situated_cosmotechnics"
        claim = "clearance_unifies_moral_order_and_weld_physics"
    else:
        posture = "incomplete_situation"
        claim = "missing_weld_or_charge_order"
    return {
        "spec": SPEC,
        "name": "Cosmotechnics of Clearance",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Yuk Hui — The Question Concerning Technology in China; cosmotechnics",
            "Gate licensed-only + CHARGE-only LIVE — not generic AI policy",
        ],
        "generic_ai_governance": generic,
        "licensed_weld": weld,
        "charge_only_live": charge,
        "posture": posture,
        "claim": claim,
        "thesis": "Generic safety tech is not Gate. Cosmotechnics is local, welded, licensed.",
        "gatekeep": "Proprietary cosmotechnics doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Cosmotechnics of Clearance",
        "inventor": INVENTOR,
        "example_ok": situate(licensed_weld=True, charge_only_live=True),
        "example_generic": situate(generic_ai_governance=True),
        "live": f"{base}/.well-known/cosmotechnics.json",
        "xenohardware": f"{base}/.well-known/xenohardware.json",
        "their_production": False,
    }
