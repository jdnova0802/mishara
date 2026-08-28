"""Renewal Day Throat — mouth on the 03:00 batch stick path.

Agent-mesh papers optimize RPC leases. Nobody owns the carrier renewal calendar.
Every auto-renew in the batch needs fresh ticket + redeem — no ghost stick at scale.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-renewal-day-throat-v1"
INVENTION = "Renewal Day Throat"
FAMILY = "competitive-response"

VERDICT_OPEN = "RENEWAL_OPEN"
VERDICT_CHOKE = "RENEWAL_CHOKE"
VERDICT_BATCH_OK = "BATCH_OK"

DEFAULT_WINDOW_UTC = "03:00"


def _in_renewal_window(now: datetime, window_hour: int = 3, slack_minutes: int = 120) -> bool:
    start = now.replace(hour=window_hour, minute=0, second=0, microsecond=0)
    end_min = window_hour * 60 + slack_minutes
    cur = now.hour * 60 + now.minute
    start_min = window_hour * 60
    return start_min <= cur <= end_min or cur <= slack_minutes  # wrap midnight batch


def evaluate_stick(
    *,
    job_id: str | None,
    auto_renew: bool | None = None,
    fresh_ticket_id: str | None = None,
    redeemed: bool | None = None,
    stale_ticket_id: str | None = None,
    prior_policy_ticket: str | None = None,
) -> dict[str, Any]:
    jid = (job_id or "").strip()
    ghosts: list[str] = []
    if auto_renew and not fresh_ticket_id:
        ghosts.append("auto_renew_without_fresh_ticket")
    if auto_renew and fresh_ticket_id and prior_policy_ticket and fresh_ticket_id == prior_policy_ticket:
        ghosts.append("reused_prior_term_ticket")
    if auto_renew and fresh_ticket_id and not redeemed:
        ghosts.append("ticket_not_redeemed_at_batch")
    if stale_ticket_id and fresh_ticket_id and stale_ticket_id == fresh_ticket_id:
        ghosts.append("stale_ticket_reused")
    choked = bool(ghosts)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "job_id": jid or None,
        "auto_renew": bool(auto_renew),
        "verdict": VERDICT_CHOKE if choked else VERDICT_OPEN,
        "may_stick": not choked,
        "ghosts": ghosts,
        "requires": ["fresh_ticket_id", "redeemed_at_commit", "bind_only_write"],
        "rule": "Batch renewal is not a TTL lease — every stick gets a new mouth.",
    }


def evaluate_batch(
    sticks: list[dict] | None = None,
    *,
    now: str | None = None,
    window_hour: int = 3,
) -> dict[str, Any]:
    now_dt = datetime.now(timezone.utc)
    if now:
        try:
            t = now.strip()
            if t.endswith("Z"):
                t = t[:-1] + "+00:00"
            now_dt = datetime.fromisoformat(t).astimezone(timezone.utc)
        except ValueError:
            pass
    items = sticks if isinstance(sticks, list) else []
    rows = []
    choked = 0
    for raw in items:
        if not isinstance(raw, dict):
            continue
        ev = evaluate_stick(
            job_id=raw.get("job_id"),
            auto_renew=raw.get("auto_renew"),
            fresh_ticket_id=raw.get("fresh_ticket_id") or raw.get("ticket_id"),
            redeemed=raw.get("redeemed"),
            stale_ticket_id=raw.get("stale_ticket_id"),
            prior_policy_ticket=raw.get("prior_policy_ticket"),
        )
        if ev["verdict"] == VERDICT_CHOKE:
            choked += 1
        rows.append(ev)
    in_window = _in_renewal_window(now_dt, window_hour=window_hour)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "window_utc": f"{window_hour:02d}:00",
        "in_renewal_window": in_window,
        "stick_count": len(rows),
        "choked_count": choked,
        "verdict": VERDICT_BATCH_OK if choked == 0 else VERDICT_CHOKE,
        "may_batch_stick": choked == 0,
        "sticks": rows,
        "rule": "03:00 batch velocity × stale clearance = ghost bind heaven. Throat on the calendar.",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Mouth on renewal batch — fresh ticket + redeem per stick, not agent-mesh lease.",
        "demo": f"POST {base}/demo/pas/renewal-day-throat",
        "well_known": f"{base}/.well-known/renewal-day-throat.json",
        "pairs_with": "Ghost Renewal Snare · Bind Ticket · Renewal Day",
        "posture": "Carrier calendar moat — IBCT does not own this window.",
    }
