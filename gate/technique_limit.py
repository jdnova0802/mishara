"""Technique Limit — Ellul: the mouth is a limit on autonomous technique.

Jacques Ellul: technique tends toward self-augmentation — efficiency as
absolute. Agent/PAS automation is technique. Without an exterior limit,
it will clear every irreversible path that can be cleared. Gate's mouth
is that exterior: not more technique, a decision alphabet that can say no.
Copycats sell more technique as safety.

Gatekeep only to ourselves: Ellul technique → mouth as non-technical limit.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-technique-limit-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def limit(
    *,
    automation_autonomous: bool | None = None,
    mouth_can_halt: bool | None = None,
    decision: str | None = None,
) -> dict[str, Any]:
    auto = bool(automation_autonomous)
    can_halt = True if mouth_can_halt is None else bool(mouth_can_halt)
    d = (decision or "").upper()
    if auto and not can_halt:
        posture = "technique_unbounded"
        claim = "efficiency_will_clear_every_path"
    elif can_halt and d in ("HALT", "BLOCK"):
        posture = "limit_exercised"
        claim = "mouth_said_no_to_autonomous_technique"
    elif can_halt:
        posture = "limit_installed"
        claim = "exterior_decision_alphabet_present"
    else:
        posture = "unevaluated"
        claim = "insufficient_technique_data"
    return {
        "spec": SPEC,
        "name": "Technique Limit",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Jacques Ellul — The Technological Society; autonomy of technique",
            "Gate — HALT as exterior limit, not another efficiency layer",
        ],
        "automation_autonomous": auto,
        "mouth_can_halt": can_halt,
        "decision": d or None,
        "posture": posture,
        "claim": claim,
        "thesis": "Safety-as-more-automation is still technique. The mouth is the limit.",
        "gatekeep": "Proprietary Ellul limit doctrine for Gate. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Technique Limit",
        "inventor": INVENTOR,
        "example_unbounded": limit(automation_autonomous=True, mouth_can_halt=False),
        "example_exercised": limit(automation_autonomous=True, mouth_can_halt=True, decision="HALT"),
        "live": f"{base}/.well-known/technique-limit.json",
        "jevons": f"{base}/.well-known/jevons.json",
        "their_production": False,
    }
