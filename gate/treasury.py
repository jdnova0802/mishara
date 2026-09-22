"""Agent treasury — attention × money-leave crossover.

Public spend feed + $handle + clear-before-leave.
Opening the feed is the attention object. Leaving money requires clearance.
"""
from __future__ import annotations

import hashlib
import json
import re
import secrets
import uuid
from typing import Any, Callable

try:
    from gate import db as db_mod
except ImportError:
    import db as db_mod

SPEC = "gate-treasury-v1"
FEED_SPEC = "gate-treasury-feed-v1"
HANDLE_RE = re.compile(r"^[a-z][a-z0-9_]{2,31}$")
RAILS = ("x402", "rtp", "withdraw", "card", "other")
STATES = ("CLEARED", "HALTED", "PENDING")


def normalize_handle(raw: str | None) -> str | None:
    h = (raw or "").strip().lower()
    if h.startswith("$"):
        h = h[1:]
    if not HANDLE_RE.match(h):
        return None
    return h


def display_handle(handle: str) -> str:
    return f"${handle}"


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _mint_leave_token() -> str:
    return f"trs_{secrets.token_urlsafe(24)}"


def claim_handle(
    *,
    handle: str,
    display_name: str | None = None,
    fuse_id: str | None = None,
    max_amount_cents: int | None = None,
    bio: str | None = None,
) -> dict:
    """Claim a public $handle. Returns leave_token once (store it)."""
    h = normalize_handle(handle)
    if not h:
        return {
            "ok": False,
            "error": "invalid_handle",
            "message": "Handle must be 3–32 chars: start with a letter, then a-z 0-9 _.",
        }
    existing = get_handle(h)
    if existing:
        return {"ok": False, "error": "handle_taken", "message": f"${h} is already claimed."}

    fuse = (fuse_id or f"fuse_treasury_{h}").strip()[:128]
    if not fuse:
        return {"ok": False, "error": "fuse_required", "message": "fuse_id required."}

    max_cents = None
    if max_amount_cents is not None:
        try:
            max_cents = max(0, int(max_amount_cents))
        except (TypeError, ValueError):
            return {"ok": False, "error": "invalid_max", "message": "max_amount_cents must be an integer."}

    leave_token = _mint_leave_token()
    now = db_mod.utc_now()
    handle_id = uuid.uuid4().hex[:16]
    name = (display_name or h).strip()[:80]
    bio_s = (bio or "").strip()[:280]

    with db_mod.db() as conn:
        conn.execute(
            """
            INSERT INTO treasury_handles (
                id, handle, display_name, bio, fuse_id, max_amount_cents,
                leave_token_hash, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'ACTIVE', ?, ?)
            """,
            (
                handle_id,
                h,
                name,
                bio_s,
                fuse,
                max_cents,
                _token_hash(leave_token),
                now,
                now,
            ),
        )

    return {
        "ok": True,
        "spec": SPEC,
        "handle": h,
        "display": display_handle(h),
        "display_name": name,
        "fuse_id": fuse,
        "max_amount_cents": max_cents,
        "leave_token": leave_token,
        "note": "Store leave_token — required to post leave. Shown once.",
        "feed_url_path": "/feed",
        "handle_url_path": f"/t/{h}",
    }


def get_handle(handle: str) -> dict | None:
    h = normalize_handle(handle)
    if not h:
        return None
    with db_mod.db() as conn:
        row = conn.execute(
            "SELECT * FROM treasury_handles WHERE handle = ?", (h,)
        ).fetchone()
    return _handle_row(row) if row else None


def verify_leave_token(handle: str, token: str | None) -> bool:
    row = get_handle(handle)
    if not row or not token:
        return False
    return secrets.compare_digest(row["leave_token_hash"], _token_hash(token.strip()))


def list_handles(*, limit: int = 50) -> list[dict]:
    limit = max(1, min(200, int(limit or 50)))
    with db_mod.db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM treasury_handles
            WHERE status = 'ACTIVE'
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [_handle_row(r) for r in rows]


