"""Item 164 — evidence-head leases instead of the revocation trilemma.

Bitstring is simple/not real-time/group-private. Accumulators are
unlinkable/heavy. This does not magically get all three on a long-lived
credential. It refuses the long-lived credential:

- real-time bound = min(TTL, next evidence-head movement)
- unlinkable = a fresh random lease_id on every refresh, no bit index
- lightweight = one hash check, no holder witness

Issuer liveness is the remaining cost. Stop republishing and the lease dies.
"""
from __future__ import annotations

import hashlib
import json
import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-head-lease-v1"
DEFAULT_TTL_MS = 60_000


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_HEAD_LEASE_PATH") or Path(__file__).resolve().parent / "data" / "head_lease.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "leases": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "leases": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "leases": []}
    data.setdefault("leases", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def catalog() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "bitstring": False,
        "accumulator": False,
        "holder_witness": False,
        "default_ttl_ms": DEFAULT_TTL_MS,
        "leases": _load()["leases"],
        "plain": "Short lease bound to an evidence head. Not a long-lived credential with a revocation list.",
    }


def issue(
    *,
    subject_ref: str,
    head_hash: str,
    ttl_ms: int | None = None,
) -> dict[str, Any]:
    sub = sanitize_mod.strip_agent(subject_ref, limit=200)
    head = (head_hash or "").strip()
    if not sub or not head:
        return {"spec": SPEC, "ok": False, "error": "subject_and_head_required"}
    try:
        ttl = int(ttl_ms) if ttl_ms is not None else DEFAULT_TTL_MS
    except (TypeError, ValueError):
        ttl = 0
    if ttl <= 0:
        return {"spec": SPEC, "ok": False, "error": "ttl_required", "plain": "A lease without a TTL is a credential. This table refuses that."}
    now = _now()
    lease_id = "ls_" + secrets.token_hex(8)
    material = f"{lease_id}:{sub}:{head}:{ttl}"
    rec = {
        "spec": SPEC,
        "ok": True,
        "lease_id": lease_id,
        "prior_lease_id": None,
        "subject_ref": sub,
        "head_hash": head,
        "issued_at": _iso(now),
        "expires_at": _iso(now + timedelta(milliseconds=ttl)),
        "ttl_ms": ttl,
        "killed": False,
        "commitment": hashlib.sha256(material.encode()).hexdigest(),
        "plain": "Fresh id. Dies at TTL or when the evidence head this was bound to is no longer current.",
    }
    store = _load()
    store["leases"].append(rec)
    _save(store)
    return rec


def refresh(*, lease_id: str, head_hash: str, ttl_ms: int | None = None) -> dict[str, Any]:
    store = _load()
    old = next((l for l in store["leases"] if l.get("lease_id") == (lease_id or "").strip()), None)
    if not old:
        return {"spec": SPEC, "ok": False, "error": "lease_not_found"}
    old["killed"] = True
    _save(store)
    nxt = issue(subject_ref=old["subject_ref"], head_hash=head_hash, ttl_ms=ttl_ms if ttl_ms is not None else old.get("ttl_ms"))
    if nxt.get("ok"):
        nxt["prior_lease_id"] = old["lease_id"]
        store = _load()
        row = next((l for l in store["leases"] if l.get("lease_id") == nxt["lease_id"]), None)
        if row:
            row["prior_lease_id"] = old["lease_id"]
            _save(store)
    return nxt


def kill(*, lease_id: str) -> dict[str, Any]:
    store = _load()
    row = next((l for l in store["leases"] if l.get("lease_id") == (lease_id or "").strip()), None)
    if not row:
        return {"spec": SPEC, "ok": False, "error": "lease_not_found"}
    row["killed"] = True
    row["killed_at"] = _iso()
    _save(store)
    return {**row, "ok": True, "plain": "Stop-republish. Verifiers with the current head will fail this id."}


def verify(*, lease_id: str, current_head_hash: str, now: datetime | None = None) -> dict[str, Any]:
    clock = now or _now()
    store = _load()
    row = next((l for l in store["leases"] if l.get("lease_id") == (lease_id or "").strip()), None)
    if not row:
        return {"spec": SPEC, "ok": False, "error": "lease_not_found"}
    if row.get("killed"):
        return {"spec": SPEC, "ok": False, "error": "killed", "plain": "Issuer stopped the lease."}
    if (current_head_hash or "").strip() != row.get("head_hash"):
        return {
            "spec": SPEC,
            "ok": False,
            "error": "head_moved",
            "plain": "Bound to a prior evidence head. Refresh against the current head.",
        }
    exp = datetime.fromisoformat(str(row["expires_at"]).replace("Z", "+00:00"))
    if clock > exp:
        return {"spec": SPEC, "ok": False, "error": "expired", "plain": "TTL elapsed. Real-time here is the lease length, not a bitstring fetch."}
    return {
        "spec": SPEC,
        "ok": True,
        "lease_id": row["lease_id"],
        "subject_ref": row["subject_ref"],
        "plain": "One hash, one TTL, new id on refresh. Not all-three-on-a-durable-credential.",
    }
