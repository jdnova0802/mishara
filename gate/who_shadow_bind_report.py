"""WHO Shadow Bind Report — independent monitoring treaty lacks for bind path.

Real: WHO Pandemic Agreement / INB (2024–2026) — independent monitoring of
outbreak response; shadow reporting when states under-report; transparency gaps.

Twist: Carriers lack independent bind-path monitoring — shadow report publishes
HALT depth + ghost events strangers can cite when internal dashboards stay green.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-who-shadow-bind-report-v1"
INVENTION = "WHO Shadow Bind Report"
TIER = "S"
FAMILY = "s-tier"

REAL = {
    "institution": "WHO Pandemic Agreement / Intergovernmental Negotiating Body",
    "concept": "Independent monitoring + shadow reporting when official counts lag",
    "gap": "Treaty monitoring for health; no analog for irreversible bind path",
    "url": "https://www.who.int/news/item/01-06-2024-who-member-states-agree-to-continue-negotiations",
}


def shadow_report(
    *,
    internal_dashboard_green: bool | None = None,
    halt_depth: int | None = None,
    ghost_events: int | None = None,
    stranger_verify_count: int | None = None,
    published: bool | None = None,
) -> dict[str, Any]:
    halts = max(0, int(halt_depth or 0))
    ghosts = max(0, int(ghost_events or 0))
    verifies = max(0, int(stranger_verify_count or 0))
    green = bool(internal_dashboard_green)
    divergence = green and (halts > 0 or ghosts > 0)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "tier": TIER,
        "real_institution": REAL,
        "verdict": "SHADOW_DIVERGENCE" if divergence else "ALIGNED",
        "divergence": divergence,
        "halt_depth": halts,
        "ghost_events": ghosts,
        "stranger_verify_count": verifies,
        "published": bool(published),
        "rule": "When dashboard stays green but HALT depth rises — shadow report is the treaty analog.",
        "carrier_analog": "Independent bind-path monitor examiners can pull without carrier PR",
    }


def attach(plan: dict) -> dict:
    cemetery = plan.get("halt_cemetery") if isinstance(plan.get("halt_cemetery"), dict) else {}
    ghost = plan.get("ghost_bind") if isinstance(plan.get("ghost_bind"), dict) else {}
    ev = shadow_report(
        internal_dashboard_green=bool(plan.get("verdict") == "LIVE" or plan.get("state") == "LIVE"),
        halt_depth=int(cemetery.get("tombstone_count") or (1 if plan.get("halt") else 0)),
        ghost_events=1 if ghost.get("haunted") else 0,
        stranger_verify_count=1 if plan.get("verify_url") else 0,
        published=True,
    )
    plan["who_shadow_report"] = ev
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "tier": TIER,
        "one_liner": "WHO shadow bind report — independent HALT monitor when dashboard stays green.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/who-shadow-bind-report",
        "well_known": f"{base}/.well-known/who-shadow-bind-report.json",
    }
