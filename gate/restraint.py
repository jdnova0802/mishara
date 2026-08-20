"""Public inventory of nos this mouth actually printed.

Not a catalog of possible nos. Production HALT/BLOCK only. No PII,
no hop body, no job_id, not demo. Empty is honest.
"""
from __future__ import annotations

try:
    from gate import db
except ImportError:
    import db

SPEC = "gate-restraint-v1"
DECISIONS = ("HALT", "BLOCK")
_REASON_RE = __import__("re").compile(r"^[A-Za-z0-9._:-]{1,128}$")


def _reason_token(hop: dict | None) -> str | None:
    if not isinstance(hop, dict):
        return None
    for key in ("epoch_reason", "reason"):
        raw = hop.get(key)
        if raw is None:
            continue
        token = str(raw).strip()[:128]
        if token and _REASON_RE.match(token):
            return token
    return None


def public_event(row: dict) -> dict:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else None
    item = {
        "event_id": row.get("id"),
        "decision": (row.get("decision") or "").upper(),
        "created_at": row.get("created_at"),
        "receipt_hash": row.get("receipt_hash"),
        "reason": _reason_token(hop),
        "acted": False,
    }
    return item


def inventory(public_url: str, *, limit: int = 200) -> dict:
    base = (public_url or "").rstrip("/")
    rows = db.list_restraint_events(limit=limit)
    events = [public_event(row) for row in rows]
    try:
        from gate import constitution as constitution_mod
    except ImportError:
        import constitution as constitution_mod

    # STIT surface: published nos are duty-fulfillment evidence, not error logs.
    latest_reason = events[0].get("reason") if events else None
    latest_decision = events[0].get("decision") if events else "HALT"
    stit = constitution_mod.stit_surface(
        decision=latest_decision,
        reason=latest_reason,
        public_url=base,
    )
    return {
        "spec": SPEC,
        "name": "Inventory of nos",
        "what": "HALT/BLOCK this mouth printed for a metered account. Not demo. Not a menu of possible nos.",
        "not": [
            "PII",
            "hop_json",
            "job_id",
            "license_number",
            "a directory of licenses",
            "demo hops",
        ],
        "pii": False,
        "demo": False,
        "their_production": False,
        "count": len(events),
        "events": events,
        "stit": stit,
        "license_fuse": f"{base}/.well-known/license-fuse.json",
        "listings": f"{base}/.well-known/listings.json",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
        "mouth_constitution": f"{base}/.well-known/mouth-constitution.json",
    }
