"""Bind ticket — commit-time authorization for irreversible spend.

Ed25519 signs a receipt after the hop. That is ink. This is the capability:

  A LIVE hop is not a bind grant. The grant is a short-lived, single-use,
  job-bound ticket. After not_after, the hop is a museum.

Lineage (public, not invented here):
- Temporary Authority, Permanent Effects / CommitGuard (2026) — witness must
  still be fresh, causally prior, bound to the same target at commit time
- CapLease (2026) — Issued → redeemed once; semantic replay is not a new grant
- MA-Commit non-decomposability (2026) — separating validation from execution
  violates safety. Hop-then-bind-later is the decomposition.

SPEED: default TTL is 15 seconds. Cached LIVE cannot spend.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import spend_protocol
except ImportError:
    import spend_protocol

SPEC = "gate-bind-ticket-v1"
DEFAULT_TTL = 15


def ttl_seconds() -> int:
    try:
        n = int(os.getenv("GATE_BIND_TICKET_TTL", str(DEFAULT_TTL)))
    except ValueError:
        n = DEFAULT_TTL
    return max(1, min(n, 300))


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def issue(
    *,
    job_id: str,
    fuse_id: str,
    event_id: str,
    receipt_hash: str | None,
    redeem_url: str,
    spend_write: dict | None = None,
) -> dict | None:
    """Mint a bearer ticket. Token is returned once; public receipts never include it.

    Fail closed if there is no spend fingerprint. A job-only ticket is not a print.
    """
    jid = (job_id or "").strip()
    fp = spend_protocol.fingerprint(spend_write)
    if not jid or not fp or not isinstance(spend_write, dict):
        return None
    now = datetime.now(timezone.utc)
    ttl = ttl_seconds()
    ticket_id = str(uuid.uuid4())
    token = secrets.token_urlsafe(32)
    write = {
        "method": spend_write.get("method"),
        "path": spend_write.get("path"),
        "job_id": spend_write.get("job_id") or jid,
        "spend_kind": spend_write.get("spend_kind"),
    }
    body = {
        "spec": SPEC,
        "ticket_id": ticket_id,
        "job_id": jid,
        "fuse_id": fuse_id,
        "event_id": event_id,
        "receipt_hash": receipt_hash,
        "not_before": now.isoformat(),
        "not_after": (now + timedelta(seconds=ttl)).isoformat(),
        "single_use": True,
        "spend": "bind",
        "spend_kind": write["spend_kind"],
        "spend_write": write,
        "spend_fingerprint": fp,
        "ttl_seconds": ttl,
        "stale_hop_cannot_spend": True,
    }
    digest = hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()
    signature = receipt_mod.sign_receipt_hash(digest)
    db.insert_bind_ticket(
        ticket_id=ticket_id,
        job_id=jid,
        fuse_id=fuse_id,
        event_id=event_id,
        receipt_hash=receipt_hash,
        token_hash=hashlib.sha256(token.encode("utf-8")).hexdigest(),
        not_before=body["not_before"],
        not_after=body["not_after"],
        spend_fingerprint=fp,
    )
    public = {
        **body,
        "signature": signature,
        "redeem": redeem_url,
        "token_present": True,
    }
    bearer = {**public, "token": token}
    return {"bearer": bearer, "public": public}


def public_from_bearer(bearer: dict | None) -> dict | None:
    if not isinstance(bearer, dict):
        return None
    out = {k: v for k, v in bearer.items() if k != "token"}
    return out


def redeem(
    *,
    ticket_id: str,
    token: str,
    job_id: str,
    method: str | None = None,
    path: str | None = None,
    spend_fingerprint: str | None = None,
    spend_kind: str | None = None,
) -> dict:
    """Atomic consume. Fail closed on missing, stale, mismatch, replay, or wrong write."""
    now = datetime.now(timezone.utc).isoformat()
    tid = (ticket_id or "").strip()
    tok = (token or "").strip()
    jid = (job_id or "").strip()
    if not tid or not tok or not jid:
        return {
            "ok": False,
            "halt": True,
            "allow_bind": False,
            "reason": "ticket_required",
            "spec": SPEC,
        }
    presented = spend_protocol.presented_write(
        job_id=jid,
        method=method,
        path=path,
        spend_kind=spend_kind,
    )
    if presented is None:
        return {
            "ok": False,
            "halt": True,
            "allow_bind": False,
            "reason": spend_protocol.REASON_REQUIRED,
            "ticket_id": tid,
            "job_id": jid,
            "spec": SPEC,
            "stale_hop_cannot_spend": True,
        }
    presented_fp = spend_protocol.fingerprint(presented)
    claimed = (spend_fingerprint or "").strip()
    if claimed and presented_fp and claimed.lower() != presented_fp.lower():
        return {
            "ok": False,
            "halt": True,
            "allow_bind": False,
            "reason": spend_protocol.REASON_MISMATCH,
            "ticket_id": tid,
            "job_id": jid,
            "spec": SPEC,
            "stale_hop_cannot_spend": True,
        }
    token_hash = hashlib.sha256(tok.encode("utf-8")).hexdigest()
    result = db.consume_bind_ticket(
        ticket_id=tid,
        token_hash=token_hash,
        job_id=jid,
        now=now,
        spend_fingerprint=presented_fp,
    )
    if result.get("ok"):
        return {
            "ok": True,
            "halt": False,
            "allow_bind": True,
            "ticket_id": tid,
            "job_id": jid,
            "consumed_at": now,
            "spec": SPEC,
            "single_use": True,
            "spend_fingerprint": presented_fp,
            "spend_write": presented,
        }
    return {
        "ok": False,
        "halt": True,
        "allow_bind": False,
        "reason": result.get("reason") or "ticket_invalid",
        "ticket_id": tid,
        "job_id": jid,
        "spec": SPEC,
        "stale_hop_cannot_spend": True,
    }


def stamp(plan: dict, *, ticket_public: dict | None, epoch: dict | None, redeem_url: str) -> dict:
    """Commit-time authorization block on the hop response. Not a museum label."""
    plan["commit_time_authorization"] = {
        "spec": "gate-commit-auth-v1",
        "bind_ticket_required": True,
        "spend_fingerprint_required": True,
        "ttl_seconds": ttl_seconds(),
        "stale_hop_cannot_spend": True,
        "single_use": True,
        "non_decomposable": "A hop without a live ticket is not a bind grant.",
        "married_write": spend_protocol.PATH_TEMPLATE,
        "redeem": redeem_url,
        "ticket": ticket_public,
        "epoch": epoch or {"locked": False},
        "lineage": [
            "CommitGuard / commit-time authorization (2026)",
            "CapLease Issued→Consumed (2026)",
            "MA-Commit non-decomposability (2026)",
        ],
    }
    if ticket_public is None and (plan.get("allow_bind") or plan.get("bind_allowed")):
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["commit_time_authorization"]["reason"] = "ticket_unissued"
    return plan


def manifest(public_url: str) -> dict:
    return {
        "spec": SPEC,
        "name": "Bind ticket",
        "greater_than_ed25519": (
            "Signatures prove a hop occurred. Tickets prove the hop is still "
            "allowed to spend, right now, once, for this job and this write."
        ),
        "ttl_seconds": ttl_seconds(),
        "stale_hop_cannot_spend": True,
        "single_use": True,
        "spend_fingerprint_required": True,
        "married_write": spend_protocol.PATH_TEMPLATE,
        "spend_protocol": f"{public_url}/.well-known/spend-protocol.json",
        "redeem": f"{public_url}/v1/pas/bind-ticket/redeem",
        "demo_redeem": f"{public_url}/demo/pas/bind-ticket/redeem",
        "their_production": False,
    }
