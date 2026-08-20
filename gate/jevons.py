"""Jevons Restraint — automation rebound into more irreversible attempts.

Jevons paradox: efficiency gains increase total consumption via rebound.
Agent/PAS automation makes bind cheaper → more attempts, more doors,
midnight renewals. Efficiency without a mouth produces spend rebound.

Gate: the mouth is the anti-rebound — attenuates the flood of cheap attempts
to a finite decision alphabet. Without it, clear-before-wire loses to volume.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-jevons-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rebound(
    *,
    automation_efficiency: str | None = "high",
    mouth_present: bool | None = True,
    attempt_volume: str | None = "rising",
) -> dict[str, Any]:
    eff = (automation_efficiency or "high").lower()
    mouth = True if mouth_present is None else bool(mouth_present)
    vol = (attempt_volume or "rising").lower()
    if eff in ("high", "extreme") and not mouth:
        posture = "jevons_uncontrolled"
        claim = "cheap_bind_automation_rebounds_into_more_irreversible_attempts"
    elif mouth:
        posture = "rebound_attenuated"
        claim = "mouth_absorbs_attempt_volume_into_allow_halt_block"
    else:
        posture = "low_efficiency_or_unevaluated"
        claim = "insufficient_rebound_pressure"
    return {
        "spec": SPEC,
        "name": "Jevons Restraint",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Jevons paradox — efficiency → lower effective cost → higher total use",
            "Rebound effect — demand response to efficiency",
            "Gate variety mouth — attenuate attempt flood",
        ],
        "automation_efficiency": eff,
        "attempt_volume": vol,
        "mouth_present": mouth,
        "posture": posture,
        "claim": claim,
        "thesis": "Making bind easier without a mouth guarantees spend rebound.",
        "gatekeep": "Proprietary Jevons framing for automation vs mouth. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Jevons Restraint",
        "inventor": INVENTOR,
        "example_danger": rebound(automation_efficiency="high", mouth_present=False),
        "example_attenuated": rebound(automation_efficiency="high", mouth_present=True),
        "live": f"{base}/.well-known/jevons.json",
        "variety": f"{base}/.well-known/variety.json",
        "their_production": False,
    }
