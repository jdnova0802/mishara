"""HALT Cemetery — admin-undeletable tombstones for epoch-locked jobs.

Competitors revoke blocks. Gate leaves headstones strangers can audit.
A HALT that stuck under epoch lock is carved into the cemetery — not a log line.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

try:
    from gate import db
except ImportError:
    import db

SPEC = "gate-halt-cemetery-v1"
INVENTION = "HALT Cemetery"
FAMILY = "competitive-response"


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def carve(
    *,
    job_id: str,
    event_id: str | int,
    decision: str,
    reason: str | None = None,
    epoch: dict | None = None,
    verify_url: str | None = None,
    receipt_hash: str | None = None,
    created_at: str | None = None,
) -> dict[str, Any]:
    """Carve a tombstone. Append-only semantics — no admin delete in spec."""
    jid = (job_id or "").strip()
    dec = (decision or "").upper()
    ep = epoch if isinstance(epoch, dict) else {}
    body = {
        "job_id": jid,
        "event_id": event_id,
        "decision": dec,
        "reason": (reason or ep.get("reason") or "").strip() or None,
        "epoch_locked": bool(ep.get("locked")),
        "prior_event_id": ep.get("prior_event_id"),
        "verify_url": verify_url,
        "receipt_hash": receipt_hash,
        "created_at": created_at,
    }
    stone_id = hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()[:24]
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "stone_id": stone_id,
        "tombstone": body,
        "admin_deletable": False,
        "resurrect_path": "velaru_charge_only",
        "rule": "Epoch HALT leaves a headstone. Quiet delete is forged history.",
    }


def from_event(row: dict | None, epoch: dict | None = None) -> dict[str, Any] | None:
    if not isinstance(row, dict):
        return None
    dec = (row.get("decision") or "").upper()
    if dec not in ("HALT", "BLOCK"):
        return None
    ep = epoch if isinstance(epoch, dict) else {}
    locked = bool(ep.get("locked")) or dec in ("HALT", "BLOCK")
    if not locked and dec != "BLOCK":
        return None
    return carve(
        job_id=str(row.get("job_id") or ""),
        event_id=row.get("id"),
        decision=dec,
        reason=row.get("reason"),
        epoch=ep,
        verify_url=row.get("verify_url"),
        receipt_hash=row.get("receipt_hash"),
        created_at=row.get("created_at"),
    )


def attach(plan: dict, *, row: dict | None = None, epoch: dict | None = None) -> dict:
    ep = epoch if isinstance(epoch, dict) else plan.get("epoch")
    stone = from_event(row, ep)
    if stone:
        plan["halt_cemetery"] = stone
    elif plan.get("halt") or (plan.get("decision") or "").upper() in ("HALT", "BLOCK"):
        stone = carve(
            job_id=str(plan.get("job_id") or ""),
            event_id=plan.get("event_id") or "pending",
            decision=str(plan.get("decision") or "HALT"),
            reason=plan.get("reason"),
            epoch=ep if isinstance(ep, dict) else {},
            verify_url=plan.get("verify_url"),
            receipt_hash=plan.get("receipt_hash"),
        )
        plan["halt_cemetery"] = stone
    return plan


def list_stones(*, job_id: str | None = None, limit: int = 50) -> dict[str, Any]:
    lim = max(1, min(int(limit or 50), 500))
    rows = db.list_bind_events(None, limit=lim * 3)
    stones: list[dict] = []
    for row in rows:
        dec = (row.get("decision") or "").upper()
        if dec not in ("HALT", "BLOCK"):
            continue
        if job_id and (row.get("job_id") or "").strip() != job_id.strip():
            continue
        stone = from_event(row, {"locked": dec == "HALT", "reason": row.get("reason")})
        if stone:
            stones.append(stone)
        if len(stones) >= lim:
            break
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "count": len(stones),
        "stones": stones,
        "admin_deletable": False,
        "vs_survey": "Operator-revocable blocks elsewhere; headstones stay.",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Epoch HALT tombstones — admin cannot quietly erase a stuck job.",
        "demo": f"GET {base}/demo/pas/halt-cemetery",
        "lookup": f"GET {base}/demo/pas/halt-cemetery?job_id={{job_id}}",
        "well_known": f"{base}/.well-known/halt-cemetery.json",
        "pairs_with": "Epoch lock · Charge Bride · Refuse Ledger",
        "posture": "Stranger-auditable permanence. Not a delete API.",
    }
