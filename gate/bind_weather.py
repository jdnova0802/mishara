"""Bind Weather — public carrier-facing availability + HALT depth report.

SLA honesty after fail-closed. Boring dashboard energy — not five-nines cosplay.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import db
except ImportError:
    import db

SPEC = "gate-bind-weather-v1"
INVENTION = "Bind Weather"
FAMILY = "competitive-response"


def report(*, limit: int = 100) -> dict[str, Any]:
    lim = max(1, min(int(limit or 100), 1000))
    rows = db.list_bind_events(None, limit=lim)
    halt = sum(1 for r in rows if (r.get("decision") or "").upper() in ("HALT", "BLOCK"))
    allow = sum(1 for r in rows if (r.get("decision") or "").upper() == "ALLOW")
    acted = sum(1 for r in rows if r.get("acted"))
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "topology": "single_region_render",
        "sla_claim": "best_effort_no_five_nines_today",
        "fail_closed": True,
        "sample_size": len(rows),
        "halt_depth": halt,
        "allow_count": allow,
        "acted_count": acted,
        "redeem_coupled": True,
        "maintenance": "coordinate_renewal_windows",
        "forecast": {
            "cold_standby_mirror": "roadmap",
            "multi_region": "production_weld",
        },
        "rule": "Weather report is honesty — bind stops when Gate stops.",
        "stavan_ready": True,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Carrier uptime + HALT depth — fail-closed stated with ops cost.",
        "demo": f"GET {base}/demo/pas/bind-weather",
        "well_known": f"{base}/.well-known/bind-weather.json",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
        "posture": "Third engineer question made visible — not hidden SLA PDF.",
    }