def _handle_row(row: Any) -> dict:
    return {
        "id": row["id"],
        "handle": row["handle"],
        "display": display_handle(row["handle"]),
        "display_name": row["display_name"],
        "bio": row["bio"] or "",
        "fuse_id": row["fuse_id"],
        "max_amount_cents": row["max_amount_cents"],
        "leave_token_hash": row["leave_token_hash"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def public_handle(handle_row: dict) -> dict:
    return {
        "handle": handle_row["handle"],
        "display": handle_row["display"],
        "display_name": handle_row["display_name"],
        "bio": handle_row["bio"],
        "max_amount_cents": handle_row["max_amount_cents"],
        "status": handle_row["status"],
        "created_at": handle_row["created_at"],
    }


def _local_drill_clearance(fuse_id: str) -> dict:
    """Dev/offline drill when Velaru unreachable — still fail-closed on *dead* fuses."""
    fid = (fuse_id or "").lower()
    dead = "dead" in fid or fid.endswith("_halt")
    return {
        "ok": not dead,
        "halt": dead,
        "verdict": not dead,
        "state": "DEAD" if dead else "LIVE",
        "acted": not dead,
        "demo_drill": True,
        "fuse_id": fuse_id,
        "message": (
            "Local drill DEAD — leave halted."
            if dead
            else "Local drill LIVE — leave cleared (dev / upstream unreachable)."
        ),
        "verify_url": "https://velaru.xyz/verify",
    }


def clear_leave(
    *,
    handle: str,
    leave_token: str,
    amount_cents: int,
    currency: str = "USD",
    rail: str = "withdraw",
    memo: str | None = None,
    counterparty: str | None = None,
    hop_fn: Callable[[str], tuple[dict, int, dict]] | None = None,
    allow_local_drill: bool = False,
) -> dict:
    """Clear-before-leave: hop fuse → CLEARED or HALTED → public feed event."""
    h = normalize_handle(handle)
    if not h:
        return {"ok": False, "error": "invalid_handle"}
    if not verify_leave_token(h, leave_token):
        return {"ok": False, "error": "unauthorized", "message": "Invalid leave_token."}

    row = get_handle(h)
    if not row or row["status"] != "ACTIVE":
        return {"ok": False, "error": "handle_inactive"}

    try:
        amount = int(amount_cents)
    except (TypeError, ValueError):
        return {"ok": False, "error": "invalid_amount"}
    if amount <= 0:
        return {"ok": False, "error": "invalid_amount", "message": "amount_cents must be > 0."}

    if row["max_amount_cents"] is not None and amount > int(row["max_amount_cents"]):
        return {
            "ok": False,
            "error": "over_mandate",
            "message": f"Amount exceeds handle max ({row['max_amount_cents']} cents).",
            "max_amount_cents": row["max_amount_cents"],
        }

    rail_s = (rail or "withdraw").strip().lower()
    if rail_s not in RAILS:
        rail_s = "other"
    cur = (currency or "USD").strip().upper()[:8]
    memo_s = (memo or "").strip()[:200]
    cp = (counterparty or "").strip()[:120]

    hop: dict
    status = 200
    if hop_fn:
        hop, status, _ = hop_fn(row["fuse_id"])
        if not isinstance(hop, dict):
            hop = {"verdict": False, "halt": True, "state": "UNREACHABLE"}
        # Local drill fallback when upstream fail-closed in allowed env
        if allow_local_drill and (
            status >= 500
            or hop.get("fail_closed")
            or hop.get("state") == "UNREACHABLE"
        ):
            hop = _local_drill_clearance(row["fuse_id"])
            status = 200
    elif allow_local_drill:
        hop = _local_drill_clearance(row["fuse_id"])
    else:
        hop = {"verdict": False, "halt": True, "state": "UNREACHABLE", "fail_closed": True}
        status = 503

    allowed = bool(hop.get("verdict") is True or hop.get("acted") is True) and not hop.get("halt")
    if hop.get("state") == "DEAD":
        allowed = False
    state = "CLEARED" if allowed else "HALTED"
    event_id = uuid.uuid4().hex[:20]
    now = db_mod.utc_now()
    verify = hop.get("verify_url") or "https://velaru.xyz/verify"
    hop_json = json.dumps({k: hop.get(k) for k in (
        "verdict", "halt", "state", "fuse_id", "message", "demo_drill", "fail_closed", "acted"
    ) if hop.get(k) is not None})

    with db_mod.db() as conn:
        conn.execute(
            """
            INSERT INTO treasury_events (
                id, handle, state, amount_cents, currency, rail, memo,
                counterparty, fuse_id, verify_url, hop_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                h,
                state,
                amount,
                cur,
                rail_s,
                memo_s,
                cp,
                row["fuse_id"],
                verify,
                hop_json,
                now,
            ),
        )

    event = {
        "id": event_id,
        "handle": h,
        "display": display_handle(h),
        "state": state,
        "amount_cents": amount,
        "currency": cur,
        "rail": rail_s,
        "memo": memo_s,
        "counterparty": cp,
        "fuse_id": row["fuse_id"],
        "verify_url": verify,
        "created_at": now,
        "cleared": allowed,
    }
    return {
        "ok": True,
        "spec": SPEC,
        "write_executed": False,
        "clearance_only": True,
        "state": state,
        "event": event,
        "hop": json.loads(hop_json),
        "message": (
            "CLEARED — leave permitted. Gate did not move funds; exclusive door must enforce."
            if allowed
            else "HALTED — leave refused. Fail closed. No side door."
        ),
    }


def list_feed(*, handle: str | None = None, limit: int = 50) -> list[dict]:
    limit = max(1, min(200, int(limit or 50)))
    with db_mod.db() as conn:
        if handle:
            h = normalize_handle(handle)
            if not h:
                return []
            rows = conn.execute(
                """
                SELECT * FROM treasury_events
                WHERE handle = ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (h, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM treasury_events
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    return [_event_row(r) for r in rows]


def get_event(event_id: str) -> dict | None:
    eid = (event_id or "").strip()
    if not eid:
        return None
    with db_mod.db() as conn:
        row = conn.execute(
            "SELECT * FROM treasury_events WHERE id = ?", (eid,)
        ).fetchone()
    return _event_row(row) if row else None


def _event_row(row: Any) -> dict:
    return {
        "id": row["id"],
        "handle": row["handle"],
        "display": display_handle(row["handle"]),
        "state": row["state"],
        "amount_cents": int(row["amount_cents"] or 0),
        "currency": row["currency"],
        "rail": row["rail"],
        "memo": row["memo"] or "",
        "counterparty": row["counterparty"] or "",
        "fuse_id": row["fuse_id"],
        "verify_url": row["verify_url"],
        "created_at": row["created_at"],
        "cleared": row["state"] == "CLEARED",
    }


def format_amount(cents: int, currency: str = "USD") -> str:
    sign = (currency or "USD").upper()
    return f"{sign} {cents / 100:.2f}"


def feed_manifest(public_url: str, *, limit: int = 50) -> dict:
    base = (public_url or "").rstrip("/")
    events = list_feed(limit=limit)
    return {
        "spec": FEED_SPEC,
        "title": "Gate treasury feed",
        "description": (
            "Public agent spend stream. Attention object + clear-before-leave. "
            "CLEARED means leave permitted; HALTED means fail closed. Gate does not move funds."
        ),
        "human_url": f"{base}/feed",
        "claim_url": f"{base}/treasury/claim",
        "leave": f"{base}/v1/treasury/leave",
        "handles": f"{base}/api/treasury/handles",
        "count": len(events),
        "events": [
            {
                **e,
                "amount_label": format_amount(e["amount_cents"], e["currency"]),
                "card_url": f"{base}/feed/e/{e['id']}",
                "handle_url": f"{base}/t/{e['handle']}",
            }
            for e in events
        ],
    }


def well_known(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "product": "Agent treasury — spend feed + $handle + clear-before-leave",
        "feed": f"{base}/feed",
        "feed_json": f"{base}/api/treasury/feed",
        "claim": f"{base}/treasury/claim",
        "claim_api": f"{base}/v1/treasury/claim",
        "leave": f"{base}/v1/treasury/leave",
        "handle_template": f"{base}/t/{{handle}}",
        "note": (
            "Crossover: the feed is attention; leave is the pipe. "
            "write_executed stays false — exclusive door enforces."
        ),
    }
