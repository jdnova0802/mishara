"""Topological HALT — ALLOW is not a continuous deformation of HALT.

HALT and ALLOW are different homotopy classes on the chassis. You cannot
slide a risk score until HALT becomes ALLOW. CHARGE is a defect / surgery:
it changes winding. Dashboard gradients are contractible loops that never
leave HALT's class. Copycats think LIVE is nearby in KPI space. It is not
nearby. It is another component.

Not Earth-side: no 'close enough to approve'.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-topological-halt-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def deform(
    *,
    sliding_score_toward_allow: bool | None = None,
    charge_id: str | None = None,
    decision: str | None = None,
) -> dict[str, Any]:
    slide = bool(sliding_score_toward_allow)
    charge = bool((charge_id or "").strip())
    d = (decision or "").upper()
    if slide and not charge and d == "ALLOW":
        posture = "illegal_deformation"
        claim = "kpi_path_is_contractible_does_not_change_class"
    elif charge:
        posture = "surgery"
        claim = "charge_changes_winding_halt_to_live"
    elif d in ("HALT", "BLOCK"):
        posture = "protected_class"
        claim = "halt_is_topologically_stable"
    else:
        posture = "unevaluated"
        claim = "no_path_data"
    return {
        "spec": SPEC,
        "name": "Topological HALT",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "sliding_score_toward_allow": slide,
        "charge_present": charge,
        "decision": d or None,
        "posture": posture,
        "claim": claim,
        "thesis": "ALLOW is not near HALT. CHARGE is surgery, not a slider.",
        "gatekeep": "Proprietary topological HALT. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Topological HALT",
        "inventor": INVENTOR,
        "example_stable": deform(decision="HALT"),
        "example_illegal": deform(sliding_score_toward_allow=True, decision="ALLOW"),
        "live": f"{base}/.well-known/topological-halt.json",
        "complementarity": f"{base}/.well-known/complementarity.json",
        "their_production": False,
    }
