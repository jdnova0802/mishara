"""Parasite Filter — Serres: exclude the soft-yes that feeds without welding.

Michel Serres' parasite interrupts exchange and feeds on the channel.
In Gate, the parasite is any path that consumes permission bandwidth
(approvals, demos, dashboards) without paying weld/CHARGE costliness.
The mouth is a filter: parasite noise stays outside the decision network.

Gatekeep only to ourselves: Serres parasite → soft-yes exclusion from permission.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-parasite-v1"
INVENTOR = "Nisaba LLC / Gate"

PARASITES = (
    "uw_approve_without_charge",
    "demo_their_production_true",
    "admin_live_toggle",
    "dashboard_green_as_permission",
    "ai_governance_pdf_as_door",
)

HOST_PATHS = (
    "charge_witness",
    "exclusive_door_hop",
    "license_parent_live_check",
    "epoch_unlock_with_costliness",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def filter_path(*, operation: str | None = None) -> dict[str, Any]:
    op = (operation or "").strip().lower()
    is_parasite = op in PARASITES or op.startswith("soft_") or op.startswith("bypass_")
    is_host = op in HOST_PATHS or op.startswith("charge") or op.startswith("weld")
    if is_parasite:
        verdict = "exclude_from_decision_network"
        claim = "parasite_feeds_on_channel_without_costliness"
    elif is_host:
        verdict = "admit_to_decision_network"
        claim = "host_path_pays_or_enforces_mouth"
    else:
        verdict = "classify_before_admit"
        claim = "unknown_operation"
    return {
        "spec": SPEC,
        "name": "Parasite Filter",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Michel Serres — The Parasite (noise/interruption/feeding on exchange)",
            "Gate closure — external soft-yes cannot enter permission network",
        ],
        "parasite_patterns": list(PARASITES),
        "host_paths": list(HOST_PATHS),
        "operation": op or None,
        "verdict": verdict,
        "claim": claim,
        "thesis": "Soft-yes without weld is a parasite on the permission channel.",
        "gatekeep": "Proprietary parasite filter for Gate doors. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Parasite Filter",
        "inventor": INVENTOR,
        "example_exclude": filter_path(operation="uw_approve_without_charge"),
        "example_admit": filter_path(operation="charge_witness"),
        "live": f"{base}/.well-known/parasite.json",
        "closure": f"{base}/.well-known/closure.json",
        "their_production": False,
    }
