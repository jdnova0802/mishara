"""Settlement-window clock on one act.

The signed receipt carries the start, the due time, and a disposition.
A stranger counts. LATE means the act is still open after the window.
The window is the settlement cycle (60 minutes), not a public-records statute.
A denial names a reason code. The underlying record stays out of the receipt.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

SPEC = "gate-clock-v1"
WINDOW_MINUTES = 60
DISPOSITIONS = ("open", "held", "denied")

_OPEN = {"HOLD", "PENDING", "OPEN", "IN_FLIGHT"}
_DENIED = {"BLOCK", "DENY", "DENIED", "DEAD", "NO_GO", "NO", "HALT"}
_HELD = {"GO", "ALLOW", "LIVE", "CLEAR", "PASS"}


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
        due = started + timedelta(minutes=WINDOW_MINUTES)
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
        "window_minutes": WINDOW_MINUTES,
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
) -> dict:
    """Return a hop whose clock is the one that will be signed."""
    base = dict(hop) if isinstance(hop, dict) else {}
    clock = normalize(
        base.get("clock") if isinstance(base.get("clock"), dict) else None,
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
