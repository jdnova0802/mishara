"""Null Door — only causal paths through the exclusive door. Spacelike skip-clear is illegal.

On this chassis, the exclusive door is a null surface: you meet the mouth
in causal sequence (hop → decode → HALT|CHARGE). Skip-clear is spacelike —
an attempt to bind without being on the generators of the door. Integrations
that 'go around' are causality violations, not architecture.

Not Earth-side: no org-chart shortcuts as legitimate paths.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-null-door-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def geodesic(
    *,
    via_exclusive_door: bool | None = None,
    spacelike_skip: bool | None = None,
) -> dict[str, Any]:
    door = bool(via_exclusive_door)
    skip = bool(spacelike_skip)
    if skip:
        posture = "spacelike_illegal"
        claim = "skip_clear_is_not_on_the_generators"
    elif door:
        posture = "null_geodesic"
        claim = "hop_meets_mouth_causally"
    else:
        posture = "no_surface"
        claim = "without_door_there_is_no_causal_mouth"
    return {
        "spec": SPEC,
        "name": "Null Door",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "via_exclusive_door": door,
        "spacelike_skip": skip,
        "posture": posture,
        "claim": claim,
        "thesis": "If it is not on the door's null generators, it is not a path. It is a violation.",
        "gatekeep": "Proprietary null-door causal law. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Null Door",
        "inventor": INVENTOR,
        "example_ok": geodesic(via_exclusive_door=True),
        "example_skip": geodesic(spacelike_skip=True),
        "live": f"{base}/.well-known/null-door.json",
        "nonorientable": f"{base}/.well-known/nonorientable.json",
        "their_production": False,
    }
