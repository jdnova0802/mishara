"""All Doors — exclusive mouth across API, UI, and renewal auto-bind.

Guidewire: bind-only → Bound; UI Bind never hits Cloud API; RenewalWF
auto-binds. One missing door = skip-clear. This invention refuses partial welds.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-all-doors-v1"
INVENTOR = "Nisaba LLC / Gate"

DOORS = ("cloud_api_bind_only", "ui_bind", "renewal_workflow")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def weld(*, doors_honored: list[str] | None = None) -> dict[str, Any]:
    honored = set(doors_honored or [])
    missing = [d for d in DOORS if d not in honored]
    if not missing:
        posture = "all_doors_welded"
        claim = "exclusive_surface_complete"
        ok = True
    elif "cloud_api_bind_only" in honored and missing:
        posture = "partial_weld_leak"
        claim = "ui_or_renewal_skip_clear"
        ok = False
    else:
        posture = "unwelded"
        claim = "no_production_mouth"
        ok = False
    return {
        "spec": SPEC,
        "name": "All Doors",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "PolicyCenter bind-only → Bound",
            "UI Bind / Gosu checking set",
            "PendingRenewalWF auto-bind",
            "Gate exclusive door + other_doors()",
        ],
        "required_doors": list(DOORS),
        "doors_honored": sorted(honored),
        "missing": missing,
        "posture": posture,
        "claim": claim,
        "passes": ok,
        "thesis": "Partial weld is a skip-clear. All doors or no production.",
        "gatekeep": "Proprietary all-doors weld. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "All Doors",
        "inventor": INVENTOR,
        "example_leak": weld(doors_honored=["cloud_api_bind_only"]),
        "example_complete": weld(doors_honored=list(DOORS)),
        "live": f"{base}/.well-known/all-doors.json",
        "capture": f"{base}/.well-known/capture.json" if base else None,
        "hardest": f"{base}/.well-known/hardest.json",
        "their_production": False,
    }
