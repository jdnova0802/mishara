"""Protracted Outage Order — Fedwire Critical Payment Order for bind finality.

Real institution: Federal Reserve Fedwire Funds Service Operating Circular 6
(effective January 5, 2026). Appendix B: during Protracted Outage, Critical
Payment Orders are final and irrevocable on oral confirm — even if Master Account
entries lag until next business day.

Twist: bind ticket redeem as Critical Bind Order — finality without fail-open,
accounting honesty when Gate ledger lags.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-protracted-outage-order-v1"
INVENTION = "Protracted Outage Order"
FAMILY = "institutional-twist"

REAL = {
    "institution": "Federal Reserve Banks",
    "instrument": "Fedwire Funds Service Operating Circular 6",
    "effective": "2026-01-05",
    "appendix": "Protracted Outage Procedures",
    "concept": "Critical Payment Order — final irrevocable on oral confirm during outage",
    "url": "https://www.frbservices.org/resources/rules-regulations/operating-circular-6.html",
}


def evaluate(
    *,
    protracted_outage: bool | None = None,
    critical_bind_order: bool | None = None,
    oral_confirm: bool | None = None,
    master_account_lagged: bool | None = None,
    fail_open_requested: bool | None = None,
) -> dict[str, Any]:
    if fail_open_requested:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "verdict": "REJECTED",
            "final": False,
            "reason": "fail_open_not_in_protracted_procedures",
            "rule": REAL["concept"],
        }
    if not protracted_outage:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "verdict": "NORMAL_OPS",
            "final": None,
            "detail": "Not protracted outage — standard redeem path.",
        }
    if critical_bind_order and oral_confirm:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "real_institution": REAL,
            "verdict": "CRITICAL_BIND_FINAL",
            "final": True,
            "irrevocable": True,
            "master_account_lagged": bool(master_account_lagged),
            "accounting_entries_may_lag": True,
            "fail_open": False,
            "detail": (
                "Bind final on oral confirm during outage — ledger may lag; "
                "not a ghost bind."
            ),
            "stavan_line": (
                "Like Fedwire OC6: final when confirmed, not when your ops console feels better."
            ),
        }
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "verdict": "NOT_FINAL",
        "final": False,
        "reason": "critical_bind_order_requires_oral_confirm",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Fedwire Critical Payment Order semantics for bind during Gate outage.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/protracted-outage-order",
        "well_known": f"{base}/.well-known/protracted-outage-order.json",
        "pairs_with": "Cold Standby Mirror · Bind Weather",
    }
