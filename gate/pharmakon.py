"""Pharmakon Dose — Stiegler: automation is poison and cure; the mouth is the dose.

Bernard Stiegler: pharmakon — the same technical object wounds and heals.
Agent/PAS automation cures latency and poisons restraint. Gate does not
abstain from automation; it doses it with a mouth. Undosed automation is
toxicology. Copycats sell the bottle without the dropper.

Gatekeep only to ourselves: Stiegler pharmakon → mouth as dose, not abstinence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-pharmakon-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dose(*, automation: bool | None = None, mouth: bool | None = None) -> dict[str, Any]:
    auto = bool(automation)
    m = bool(mouth)
    if auto and not m:
        posture = "undosed_poison"
        claim = "automation_without_mouth_is_toxic"
    elif auto and m:
        posture = "dosed"
        claim = "mouth_is_the_dropper"
    elif m and not auto:
        posture = "dose_without_drug"
        claim = "mouth_ready_automation_absent"
    else:
        posture = "unevaluated"
        claim = "no_pharmakon_assay"
    return {
        "spec": SPEC,
        "name": "Pharmakon Dose",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Bernard Stiegler — pharmakon (poison/cure of technical objects)",
            "Plato / Derrida — pharmakon; Gate convivial + technique limit",
        ],
        "automation": auto,
        "mouth": m,
        "posture": posture,
        "claim": claim,
        "thesis": "Do not abstain from agents. Dose them. The mouth is the dose.",
        "gatekeep": "Proprietary pharmakon-dose doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Pharmakon Dose",
        "inventor": INVENTOR,
        "example_dosed": dose(automation=True, mouth=True),
        "example_toxic": dose(automation=True, mouth=False),
        "live": f"{base}/.well-known/pharmakon.json",
        "technique_limit": f"{base}/.well-known/technique-limit.json",
        "their_production": False,
    }
