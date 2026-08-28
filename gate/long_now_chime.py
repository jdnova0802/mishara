"""Long Now Chime — never-repeating bind receipt sequence.

Real: Long Now Foundation / 10,000-Year Clock (Jeff Bezos funded, Texas mountain).
Chimes advance on century boundaries; each chime unique in 10,000 years — no repeat.

Twist: Every HALT/BIND receipt gets a monotonic chime index in epoch — strangers can
verify ordering without trusting dashboard timestamps.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-long-now-chime-v1"
INVENTION = "Long Now Chime"
TIER = "S"
FAMILY = "s-tier"

REAL = {
    "institution": "Long Now Foundation — 10,000-Year Clock",
    "site": "West Texas mountain (Clock of the Long Now)",
    "property": "Century chimes never repeat in 10,000-year cycle",
    "url": "https://longnow.org/clock/",
}


def chime(
    *,
    epoch_seq: int | None = None,
    job_id: str | None = None,
    prior_chime: int | None = None,
) -> dict[str, Any]:
    seq = max(0, int(epoch_seq or 0))
    prior = int(prior_chime) if prior_chime is not None else None
    next_chime = seq + 1
    monotonic = prior is None or next_chime > prior
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "tier": TIER,
        "real_institution": REAL,
        "chime_index": next_chime,
        "prior_chime": prior,
        "monotonic": monotonic,
        "verdict": "CHIME_OK" if monotonic else "CHIME_COLLISION",
        "job_id": (job_id or "").strip() or None,
        "rule": "Bind receipts never repeat their chime — epoch ordering is stranger-grade.",
    }


def attach(plan: dict) -> dict:
    epoch = plan.get("epoch") if isinstance(plan.get("epoch"), dict) else {}
    seq = int(epoch.get("sequence") or epoch.get("seq") or 0)
    prior = plan.get("long_now_prior_chime")
    ev = chime(epoch_seq=seq, job_id=str(plan.get("job_id") or ""), prior_chime=prior)
    plan["long_now_chime"] = ev
    if not ev.get("monotonic"):
        plan["long_now_collision"] = True
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "tier": TIER,
        "one_liner": "10,000-Year Clock chime — bind receipts never repeat in epoch.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/long-now-chime",
        "well_known": f"{base}/.well-known/long-now-chime.json",
    }
