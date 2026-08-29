"""Qualified Irreversible Commit — the event meter.

One server-side redeem consume + one irreversible write.
Billable: max(MAR, LAQ × per_QIC_rate), stacked with cleared-flow bps.

Satoshi's miners got the block reward. The inventor got $0.
Here the named HoldCo meters every real commit.

$0 until Gate 1. Demo redeem is not their production.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

try:
    from gate import exclusion as exclusion_mod
except ImportError:
    import exclusion as exclusion_mod

try:
    from gate import operator_invoice as operator_mod
except ImportError:
    import operator_invoice as operator_mod

SPEC = "gate-qic-meter-v1"
PATENT = "64/124,027"
OPERATOR = "Nisaba LLC"
NAME = "qualified_irreversible_commit"
FORMULA = "max(MAR, LAQ × per_QIC_rate)"
DEFAULT_PER_QIC_USD = 0.10
THEIR_PRODUCTION = False

# Illustrative ranges from the term sheet — not a forecast or offer.
PER_QIC_USD_RANGE = (0.05, 2.00)
MAR_USD_RANGE = (50_000, 500_000)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _base(public_url: str) -> str:
    return (public_url or "").rstrip("/")


def laq_count() -> int:
    """Licensed actual QIC = unique redeemed job ids in the spend map."""
    try:
        return len(exclusion_mod.spent_job_ids())
    except Exception:
        return 0


def stamp_event(*, job_id: str, ticket_id: str) -> dict[str, Any]:
    """Attach to a successful redeem. Counted; not billable until Gate 1."""
    return {
        "spec": SPEC,
        "name": NAME,
        "counted": True,
        "job_id": job_id,
        "ticket_id": ticket_id,
        "definition": (
            "One server-side atomic redeem consume plus one irreversible write "
            "in the Licensed Field."
        ),
        "billable_usd": 0,
        "reason": "gate1_unpaid",
        "formula": FORMULA,
        "their_production": THEIR_PRODUCTION,
    }


def billable(
    *,
    mar_usd: float = 0,
    per_qic_usd: float = DEFAULT_PER_QIC_USD,
    their_production: bool = THEIR_PRODUCTION,
    laq: int | None = None,
) -> dict[str, Any]:
    count = int(laq) if laq is not None else laq_count()
    raw = max(float(mar_usd), float(count) * float(per_qic_usd))
    usd = 0.0 if not their_production else raw
    return {
        "spec": SPEC,
        "formula": FORMULA,
        "laq": count,
        "mar_usd": float(mar_usd),
        "per_qic_usd": float(per_qic_usd),
        "raw_usd": raw,
        "billable_usd": usd,
        "their_production": bool(their_production),
        "reason": None if their_production else "gate1_unpaid",
        "stacks_with": {
            "cleared_flow_bps": operator_mod.BPS,
            "carry_bps_above_hurdle": operator_mod.BPS_CARRY,
            "conformant_cert_annual": True,
        },
    }


def counts_by_vertical() -> dict[str, str]:
    return {
        "platform_agents": "tool_invocation_commit",
        "operators_payout": "withdraw_payout_stick",
        "enterprise_spend": "org_root_delegated_write",
        "insurance_field_a": "bind_only_commit",
        "hiring": "decision_stick",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = _base(public_url)
    meter = billable()
    return {
        "spec": SPEC,
        "patent": PATENT,
        "operator": OPERATOR,
        "inventor": inventor_mod.stamp(),
        "evaluated_at": _now(),
        "qic": {
            "name": NAME,
            "definition": (
                "One server-side atomic redeem consume plus one irreversible write "
                "in the Licensed Field — vertical-agnostic "
                "(bind, payout, tool commit, release)."
            ),
            "counts_by_vertical_example": counts_by_vertical(),
        },
        "caq": {
            "name": "contracted_annual_qic",
            "definition": "Volume commitment in license agreement (tier / overage).",
        },
        "laq": {
            "name": "licensed_actual_annual_qic",
            "definition": "Metered actual events — unique redeemed job ids in the spend map.",
            "count": meter["laq"],
        },
        "billable_formula": FORMULA,
        "billable": meter,
        "per_qic_usd_range": list(PER_QIC_USD_RANGE),
        "mar_usd_range": list(MAR_USD_RANGE),
        "hybrid_bps_note": (
            "Cleared-flow or premium bps may apply instead of or stacked with per-QIC — "
            "see /operator register fees."
        ),
        "until_gate1_usd": 0,
        "their_production": THEIR_PRODUCTION,
        "vs_satoshi": {
            "satoshi": "Block reward to anonymous miners. Inventor cannot cash.",
            "here": "Named HoldCo meters every real commit and stays on the invoice.",
        },
        "links": {
            "page": f"{base}/conformant",
            "conformant": f"{base}/.well-known/conformant.json",
            "licensed_field": f"{base}/.well-known/licensed-field.json",
            "exclusion": f"{base}/.well-known/exclusion.json",
            "spend_protocol": f"{base}/.well-known/spend-protocol.json",
            "operator": f"{base}/operator",
            "register": f"{base}/.well-known/register.json",
        },
        "page": f"{base}/conformant",
        "gatekeep": "QIC meter. $0 until Gate 1. Not a buyer chrome plate.",
    }
