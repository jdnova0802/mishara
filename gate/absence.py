"""R2 — proof of non-authorization in a time window.

CT inclusion says a receipt exists. This object says: among public bind
events in [t0, t1], no ALLOW/LIVE for this fuse_id (and optional job_id).
The stranger re-derives from the same list. Not a ZK absence.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

try:
    from gate import evidence_log as evidence_log_mod
except ImportError:
    import evidence_log as evidence_log_mod

SPEC = "gate-absence-v1"
HOT_ALLOW = ("ALLOW", "LIVE", "GO")


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


def prove(
    rows: list[dict[str, Any]],
    *,
    fuse_id: str,
    job_id: str | None = None,
    t0: str,
    t1: str,
) -> dict[str, Any]:
    fuse = (fuse_id or "").strip()
    job = (job_id or "").strip() or None
    start = _parse(t0)
    end = _parse(t1)
    if not fuse or start is None or end is None or end < start:
        return {"spec": SPEC, "ok": False, "error": "window_required", "plain": "Need fuse_id and a closed [t0, t1]."}
    scanned: list[str] = []
    hits: list[dict[str, str]] = []
    for row in rows:
        when = _parse(str(row.get("created_at") or ""))
        if when is None or when < start or when > end:
            continue
        rid = str(row.get("receipt_hash") or row.get("id") or "")
        if rid:
            scanned.append(rid)
        if str(row.get("fuse_id") or "") != fuse:
            continue
        if job and str(row.get("job_id") or "") != job:
            continue
        decision = str(row.get("decision") or "").upper()
        if decision in HOT_ALLOW:
            hits.append(
                {
                    "event_id": str(row.get("id") or ""),
                    "receipt_hash": rid,
                    "decision": decision,
                    "created_at": str(row.get("created_at") or ""),
                }
            )
    scanned_sorted = sorted(set(scanned))
    root = evidence_log_mod.merkle_root(scanned_sorted) if scanned_sorted else evidence_log_mod.EMPTY_LEAF.hex()
    statement = {
        "fuse_id": fuse,
        "job_id": job,
        "t0": start.astimezone(timezone.utc).replace(microsecond=0).isoformat(),
        "t1": end.astimezone(timezone.utc).replace(microsecond=0).isoformat(),
        "scanned_count": len(scanned_sorted),
        "matching_allow": hits,
        "window_root": root,
    }
    digest = hashlib.sha256(json.dumps(statement, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    absent = not hits
    return {
        "spec": SPEC,
        "ok": True,
        "absent": absent,
        "statement": statement,
        "statement_sha256": digest,
        "plain": (
            "No ALLOW/LIVE for this fuse in the window. Recompute from the public bind list."
            if absent
            else "An ALLOW/LIVE sits in the window. Absence fails. The halt did not hold."
        ),
    }
