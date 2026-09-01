"""PvP may — permission versus permission.

CLS settled two money legs in one window or neither.
Nobody has settled two *permissions* in one SI second or neither.

First in human history: both named throats redeem in the shared UTC now,
or no ticket is consumed. Immobilizes may (CSD). Pairs may (CLS).
Recuses the mouth from the commercial outcome (Swiss).

Not a second write. Not a second sibling. Solo redeem is blocked while
the window is OPEN/ARMED.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import command_radiation
except ImportError:
    import command_radiation

try:
    from gate import spend_protocol
except ImportError:
    import spend_protocol

try:
    from gate import named_may as named_may_mod
except ImportError:
    import named_may as named_may_mod

try:
    from gate import qic as qic_mod
except ImportError:
    import qic as qic_mod

SPEC = "gate-pvp-may-v1"
REASON_PAIR = "pvp_pair_required"
REASON_WINDOW = "pvp_window_required"
REASON_SIDE = "pvp_side_unknown"
REASON_SKEW = "pvp_counterpart_now_skew"
REASON_ONE = "pvp_waiting_on_counterpart"


def _halt(reason: str, **extra) -> dict:
    out = {
        "ok": False,
        "halt": True,
        "radiated": False,
        "settled": False,
        "reason": reason,
        "spec": SPEC,
        "first_in_history": True,
    }
    out.update(extra)
    return out


def locked(ticket_id: str) -> dict | None:
    return db.pvp_lock_for_ticket(ticket_id)


def open_window(
    *,
    side_a_ticket: str,
    side_b_ticket: str,
    side_a_job: str,
    side_b_job: str,
) -> dict:
    a = (side_a_ticket or "").strip()
    b = (side_b_ticket or "").strip()
    ja = (side_a_job or "").strip()
    jb = (side_b_job or "").strip()
    if not a or not b or a == b or not ja or not jb:
        return _halt("pvp_sides_required")
    ta = db.get_bind_ticket(a)
    tb = db.get_bind_ticket(b)
    if not ta or not tb:
        return _halt("ticket_not_found")
    if ta.get("consumed_at") or tb.get("consumed_at"):
        return _halt("ticket_replay")
    if locked(a) or locked(b):
        return _halt("pvp_already_immobilized")
    wid = f"pvp_{uuid.uuid4().hex[:20]}"
    db.pvp_open(
        window_id=wid,
        side_a_ticket=a,
        side_b_ticket=b,
        side_a_job=ja,
        side_b_job=jb,
    )
    return {
        "ok": True,
        "spec": SPEC,
        "window_id": wid,
        "state": "OPEN",
        "immobilized": [a, b],
        "first_in_history": True,
        "what": "Two mays immobilized. Neither can radiate alone. Both now, or neither.",
    }


def _side_of(window: dict, ticket_id: str) -> str | None:
    if ticket_id == window.get("side_a_ticket"):
        return "a"
    if ticket_id == window.get("side_b_ticket"):
        return "b"
    return None


def _eligible(
    *,
    ticket_id: str,
    token: str,
    job_id: str,
    method: str | None,
    path: str | None,
    now: str | None,
    holder_id: str | None,
    server_now: datetime,
) -> dict:
    clock = command_radiation.check_now(now, server=server_now)
    if not clock.get("ok"):
        return _halt(clock.get("reason") or command_radiation.REASON_NOW_REQUIRED, command_radiation=clock)
    presented = spend_protocol.presented_write(job_id=job_id, method=method, path=path)
    if presented is None:
        return _halt(spend_protocol.REASON_REQUIRED)
    row = db.get_bind_ticket(ticket_id)
    if not row:
        return _halt("ticket_not_found")
    if row.get("job_id") != job_id:
        return _halt("ticket_job_mismatch")
    held = named_may_mod.check(
        issued_holder=(row.get("holder_id") or None),
        presented_holder=holder_id,
    )
    if not held.get("ok"):
        return _halt(held.get("reason") or named_may_mod.REASON_REQUIRED, named_may=held)
    token_hash = hashlib.sha256((token or "").encode("utf-8")).hexdigest()
    if row.get("token_hash") != token_hash:
        return _halt("ticket_token_mismatch")
    return {
        "ok": True,
        "token_hash": token_hash,
        "spend_fingerprint": spend_protocol.fingerprint(presented),
        "clock": clock,
        "presented": presented,
    }


def offer(
    *,
    window_id: str,
    ticket_id: str,
    token: str,
    job_id: str,
    method: str | None = None,
    path: str | None = None,
    now: str | None = None,
    holder_id: str | None = None,
) -> dict:
    """Present one throat. When the other presents in the same now, both consume."""
    server_now = datetime.now(timezone.utc)
    wid = (window_id or "").strip()
    tid = (ticket_id or "").strip()
    jid = (job_id or "").strip()
    window = db.pvp_get(wid)
    if not window:
        return _halt(REASON_WINDOW)
    if window.get("state") == "SETTLED":
        return _halt("pvp_already_settled")
    if window.get("state") == "VOID":
        return _halt("pvp_void")
    side = _side_of(window, tid)
    if not side:
        return _halt(REASON_SIDE)
    expected_job = window["side_a_job"] if side == "a" else window["side_b_job"]
    if jid != expected_job:
        return _halt("ticket_job_mismatch")
    elig = _eligible(
        ticket_id=tid,
        token=token,
        job_id=jid,
        method=method,
        path=path,
        now=now,
        holder_id=holder_id,
        server_now=server_now,
    )
    if not elig.get("ok"):
        return elig
    offered = server_now.isoformat()
    window = db.pvp_record_offer(
        window_id=wid,
        side=side,
        offered_at=offered,
        presented_now=(now or "").strip(),
    )
    other_now = window.get("side_b_now") if side == "a" else window.get("side_a_now")
    other_off = window.get("side_b_offered_at") if side == "a" else window.get("side_a_offered_at")
    if not other_off or not other_now:
        return {
            "ok": True,
            "halt": False,
            "radiated": False,
            "settled": False,
            "state": "ARMED",
            "reason": REASON_ONE,
            "window_id": wid,
            "side": side,
            "spec": SPEC,
            "first_in_history": True,
            "immobilized": True,
        }
    other_clock = command_radiation.check_now(other_now, server=server_now)
    if not other_clock.get("ok"):
        db.pvp_void(window_id=wid, reason=REASON_SKEW)
        return _halt(REASON_SKEW, window_id=wid)
    this_dt = command_radiation.parse_utc(now)
    other_dt = command_radiation.parse_utc(other_now)
    skew = command_radiation.max_skew_seconds()
    if this_dt is None or other_dt is None or abs((this_dt - other_dt).total_seconds()) > skew:
        db.pvp_void(window_id=wid, reason=REASON_SKEW)
        return _halt(REASON_SKEW, window_id=wid)

    a_row = db.get_bind_ticket(window["side_a_ticket"])
    b_row = db.get_bind_ticket(window["side_b_ticket"])
    if not a_row or not b_row:
        return _halt("ticket_not_found", window_id=wid)
    # The offering side has a live token; the waiting side was already eligibility-checked
    # at offer time. Consume using stored token hashes (already verified then).
    a_hash = a_row["token_hash"]
    b_hash = b_row["token_hash"]
    a_fp = (a_row.get("spend_fingerprint") or "").strip() or None
    b_fp = (b_row.get("spend_fingerprint") or "").strip() or None
    result = db.pvp_settle(
        window_id=wid,
        now=offered,
        a_ticket=window["side_a_ticket"],
        a_token_hash=a_hash,
        a_job=window["side_a_job"],
        a_spend=a_fp,
        b_ticket=window["side_b_ticket"],
        b_token_hash=b_hash,
        b_job=window["side_b_job"],
        b_spend=b_fp,
    )
    if not result.get("ok"):
        return _halt(result.get("reason") or "pvp_atomic_abort", window_id=wid)
    return {
        "ok": True,
        "halt": False,
        "radiated": True,
        "settled": True,
        "state": "SETTLED",
        "window_id": wid,
        "spec": SPEC,
        "first_in_history": True,
        "qic": [
            qic_mod.stamp_event(job_id=window["side_a_job"], ticket_id=window["side_a_ticket"]),
            qic_mod.stamp_event(job_id=window["side_b_job"], ticket_id=window["side_b_ticket"]),
        ],
        "what": "Both throats redeemed in one now. Neither could have spent alone.",
    }


def spec(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "PvP may — permission versus permission",
        "first_in_history": True,
        "comps": {
            "CLS": "two money legs or neither — here two mays or neither",
            "DTCC_CSD": "immobilize the instrument until delivery",
            "Swiss": "the mouth does not take the commercial side",
            "Vienna": "the act is not in force until both throats have spoken in one now",
        },
        "empty_before": (
            "Multisig spends one UTXO. Counterpart matching is a fingerprint. "
            "Nobody consumed two permissions atomically in one SI second."
        ),
        "open": f"POST {base}/demo/pas/pvp/open",
        "offer": f"POST {base}/demo/pas/pvp/offer",
        "solo_redeem_while_immobilized": REASON_PAIR,
        "their_production": False,
    }
