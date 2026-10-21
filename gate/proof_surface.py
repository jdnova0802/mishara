"""Public proof strip — existing evidence-head + relics, no new doctrine."""
from __future__ import annotations

import time
from typing import Any

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import evidence_log as evidence_log_mod
except ImportError:
    import evidence_log as evidence_log_mod

try:
    from gate import liturgy as liturgy_mod
except ImportError:
    import liturgy as liturgy_mod

_CACHE: dict[str, Any] = {"at": 0.0, "strip": None}
_TTL = 15.0


def halted_write_count(events: list[dict] | None = None) -> int:
    """Count real HALT/BLOCK bind events. Canonical drill is not a live stop."""
    rows = events if events is not None else db.list_bind_events(None, limit=500)
    n = 0
    for ev in rows or []:
        if (ev.get("decision") or "") in ("HALT", "BLOCK"):
            n += 1
    return n


def evidence_strip(*, public_url: str = "") -> dict[str, Any]:
    empty = {
        "tree_size": 0,
        "root_hash": "",
        "root_short": "",
        "checked_at": None,
        "halted_writes": 0,
        "relic_count": 0,
        "head_url": "/.well-known/evidence-head.json",
        "watch_url": "/.well-known/evidence-watch.json",
        "mass_url": "/mass",
    }
    now = time.time()
    cached = _CACHE.get("strip")
    if cached and now - float(_CACHE.get("at") or 0) < _TTL:
        return dict(cached)
    try:
        rows = db.list_bind_events_chronological()
        leaves = evidence_log_mod.log_from_rows(rows)
        head = evidence_log_mod.signed_tree_head(leaves)
        root = head.get("root_hash") or ""
        events = db.list_bind_events(None, limit=500)
        halted = halted_write_count(events)
        relics = liturgy_mod.relics_manifest(public_url or "", events)
        strip = {
            "tree_size": head.get("tree_size"),
            "root_hash": root,
            "root_short": (root[:16] + "…") if len(root) > 16 else root,
            "checked_at": head.get("timestamp"),
            "halted_writes": halted,
            "relic_count": relics.get("count") or 0,
            "head_url": "/.well-known/evidence-head.json",
            "watch_url": "/.well-known/evidence-watch.json",
            "mass_url": "/mass",
        }
    except Exception:
        return empty
    _CACHE["at"] = now
    _CACHE["strip"] = strip
    return dict(strip)
