"""Bind-event settlement clock on one signed receipt.

This module is Bind Room / bind_events only. The window is the 60-minute
human settlement cycle on an open HOLD. It is not shared infrastructure
for other mouths.

Do not import this from issuing_mouth. Stripe issuing_authorization.request
must AUTHORIZE or DECLINE in under two seconds; a 60-minute window is
meaningless there. A later vertical that needs a clock gets its own
window as a parameter on that product, not this constant.

A stranger counts. LATE means the signed disposition is still open after
due_at. Denial is never LATE. The underlying record stays out of the clock.

First live LATE is still unobserved (unit tests backdate due_at under
GATE_DEV_MODE). Do not mint one to close that gap.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any

SPEC = "gate-clock-v1"
BIND_SETTLEMENT_WINDOW_MINUTES = 60
WINDOW_MINUTES = BIND_SETTLEMENT_WINDOW_MINUTES
DISPOSITIONS = ("open", "held", "denied")

_OPEN = {"HOLD", "PENDING", "OPEN", "IN_FLIGHT"}
_DENIED = {"BLOCK", "DENY", "DENIED", "DEAD", "NO_GO", "NO", "HALT"}
_HELD = {"GO", "ALLOW", "LIVE", "CLEAR", "PASS"}


def _dev_mode() -> bool:
    return os.getenv("GATE_DEV_MODE", "").strip().lower() in ("1", "true", "yes", "on")


def _parse(value: str | None) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _iso(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _reason(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text or len(text) > 80:
        return None
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.:-")
    if any(ch not in allowed for ch in text):
        return None
    return text


def classify(decision: str | None, acted: bool | None) -> str:
    name = (decision or "").strip().upper()
    if name in _OPEN:
        return "open"
    if name in _DENIED:
        return "denied"
    if acted is True or name in _HELD:
        return "held"
    return "open"


def normalize(
    raw: dict | None,
    *,
    started_at: str,
    decision: str | None,
    acted: bool | None,
) -> dict[str, Any] | None:
    """Allowlisted clock. Drops every other key, including any document body."""
    raw = raw if isinstance(raw, dict) else {}
    started = _parse(raw.get("started_at") if isinstance(raw.get("started_at"), str) else None)
    if started is None:
        started = _parse(started_at)
    if started is None:
        return None
    due = _parse(raw.get("due_at") if isinstance(raw.get("due_at"), str) else None)
    if due is None:
        due = started + timedelta(minutes=BIND_SETTLEMENT_WINDOW_MINUTES)
    disposition = raw.get("disposition")
    if disposition not in DISPOSITIONS:
        disposition = classify(decision, acted)
    reason = _reason(raw.get("reason_code")) if disposition == "denied" else None
    if disposition == "denied" and reason is None:
        reason = _reason(decision) or "denied"
    clock: dict[str, Any] = {
        "spec": SPEC,
        "started_at": _iso(started),
        "due_at": _iso(due),
        "disposition": disposition,
        "window_minutes": BIND_SETTLEMENT_WINDOW_MINUTES,
    }
    if reason:
        clock["reason_code"] = reason
    return clock


def attach(
    hop: dict | None,
    *,
    started_at: str,
    decision: str | None,
    acted: bool | None,
    inject: bool | None = None,
) -> dict:
    """Return a hop whose clock is the one that will be signed.

    Production (GATE_DEV_MODE off) ignores hop['clock'] times and
    disposition. Gate writes started_at + 60 minutes from classify.
    Tests may inject a backdated due_at only when GATE_DEV_MODE is on.
    """
    base = dict(hop) if isinstance(hop, dict) else {}
    allow_inject = _dev_mode() if inject is None else inject
    raw = base.get("clock") if allow_inject and isinstance(base.get("clock"), dict) else None
    clock = normalize(
        raw,
        started_at=started_at,
        decision=decision,
        acted=acted,
    )
    if clock is not None:
        base["clock"] = clock
    return base


def word(clock: dict | None, *, now: datetime | None = None) -> str | None:
    """LATE when the signed disposition is still open after due_at."""
    if not isinstance(clock, dict) or clock.get("disposition") != "open":
        return None
    due = _parse(clock.get("due_at") if isinstance(clock.get("due_at"), str) else None)
    if due is None:
        return None
    moment = now or datetime.now(timezone.utc)
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    if moment.astimezone(timezone.utc) > due:
        return "LATE"
    return None
