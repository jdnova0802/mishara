"""Use-time Finality Sink — fuse must still be LIVE at redeem.

Issue-time hop is not enough. Redeem rechecks the named fuse before consume.
TOCTOU between hop and spend is DENY. This is the physics Prefinality and
bind tickets both need.

fuse_lookup callback returns a hop/lookup dict; we accept LIVE only.
Missing/unreachable fuse → halt (fail closed).
"""
from __future__ import annotations

from typing import Any, Callable

SPEC = "gate-finality-sink-v1"
REASON_FUSE_REQUIRED = "fuse_id_required_at_sink"
REASON_FUSE_NOT_LIVE = "fuse_not_live_at_use_time"
REASON_FUSE_UNREACHABLE = "fuse_unreachable_at_use_time"
REASON_FUSE_HALT = "fuse_halt_at_use_time"

FuseLookup = Callable[[str], dict | None]


def _state_of(hop: dict | None) -> str:
    if not isinstance(hop, dict):
        return "UNREACHABLE"
    for key in ("state", "fuse_state", "status"):
        raw = hop.get(key)
        if raw is None and isinstance(hop.get("fuse"), dict):
            raw = hop["fuse"].get(key)
        if raw is not None:
            return str(raw).strip().upper()
    return "UNKNOWN"


def recheck(*, fuse_id: str | None, fuse_lookup: FuseLookup | None) -> dict[str, Any]:
    """Fail closed unless fuse is LIVE at use time."""
    fid = (fuse_id or "").strip()
    meta: dict[str, Any] = {
        "spec": SPEC,
        "ok": False,
        "halt": True,
        "fuse_id": fid or None,
        "use_time": True,
        "toctou_closed": True,
    }
    if not fid:
        meta["reason"] = REASON_FUSE_REQUIRED
        return meta
    if fuse_lookup is None:
        # No callback configured → fail closed in production posture.
        # Tests may pass a stub; app always wires velaru lookup.
        meta["reason"] = REASON_FUSE_UNREACHABLE
        meta["hint"] = "fuse_lookup callback required at redeem"
        return meta
    try:
        hop = fuse_lookup(fid)
    except Exception:
        meta["reason"] = REASON_FUSE_UNREACHABLE
        return meta
    state = _state_of(hop)
    meta["fuse_state"] = state
    meta["fuse_hop"] = {
        "halt": bool((hop or {}).get("halt")) if isinstance(hop, dict) else True,
        "verdict": (hop or {}).get("verdict") if isinstance(hop, dict) else False,
        "http_status": (hop or {}).get("http_status") if isinstance(hop, dict) else None,
    }
    if not isinstance(hop, dict):
        meta["reason"] = REASON_FUSE_UNREACHABLE
        return meta
    if hop.get("halt") is True or hop.get("verdict") is False:
        meta["reason"] = REASON_FUSE_HALT
        return meta
    if state != "LIVE":
        meta["reason"] = REASON_FUSE_NOT_LIVE
        return meta
    meta.update({"ok": True, "halt": False, "reason": None})
    return meta


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Use-time Finality Sink",
        "what": "Recheck fuse LIVE at redeem — hop ink is not spend grant.",
        "not": [
            "cached LIVE from issue time",
            "soft omit under latency panic",
            "museum hop",
        ],
        "redeem": f"{base}/v1/pas/bind-ticket/redeem",
        "prefinality": f"{base}/.well-known/prefinality.json",
        "toctou_closed": True,
        "fail_closed": True,
        "their_production": False,
    }
