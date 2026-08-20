"""Invented Accident — Virilio: the PAS invents skip-clear; the mouth is the invented brake.

Paul Virilio: the invention of the ship is the invention of the shipwreck.
Inventing cheap bind automation invents skip-clear at volume (Jevons).
Gate is the invented accident-brake: not after-the-fact insurance theater,
a mouth contemporaneous with the hop. Copycats sell ships without wrecks.

Gatekeep only to ourselves: Virilio accident → mouth invented with the PAS.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-invented-accident-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def contemporaneous(
    *,
    pas_automation: bool | None = None,
    mouth_on_path: bool | None = None,
) -> dict[str, Any]:
    pas = bool(pas_automation)
    mouth = bool(mouth_on_path)
    if pas and not mouth:
        posture = "ship_without_brake"
        claim = "invented_bind_invented_skip_clear_unbraked"
    elif pas and mouth:
        posture = "accident_invented_with_brake"
        claim = "mouth_contemporaneous_with_the_hop"
    else:
        posture = "no_ship"
        claim = "no_pas_automation_assay"
    return {
        "spec": SPEC,
        "name": "Invented Accident",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Paul Virilio — the invention of the ship is the invention of the wreck",
            "Gate Jevons + technique limit — automation rebound needs a mouth now",
        ],
        "pas_automation": pas,
        "mouth_on_path": mouth,
        "posture": posture,
        "claim": claim,
        "thesis": "You do not add a mouth later. The wreck is invented with the bind API.",
        "gatekeep": "Proprietary Virilio accident doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Invented Accident",
        "inventor": INVENTOR,
        "example_brake": contemporaneous(pas_automation=True, mouth_on_path=True),
        "example_wreck": contemporaneous(pas_automation=True, mouth_on_path=False),
        "live": f"{base}/.well-known/invented-accident.json",
        "jevons": f"{base}/.well-known/jevons.json",
        "their_production": False,
    }
