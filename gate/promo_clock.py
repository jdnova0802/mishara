"""Promo Clock — fail-closed surface dates for liveness products.

Marketing clocks must not lie. If \"next drill\" is in the past, do not
show it as upcoming — flip to last-proved or hide.

Product cousin: Stale LIVE Rejector (clearance). This is Stale Promo Rejector (site).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-promo-clock-v1"


def _parse(ts: str | None) -> datetime | None:
    if not ts or not str(ts).strip():
        return None
    t = str(ts).strip().replace("Z", "+00:00")
    # allow "2026-08-18T17:00:00-07:00" and date-only
    if len(t) == 10 and t[4] == "-" and t[7] == "-":
        t = t + "T23:59:59+00:00"
    try:
        dt = datetime.fromisoformat(t)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def evaluate(
    *,
    next_at: str | None = None,
    last_proved_at: str | None = None,
    label: str | None = None,
    href: str | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Return a fail-closed promo surface state.

    modes:
      upcoming — next_at in the future (safe to say \"Next drill\")
      proved   — next is stale/missing; last_proved_at exists → \"Last proved\"
      hidden   — nothing honest to show (do not render a dead Next)
      invalid  — unparseable timestamps (treat as hidden)
    """
    now_dt = _parse(now) or datetime.now(timezone.utc)
    nxt = _parse(next_at)
    proved = _parse(last_proved_at)

    if next_at and nxt is None:
        return {
            "spec": SPEC,
            "ok": False,
            "mode": "invalid",
            "render": False,
            "headline": None,
            "reason": "next_at_unparseable",
            "now": _iso(now_dt),
        }

    if nxt is not None and nxt > now_dt:
        return {
            "spec": SPEC,
            "ok": True,
            "mode": "upcoming",
            "render": True,
            "headline": "Next drill",
            "when": _iso(nxt),
            "when_display": next_at,
            "label": label,
            "href": href,
            "stale": False,
            "now": _iso(now_dt),
        }

    # next missing or past → never show as Next
    if proved is not None:
        return {
            "spec": SPEC,
            "ok": True,
            "mode": "proved",
            "render": True,
            "headline": "Last proved",
            "when": _iso(proved),
            "when_display": last_proved_at,
            "label": label,
            "href": href,
            "stale": bool(nxt is not None and nxt <= now_dt),
            "stale_next_at": _iso(nxt) if nxt else None,
            "now": _iso(now_dt),
        }

    return {
        "spec": SPEC,
        "ok": True,
        "mode": "hidden",
        "render": False,
        "headline": None,
        "reason": "stale_or_missing_next_without_proved",
        "stale": bool(nxt is not None and nxt <= now_dt),
        "stale_next_at": _iso(nxt) if nxt else None,
        "label": label,
        "href": href,
        "now": _iso(now_dt),
    }


def manifest(public_url: str = "", **kwargs: Any) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    state = evaluate(**kwargs) if kwargs else evaluate()
    return {
        "spec": SPEC,
        "name": "Promo Clock",
        "one_liner": "Past \"next drill\" dates fail closed — show last proved or hide.",
        "cousin": "stale_live — clearance; promo_clock — site surface",
        "well_known": f"{base}/.well-known/promo-clock.json" if base else None,
        "script": f"{base}/static/promo-clock.js" if base else None,
        "usage": {
            "html": (
                '<div class="drill-bar" data-promo-clock '
                'data-next-at="2026-09-01T17:00:00-07:00" '
                'data-last-proved-at="2026-08-24T06:31:00Z" '
                'data-label="AWS Loft SF" data-href="/fuse/demo"></div>'
                '<script src="/static/promo-clock.js" defer></script>'
            ),
            "rule": "If next_at <= now → never headline Next drill.",
        },
        "state": state,
    }
