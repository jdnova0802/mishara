"""HRO Preoccupation — High Reliability: published nos over cheerful greens.

Weick/Sutcliffe HRO: preoccupation with failure, reluctance to simplify,
sensitivity to operations, commitment to resilience, deference to expertise.
Gate: restraint inventory is preoccupation with failure made public.
Dashboard-only 'all green' is the opposite HRO. Copycats simplify to a score.

Gatekeep only to ourselves: HRO → published HALTs as reliability, not shame.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-hro-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def posture_of(
    *,
    hide_halts: bool | None = None,
    publish_restraint: bool | None = None,
    simplify_to_score: bool | None = None,
) -> dict[str, Any]:
    hide = bool(hide_halts)
    pub = bool(publish_restraint)
    simp = bool(simplify_to_score)
    if hide or simp:
        posture = "anti_hro"
        claim = "cheerful_green_is_not_reliability"
    elif pub:
        posture = "hro"
        claim = "preoccupation_with_failure_is_public"
    else:
        posture = "unevaluated"
        claim = "no_inventory_assay"
    return {
        "spec": SPEC,
        "name": "HRO Preoccupation",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Weick & Sutcliffe — managing the unexpected; HRO principles",
            "Gate proof-of-restraint + Goodhart — nos as evidence not KPI",
        ],
        "hide_halts": hide,
        "publish_restraint": pub,
        "simplify_to_score": simp,
        "posture": posture,
        "claim": claim,
        "thesis": "Reliability is a public no. Cheerful green is a simplification error.",
        "gatekeep": "Proprietary HRO doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "HRO Preoccupation",
        "inventor": INVENTOR,
        "example_hro": posture_of(publish_restraint=True),
        "example_anti": posture_of(hide_halts=True, simplify_to_score=True),
        "live": f"{base}/.well-known/hro.json",
        "proof_restraint": f"{base}/.well-known/proof-restraint.json",
        "their_production": False,
    }
