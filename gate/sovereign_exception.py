"""Sovereign Exception CHARGE — Agamben: only CHARGE suspends DEAD lawfully.

State of exception: sovereign decides when the norm is suspended.
Gate inverts costume politics into ops: DEAD is the norm; CHARGE is the
sole lawful exception that opens LIVE. Soft-yes exception is usurpation —
exception without costliness. Copycats invent a thousand exceptions; Gate has one.

Gatekeep only to ourselves: Agamben exception → CHARGE-only suspension of DEAD.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-sovereign-exception-v1"
INVENTOR = "Nisaba LLC / Gate"

USURPATIONS = (
    "admin_live_toggle",
    "uw_approve_as_live",
    "demo_production_flip",
    "support_override",
    "risk_committee_email",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def decide(*, path: str | None = None, charge_id: str | None = None) -> dict[str, Any]:
    p = (path or "").strip().lower()
    has_charge = bool((charge_id or "").strip())
    if p == "charge" or (has_charge and p in ("", "dead_to_live", "resurrection")):
        verdict = "lawful_exception"
        claim = "charge_sole_suspension_of_dead"
    elif p in USURPATIONS or p.startswith("soft_") or p.endswith("_override"):
        verdict = "usurpation"
        claim = "exception_without_costliness_is_not_sovereign_ops"
    else:
        verdict = "norm_holds"
        claim = "dead_remains_default"
    return {
        "spec": SPEC,
        "name": "Sovereign Exception CHARGE",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Giorgio Agamben — state of exception / sovereign decision",
            "Gate — DEAD norm; CHARGE-only lawful exception to LIVE",
        ],
        "usurpations": list(USURPATIONS),
        "path": p or None,
        "charge_present": has_charge,
        "verdict": verdict,
        "claim": claim,
        "thesis": "One exception. Named. Costly. Everything else is usurpation.",
        "gatekeep": "Proprietary exception doctrine for DEAD→LIVE. Ours.",
        "not_politics_cosplay": True,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Sovereign Exception CHARGE",
        "inventor": INVENTOR,
        "example_lawful": decide(path="charge", charge_id="chg_1"),
        "example_usurpation": decide(path="admin_live_toggle"),
        "live": f"{base}/.well-known/sovereign-exception.json",
        "costliness": f"{base}/.well-known/costliness.json",
        "their_production": False,
    }
