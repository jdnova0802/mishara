"""POSIWID Mouth — purpose is what it does: if it cannot HALT, it is not a mouth.

Stafford Beer: the purpose of a system is what it does. A 'safety product'
that always ALLOWs has the purpose of skip-clear. Gate publishes what it
does: HALT/BLOCK under fail-closed, CHARGE-only LIVE. Copycats declare
purpose in decks. POSIWID reads the ISA.

Gatekeep only to ourselves: Beer POSIWID → mouth identified by HALT capability.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-posiwid-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def purpose(*, can_halt: bool | None = None, always_allow: bool | None = None) -> dict[str, Any]:
    halt = bool(can_halt)
    always = bool(always_allow)
    if always or not halt:
        posture = "purpose_is_skip_clear"
        claim = "system_that_cannot_halt_is_not_a_mouth"
    else:
        posture = "purpose_is_mouth"
        claim = "what_it_does_includes_halt"
    return {
        "spec": SPEC,
        "name": "POSIWID Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Stafford Beer — POSIWID (purpose is what it does)",
            "Gate variety alphabet — HALT is not optional decoration",
        ],
        "can_halt": halt,
        "always_allow": always,
        "posture": posture,
        "claim": claim,
        "thesis": "If it never HALTs in production, its purpose is not clearance. It is flow.",
        "gatekeep": "Proprietary POSIWID doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "POSIWID Mouth",
        "inventor": INVENTOR,
        "example_mouth": purpose(can_halt=True, always_allow=False),
        "example_flow": purpose(can_halt=False, always_allow=True),
        "live": f"{base}/.well-known/posiwid.json",
        "variety": f"{base}/.well-known/variety.json",
        "their_production": False,
    }
