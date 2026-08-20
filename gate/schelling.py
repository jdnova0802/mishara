"""Schelling Default — focal clear-before-wire + credible commitment.

Schelling: parties coordinate on a salient focal point without communication.
Credible commitment: burn bridges so the threat/promise is believable.

Gate: clear-before-wire is the Schelling default for irreversible spend.
The weld burns the bypass bridge — exclusive door makes the commitment
credible. Without the weld, the mouth is a museum; with it, the focal point holds.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-schelling-v1"
INVENTOR = "Nisaba LLC / Gate"

FOCAL = "clear-before-wire"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def coordinate(
    *,
    exclusive_door: bool | None = None,
    welded: bool | None = None,
    their_production: bool = False,
) -> dict[str, Any]:
    door = bool(exclusive_door) if exclusive_door is not None else False
    weld = bool(welded) if welded is not None else False
    if weld and door:
        posture = "credible_focal"
        claim = "weld_burns_bypass_clear_before_wire_is_schelling_default"
    elif door and not weld:
        posture = "salient_but_not_credible"
        claim = "door_named_but_bypass_still_cheap"
    elif weld and not door:
        posture = "costly_without_exclusivity"
        claim = "weld_without_exclusive_door_is_partial_commitment"
    else:
        posture = "museum"
        claim = "receipt_without_door_or_weld_is_non_event"

    return {
        "spec": SPEC,
        "name": "Schelling Default",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Thomas Schelling — focal points; Strategy of Conflict",
            "Credible commitment — limit own options to make promise/threat believable",
            "Gate exclusive timing — bypass must cost more than going through the door",
        ],
        "focal_point": FOCAL,
        "exclusive_door": door,
        "welded": weld,
        "posture": posture,
        "claim": claim,
        "their_production": their_production,
        "thesis": "Clear-before-wire wins coordination when the weld makes it the only salient door.",
        "gatekeep": "Proprietary Schelling framing of the mouth default. Ours.",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Schelling Default",
        "inventor": INVENTOR,
        "example_credible": coordinate(exclusive_door=True, welded=True),
        "example_museum": coordinate(exclusive_door=False, welded=False),
        "live": f"{base}/.well-known/schelling.json",
        "exclusive_timing": f"{base}/.well-known/exclusive-timing.json",
        "operator": f"{base}/.well-known/operator.json",
        "their_production": False,
    }
