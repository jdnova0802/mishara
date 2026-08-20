"""Always/Never — Feaver property for the mouth.

Always work when CHARGE orders LIVE. Never work when DEAD / timeout / soft-yes.
'Mostly works' is a failed never-clause.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-always-never-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def assay(
    *,
    charge_ordered: bool | None = None,
    became_live: bool | None = None,
    timeout_as_live: bool | None = None,
    soft_yes_as_live: bool | None = None,
) -> dict[str, Any]:
    ordered = bool(charge_ordered)
    live = bool(became_live)
    bad_timeout = bool(timeout_as_live)
    bad_soft = bool(soft_yes_as_live)
    never_ok = not bad_timeout and not bad_soft
    always_ok = (not ordered) or live
    if not never_ok:
        posture = "never_clause_broken"
        claim = "fail_closed_required"
        ok = False
    elif ordered and not live:
        posture = "always_clause_broken"
        claim = "charge_must_resurrect"
        ok = False
    else:
        posture = "always_never_holds"
        claim = "feaver_property_satisfied"
        ok = True
    return {
        "spec": SPEC,
        "name": "Always/Never",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Peter Feaver — always when ordered, never when not",
            "Nuclear NC2 / PAL",
            "Gate fail-closed + CHARGE-only",
        ],
        "charge_ordered": ordered,
        "became_live": live,
        "timeout_as_live": bad_timeout,
        "soft_yes_as_live": bad_soft,
        "always_ok": always_ok,
        "never_ok": never_ok,
        "posture": posture,
        "claim": claim,
        "passes": ok,
        "thesis": "Mostly works is broken. Always CHARGE. Never soft-yes/timeout LIVE.",
        "gatekeep": "Proprietary always/never assay. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Always/Never",
        "inventor": INVENTOR,
        "example_broken_never": assay(timeout_as_live=True),
        "example_holds": assay(charge_ordered=True, became_live=True),
        "live": f"{base}/.well-known/always-never.json",
        "hardest": f"{base}/.well-known/hardest.json",
        "their_production": False,
    }
