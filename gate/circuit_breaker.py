"""Item 19 — flag a fuse if BLOCK/HOLD spikes in a short window."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

SPEC = "gate-circuit-breaker-v1"
WINDOW_SECONDS = 900
SPIKE_COUNT = 5
HOT = {"BLOCK", "HALT", "HOLD"}


def _parse(ts: str | None) -> datetime | None:
    if not ts:
        return None
    s = ts.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def evaluate(rows: list[dict[str, Any]], fuse_id: str, *, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=WINDOW_SECONDS)
    hot = 0
    for row in rows:
        if str(row.get("fuse_id") or "") != fuse_id:
            continue
        when = _parse(str(row.get("created_at") or ""))
        if when is None or when < cutoff:
            continue
        if str(row.get("decision") or "").upper() in HOT:
            hot += 1
    opened = hot >= SPIKE_COUNT
    return {
        "spec": SPEC,
        "fuse_id": fuse_id,
        "window_seconds": WINDOW_SECONDS,
        "spike_count": SPIKE_COUNT,
        "hot_in_window": hot,
        "open": opened,
        "action": "HALT_AGENT" if opened else "NONE",
    }
