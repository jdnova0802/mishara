"""NSS Finality Stamp — DTCC/FICC settlement finality moment for bind.

Real institution: DTCC Fixed Income Clearing Corporation + Federal Reserve
National Settlement Service (Operating Circular 12). Point of finality: when
Master Accounts debited/credited through NSS — final and irrevocable in central bank money.

Twist: bind stick gets explicit finality stamp separate from hop LIVE — the moment
premium becomes history, not when dashboard went green.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-nss-finality-stamp-v1"
INVENTION = "NSS Finality Stamp"
FAMILY = "institutional-twist"

REAL = {
    "institution": "DTCC FICC + Federal Reserve National Settlement Service",
    "finality_rule": "Master Account debit/credit through NSS — final irrevocable",
    "oc12": "Federal Reserve Operating Circular 12",
    "sec": "SEC 17Ad-22 settlement finality disclosure",
    "url": "https://www.dtcc.com/clearing/ficc",
}


def stamp(
    *,
    job_id: str | None,
    bind_consumed: bool | None = None,
    master_account_posted: bool | None = None,
    hop_live_only: bool | None = None,
) -> dict[str, Any]:
    jid = (job_id or "").strip() or None
    if hop_live_only and not bind_consumed:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "real_institution": REAL,
            "verdict": "NOT_FINAL",
            "finality": False,
            "reason": "hop_live_is_not_nss_finality",
            "ghost": "dashboard_green_as_bind",
        }
    if bind_consumed and master_account_posted:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "verdict": "BIND_FINAL",
            "finality": True,
            "irrevocable": True,
            "job_id": jid,
            "money_finality_analog": "central_bank_money_posted",
            "rule": "LIVE hop ≠ NSS finality — ticket consume + post is the stick.",
        }
    if bind_consumed:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "verdict": "PENDING_POST",
            "finality": False,
            "pending": "master_account_post",
            "job_id": jid,
        }
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "verdict": "UNSTAMPED",
        "finality": False,
        "job_id": jid,
    }


def attach(plan: dict) -> dict:
    consumed = bool((plan.get("bind_ticket") or {}).get("consumed")) or plan.get("acted")
    plan["nss_finality"] = stamp(
        job_id=str(plan.get("job_id") or ""),
        bind_consumed=consumed,
        master_account_posted=bool(plan.get("acted") and plan.get("allow_bind")),
        hop_live_only=bool(plan.get("verdict") or plan.get("state") == "LIVE") and not consumed,
    )
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "FICC/NSS finality moment — hop LIVE is not bind posted.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/nss-finality-stamp",
        "well_known": f"{base}/.well-known/nss-finality-stamp.json",
    }
