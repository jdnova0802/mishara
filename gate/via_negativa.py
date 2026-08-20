"""Via Negativa Mouth — antifragile subtraction over dashboard addition.

Taleb antifragile: via negativa — improve by removing what harms.
Barbell: extreme safety + small convex bets; avoid fragile middle.

Gate: remove bypass doors, remove soft-yes resurrection, remove PII from
restraint — do not add another risk score. CHARGE/weld barbell: mostly
fail-closed safety + costly regime change as the only convex reopen.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-via-negativa-v1"
INVENTOR = "Nisaba LLC / Gate"

SUBTRACT = (
    "bypass_doors_without_exclusive_weld",
    "uw_approve_as_resurrection",
    "admin_LIVE_toggle",
    "PII_on_public_nos",
    "museum_receipts_as_product",
    "safety_score_as_permission",
)

BARBELL = {
    "safe_mass": "fail-closed HALT/BLOCK; epoch lock; license grip; one married write",
    "convex_tip": "CHARGE / weld — costly reopen with bounded downside (named witness)",
    "fragile_middle_rejected": "moderate risk dashboards that look safe until ruin",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def prescribe(*, added_control: str | None = None) -> dict[str, Any]:
    add = (added_control or "").strip()
    is_additive_trap = add.lower() in (
        "risk_score",
        "dashboard",
        "trust_pdf",
        "ai_governance_policy",
        "more_alerts",
    ) or add.startswith("add_")
    return {
        "spec": SPEC,
        "name": "Via Negativa Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Taleb — Antifragile; via negativa; barbell; optionality over prediction",
            "Gate — exclusive door removes bypass; CHARGE removes soft resurrection",
        ],
        "subtract_first": list(SUBTRACT),
        "barbell": BARBELL,
        "proposed_addition": add or None,
        "verdict": (
            "reject_additive_fragility_subtract_instead"
            if is_additive_trap
            else "evaluate_whether_addition_or_subtraction"
        ),
        "thesis": "The mouth gets stronger by removing doors, not by adding scores.",
        "gatekeep": "Proprietary via-negativa operating doctrine for Gate. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Via Negativa Mouth",
        "inventor": INVENTOR,
        "example_reject_score": prescribe(added_control="risk_score"),
        "example_ok": prescribe(added_control="remove_renewal_bypass"),
        "live": f"{base}/.well-known/via-negativa.json",
        "skin": f"{base}/.well-known/skin.json",
        "their_production": False,
    }
