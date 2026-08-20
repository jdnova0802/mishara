"""Immunological Weld — Sloterdijk: the weld is a sphere against skip-clear air.

Spheres / immunology: life requires protected interior atmospheres.
Gate's weld is immunological — licensed interior where clear-before-wire
is breathable air; outside is skip-clear weather. Opening the sphere
without CHARGE is autoimmune collapse. Copycats sell open dashboards
as if exposure were safety.

Gatekeep only to ourselves: Sloterdijk spheres → weld as immune membrane.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-immunological-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sphere(
    *,
    welded: bool | None = None,
    their_production: bool | None = None,
    exclusive_door: bool | None = None,
) -> dict[str, Any]:
    weld = bool(welded)
    prod = bool(their_production)
    door = bool(exclusive_door)
    if prod and not weld:
        posture = "autoimmune"
        claim = "production_air_without_weld_membrane"
    elif weld and door:
        posture = "immunized"
        claim = "licensed_interior_breathable_under_mouth"
    elif weld and not door:
        posture = "membrane_without_mouth"
        claim = "weld_present_bypass_weather_still_enters"
    else:
        posture = "demo_exterior"
        claim = "honest_outside_sphere_until_weld"
    return {
        "spec": SPEC,
        "name": "Immunological Weld",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Peter Sloterdijk — Spheres / immunological philosophy",
            "Gate skin + costly signal — weld as membrane, not branding",
        ],
        "welded": weld,
        "production_claimed": prod,
        "exclusive_door": door,
        "posture": posture,
        "claim": claim,
        "thesis": "Production without a weld is autoimmune. The membrane is the product.",
        "gatekeep": "Proprietary Sloterdijk framing of the weld. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Immunological Weld",
        "inventor": INVENTOR,
        "example_immunized": sphere(welded=True, exclusive_door=True, their_production=True),
        "example_autoimmune": sphere(welded=False, their_production=True),
        "live": f"{base}/.well-known/immunological.json",
        "skin": f"{base}/.well-known/skin.json",
        "their_production": False,
    }
