"""Goodhart Mouth — restraint is evidence, not a KPI to hack.

Goodhart: when a measure becomes a target, it ceases to be a good measure.
If 'HALT count' becomes a sales metric, mouths will print theater nos.
Gate: restraint inventory is citeable evidence of production nos — not a
target. Optimize exclusive-door coverage and weld honesty, never HALT volume.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-goodhart-v1"
INVENTOR = "Nisaba LLC / Gate"

FORBIDDEN_TARGETS = (
    "maximize_halt_count",
    "maximize_receipt_volume",
    "maximize_demo_hops",
    "optimize_risk_score_alone",
)

VALID_PRESSURES = (
    "exclusive_door_coverage",
    "weld_before_their_production",
    "charge_only_resurrection",
    "stranger_verify_fetchability",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def police(*, proposed_target: str | None = None) -> dict[str, Any]:
    t = (proposed_target or "").strip().lower()
    bad = t in FORBIDDEN_TARGETS or t.startswith("maximize_") or t.startswith("kpi_")
    return {
        "spec": SPEC,
        "name": "Goodhart Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Goodhart's law — when a measure becomes a target it ceases to be a good measure",
            "Gate restraint — published nos as evidence, empty inventory can be honest",
        ],
        "forbidden_targets": list(FORBIDDEN_TARGETS),
        "valid_pressures": list(VALID_PRESSURES),
        "proposed_target": t or None,
        "verdict": "reject_goodhart_hack" if bad else "pressure_may_be_valid",
        "thesis": "Do not sell HALT volume. Sell doors that cannot bypass the mouth.",
        "gatekeep": "Proprietary Goodhart guardrail for Gate metrics. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Goodhart Mouth",
        "inventor": INVENTOR,
        "example_reject": police(proposed_target="maximize_halt_count"),
        "example_ok": police(proposed_target="exclusive_door_coverage"),
        "live": f"{base}/.well-known/goodhart.json",
        "restraint": f"{base}/.well-known/restraint.json",
        "their_production": False,
    }
