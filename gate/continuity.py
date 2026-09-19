"""Human Continuity — incapacity, departure, compromise as protocol.

The boom left offboarding as folklore and death-of-principal as
"delete the account." Continuity is the missing law: when the human
root can no longer authorize, attenuated authority must become
non-completable — not hopefully cleaned up later.
"""
from __future__ import annotations

import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from gate import mandate as mandate_mod
except ImportError:
    import mandate as mandate_mod

SPEC = "gate-continuity-v1"
EVENTS = (
    "incapacity",   # cannot authorize
    "departure",    # left the role / org
    "compromise",   # credentials or will under duress
    "death",        # biological / legal end of principal
    "suspension",   # temporary hold
)

_lock = threading.Lock()
_events: dict[str, dict[str, Any]] = {}
_by_principal: dict[str, list[str]] = {}


def _iso(ts: float | None = None) -> str:
    dt = datetime.fromtimestamp(ts or time.time(), tz=timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _reset_for_tests() -> None:
    with _lock:
        _events.clear()
        _by_principal.clear()


def record(
    *,
    human_principal_id: str,
    event: str,
    reason: str = "",
    human_root_digest: str | None = None,
    agent_id: str | None = None,
    cascade_die: bool = True,
    public_url: str = "",
) -> dict:
    principal = (human_principal_id or "").strip()
    kind = (event or "").strip().lower()
    if not principal:
        return {"ok": False, "reason": "human_principal_id_required", "event": None}
    if kind not in EVENTS:
        return {"ok": False, "reason": "unknown_event", "event": None, "events": list(EVENTS)}

    eid = f"cont_{uuid.uuid4().hex}"
    now = time.time()
    row = {
        "spec": SPEC,
        "continuity_id": eid,
        "human_principal_id": principal,
        "human_root_digest": (human_root_digest or "").strip() or None,
        "agent_id": (agent_id or "").strip() or None,
        "event": kind,
        "reason": (reason or "").strip() or kind,
        "recorded_at": _iso(now),
        "recorded_at_unix": int(now),
        "cascade_die": bool(cascade_die),
        "death": None,
        "invariant": (
            "Continuity is protocol, not offboarding folklore. "
            "When the human root cannot authorize, descendants must not complete."
        ),
    }

    death_out = None
    if cascade_die:
        # Mortality: void the right to become real for this principal lineage.
        death_out = mandate_mod.die(
            human_principal_id=principal,
            human_root_digest=human_root_digest,
            agent_id=agent_id if kind in ("compromise", "suspension") else None,
            reason=f"continuity:{kind}:{row['reason']}",
            public_url=public_url,
        )
        row["death"] = {
            "ok": death_out.get("ok"),
            "death_id": (death_out.get("death_certificate") or {}).get("death_id"),
            "reason": death_out.get("reason"),
        }

    with _lock:
        _events[eid] = dict(row)
        _by_principal.setdefault(principal, []).append(eid)

    # Index into Finder — continuity is searchable, not folklore.
    try:
        from gate import finder as finder_mod
    except ImportError:
        try:
            import finder as finder_mod
        except ImportError:
            finder_mod = None
    if finder_mod is not None:
        try:
            finder_mod.record_continuity(row)
        except Exception:
            pass

    return {
        "ok": True,
        "reason": None,
        "event": row,
        "death": death_out,
        "invariant": row["invariant"],
    }


def get(continuity_id: str) -> dict | None:
    with _lock:
        row = _events.get(continuity_id)
        return dict(row) if row else None


def for_principal(human_principal_id: str) -> list[dict]:
    pid = (human_principal_id or "").strip()
    with _lock:
        ids = list(_by_principal.get(pid) or [])
        return [dict(_events[i]) for i in ids if i in _events]


def list_events(limit: int = 100) -> list[dict]:
    with _lock:
        rows = sorted(
            (_events.values()),
            key=lambda r: int(r.get("recorded_at_unix") or 0),
            reverse=True,
        )
    return [dict(r) for r in rows[: max(1, min(int(limit), 500))]]


def is_non_authorizing(human_principal_id: str) -> dict:
    """True if continuity has ended the principal's right to authorize."""
    events = for_principal(human_principal_id)
    terminal = [e for e in events if e.get("event") in ("incapacity", "departure", "compromise", "death")]
    latest = terminal[0] if terminal else None
    # for_principal returns chronological append order; prefer latest terminal
    if terminal:
        latest = max(terminal, key=lambda e: int(e.get("recorded_at_unix") or 0))
    return {
        "non_authorizing": bool(latest),
        "event": latest,
        "human_principal_id": human_principal_id,
    }


def manifest(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Gate Human Continuity",
        "description": (
            "Incapacity, departure, compromise, death — when the human root "
            "can no longer authorize, attenuated authority becomes non-completable."
        ),
        "invariant": "Offboarding folklore is not protocol. Continuity cascades into mortality.",
        "events": list(EVENTS),
        "record": f"{base}/v1/continuity/record",
        "get": f"{base}/v1/continuity/{{continuity_id}}",
        "for_principal": f"{base}/v1/continuity/principal/{{human_principal_id}}",
        "well_known": f"{base}/.well-known/continuity.json",
        "related": {
            "mandate": f"{base}/.well-known/mandate.json",
            "finder": f"{base}/.well-known/finder.json",
        },
    }
