"""Mimetic Soft-Yes Breaker — Girard: stop the race to imitate cheap approval.

Mimetic desire: agents copy each other's wants; rivalry escalates.
Ops form: teams imitate whoever shipped soft-yes fastest — until ruin.
Gate breaks mimesis by making the focal act clear-before-wire (Schelling)
and costly (weld/CHARGE). You cannot win by copying the bypass; the mouth
makes the bypass non-focal. Copycats amplify mimetic soft-yes.

Gatekeep only to ourselves: Girard mimesis → mouth as anti-mimetic default.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-mimetic-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def break_race(
    *,
    peers_soft_yes: bool | None = None,
    exclusive_door: bool | None = None,
    welded: bool | None = None,
    decision: str | None = None,
) -> dict[str, Any]:
    peers = bool(peers_soft_yes)
    door = bool(exclusive_door)
    weld = bool(welded)
    d = (decision or "").upper()
    if peers and not door and not weld:
        posture = "mimetic_soft_yes_race"
        claim = "imitating_bypass_escalates_to_ruin"
    elif door and weld and d in ("HALT", "BLOCK", "ALLOW"):
        posture = "mimesis_broken"
        claim = "focal_clear_before_wire_displaces_bypass_copying"
    elif door or weld:
        posture = "anti_mimetic_scaffold"
        claim = "door_or_weld_present_race_weakened"
    else:
        posture = "unevaluated"
        claim = "insufficient_rivalry_data"
    return {
        "spec": SPEC,
        "name": "Mimetic Soft-Yes Breaker",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "René Girard — mimetic desire / rivalry",
            "Schelling — focal points (Gate Schelling Default)",
            "Gate — clear-before-wire breaks soft-yes imitation races",
        ],
        "peers_soft_yes": peers,
        "exclusive_door": door,
        "welded": weld,
        "decision": d or None,
        "posture": posture,
        "claim": claim,
        "thesis": "The mouth ends the race to imitate cheap approval.",
        "gatekeep": "Proprietary Girard framing for soft-yes rivalry. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Mimetic Soft-Yes Breaker",
        "inventor": INVENTOR,
        "example_race": break_race(peers_soft_yes=True, exclusive_door=False, welded=False),
        "example_broken": break_race(
            peers_soft_yes=True, exclusive_door=True, welded=True, decision="HALT"
        ),
        "live": f"{base}/.well-known/mimetic.json",
        "schelling": f"{base}/.well-known/schelling.json",
        "their_production": False,
    }
