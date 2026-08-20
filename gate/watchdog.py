"""Watchdog Mouth — if the chassis is not petted with exclusive-door hops, HALT.

Hardware watchdogs reset a runaway CPU. Gate's watchdog: a production
claim without exclusive-door traffic, CHARGE discipline, or published
nos is a runaway. Demo-only 'LIVE' without pets is a bite. Copycats
disable the watchdog for UX.

Gatekeep only to ourselves: watchdog timer → production must be petted by the mouth.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-watchdog-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def pet(
    *,
    their_production: bool | None = None,
    exclusive_door_honored: bool | None = None,
    watchdog_enabled: bool | None = None,
) -> dict[str, Any]:
    prod = bool(their_production)
    door = bool(exclusive_door_honored)
    en = True if watchdog_enabled is None else bool(watchdog_enabled)
    if not en and prod:
        posture = "watchdog_disabled_illegal"
        claim = "production_without_watchdog_is_runaway_cpu"
    elif prod and not door:
        posture = "bite"
        claim = "production_unpetted_halt"
    elif prod and door:
        posture = "petted"
        claim = "mouth_kicks_the_dog"
    else:
        posture = "demo_idle"
        claim = "watchdog_armed_outside_production"
    return {
        "spec": SPEC,
        "name": "Watchdog Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Hardware watchdog timers — unpetted CPUs reset",
            "Gate their_production false until real weld + exclusive door",
        ],
        "production_claimed": prod,
        "exclusive_door_honored": door,
        "watchdog_enabled": en,
        "posture": posture,
        "claim": claim,
        "thesis": "Production that never hits the mouth has already hung. The watchdog bites.",
        "gatekeep": "Proprietary watchdog-mouth doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Watchdog Mouth",
        "inventor": INVENTOR,
        "example_petted": pet(their_production=True, exclusive_door_honored=True),
        "example_bite": pet(their_production=True, exclusive_door_honored=False),
        "live": f"{base}/.well-known/watchdog.json",
        "skin": f"{base}/.well-known/skin.json",
        "their_production": False,
    }
