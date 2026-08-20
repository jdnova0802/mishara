"""Counterproductivity Threshold — Illich: past a point, more controls worsen spend.

Illich counterproductivity: tools beyond a threshold invert and harm the
goal they served. Gate: past a density of dashboards, alerts, and AI
governance PDFs, 'safety' increases irreversible bypass pressure (Jevons +
Goodhart). The mouth is the threshold device — one alphabet, not infinite
controls. Copycats add controls until the mouth is optional.

Gatekeep only to ourselves: Illich counterproductivity → mouth as threshold.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-counterproductivity-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def threshold(
    *,
    control_count: int | None = None,
    mouth_present: bool | None = None,
    bypass_pressure: str | None = None,
) -> dict[str, Any]:
    n = int(control_count) if control_count is not None else 0
    mouth = True if mouth_present is None else bool(mouth_present)
    pressure = (bypass_pressure or "unknown").lower()
    if n >= 8 and not mouth:
        posture = "counterproductive"
        claim = "control_density_without_mouth_increases_bypass_pressure"
    elif mouth and n >= 0:
        posture = "threshold_held"
        claim = "mouth_caps_control_sprawl_into_allow_halt_block"
    elif n >= 5 and pressure in ("rising", "high"):
        posture = "approaching_inversion"
        claim = "more_controls_correlating_with_bypass_pressure"
    else:
        posture = "below_threshold_or_unevaluated"
        claim = "insufficient_sprawl_signal"
    return {
        "spec": SPEC,
        "name": "Counterproductivity Threshold",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Ivan Illich — counterproductivity / tools for conviviality",
            "Gate via negativa + Goodhart — subtract; never KPI HALTs",
        ],
        "control_count": n,
        "mouth_present": mouth,
        "bypass_pressure": pressure,
        "posture": posture,
        "claim": claim,
        "thesis": "Infinite controls without a mouth become the hazard.",
        "gatekeep": "Proprietary Illich threshold for Gate control sprawl. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Counterproductivity Threshold",
        "inventor": INVENTOR,
        "example_bad": threshold(control_count=12, mouth_present=False, bypass_pressure="rising"),
        "example_held": threshold(control_count=3, mouth_present=True),
        "live": f"{base}/.well-known/counterproductivity.json",
        "via_negativa": f"{base}/.well-known/via-negativa.json",
        "their_production": False,
    }
