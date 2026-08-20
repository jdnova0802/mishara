"""Non-Orientable Door — Möbius exclusive door: there is no around.

On an orientable surface you can sneak to the other side. A Möbius /
non-orientable door has no backside for skip-clear. The exclusive door
is that topology: every path that looks like 'around' is still the door.
Copycats add side doors and call them integrations.

Gatekeep only to ourselves: topology → exclusive door with no backside.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-nonorientable-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def topology(
    *,
    exclusive_door: bool | None = None,
    side_doors: int | None = None,
) -> dict[str, Any]:
    door = bool(exclusive_door)
    sides = int(side_doors) if side_doors is not None else 0
    if door and sides == 0:
        posture = "nonorientable"
        claim = "no_backside_for_skip_clear"
    elif sides > 0:
        posture = "orientable_leak"
        claim = "side_doors_restore_a_backside"
    else:
        posture = "no_manifold"
        claim = "without_exclusive_door_there_is_only_weather"
    return {
        "spec": SPEC,
        "name": "Non-Orientable Door",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Möbius / non-orientable manifolds — no consistent backside",
            "Gate exclusive door — every hop is the same face",
        ],
        "exclusive_door": door,
        "side_doors": sides,
        "posture": posture,
        "claim": claim,
        "thesis": "If it has a side door, it is orientable — and leakable.",
        "gatekeep": "Proprietary non-orientable door doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Non-Orientable Door",
        "inventor": INVENTOR,
        "example_ok": topology(exclusive_door=True, side_doors=0),
        "example_leak": topology(exclusive_door=True, side_doors=2),
        "live": f"{base}/.well-known/nonorientable.json",
        "xenohardware": f"{base}/.well-known/xenohardware.json",
        "their_production": False,
    }
