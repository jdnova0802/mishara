"""Restraint Invoice — billable SKU: stranger prove of what did not bind/pay/fire.

Invention (NORTH_STAR applicable-now): insurance language for counterfactual.
Builds on counterfactual spend receipts.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import counterfactual as cf_mod
except ImportError:
    import counterfactual as cf_mod

SPEC = "gate-restraint-invoice-v1"
INVENTION = "Restraint Invoice"
FAMILY = "applicable_now"
SKU = "restraint_invoice"
DEFAULT_PRICE_CENTS = 75000  # $750 after-action pack seed


def draft(
    *,
    job_id: str | None = None,
    fuse_id: str | None = None,
    decision: str | None = None,
    acted: bool | None = None,
    verify_url: str | None = None,
    event_id: str | None = None,
    public_url: str = "",
    price_cents: int | None = None,
) -> dict[str, Any]:
    """Draft a restraint invoice when HALT/BLOCK without act — prove non-spend."""
    d = (decision or "").strip().upper()
    is_cf = cf_mod.is_counterfactual(decision=d, acted=acted)
    forbidden = cf_mod.forbidden_for_job(job_id)
    claim = None
    if is_cf and event_id:
        claim = cf_mod.build_claim(
            event_id=event_id,
            fuse_id=fuse_id or "",
            job_id=job_id,
            decision=d,
            verify_url=verify_url,
            created_at="",
            receipt_hash=None,
        )
    cents = int(price_cents if price_cents is not None else DEFAULT_PRICE_CENTS)
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "sku": SKU,
        "billable": is_cf,
        "price_cents": cents,
        "price_label": f"${cents / 100:.0f}",
        "job_id": job_id,
        "fuse_id": fuse_id,
        "decision": d or None,
        "acted": acted,
        "counterfactual": is_cf,
        "forbidden_writes": forbidden,
        "claim": claim,
        "verify_url": verify_url,
        "line_items": (
            [
                {
                    "description": "Stranger-verifiable prove of non-bind / non-payout",
                    "qty": 1,
                    "amount_cents": cents,
                }
            ]
            if is_cf
            else []
        ),
        "insurance_language": (
            "Counterfactual spend receipt: within observation boundary, "
            "forbidden bind/payout transition did not execute at Gate hop."
        ),
        "pull": f"{base}/demo/pas/restraint-invoice" if base else None,
        "rule": "Bill what did not stick — stranger prove, not narrative.",
        "pairs_with": "Counterfactual Spend · Hop Tattoo · Soft-Yes Snare",
    }


def attach(plan: dict, *, public_url: str = "") -> dict:
    plan["restraint_invoice"] = draft(
        job_id=plan.get("job_id"),
        fuse_id=plan.get("fuse_id"),
        decision=plan.get("decision"),
        acted=plan.get("acted"),
        verify_url=plan.get("verify_url"),
        event_id=plan.get("event_id"),
        public_url=public_url,
    )
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Billable SKU — stranger prove of what did not bind / pay / fire.",
        "sku": SKU,
        "default_price_cents": DEFAULT_PRICE_CENTS,
        "demo": f"POST {base}/demo/pas/restraint-invoice",
        "well_known": f"{base}/.well-known/restraint-invoice.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. After-action pack — CUO Drill Pack companion.",
    }
