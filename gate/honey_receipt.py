"""Item 145 — canary receipts on public surfaces.

Explicitly fake. real_receipt_id is always null. Never counted in CDPI,
calibration, or anomaly. Distinct from gate-bypass-canary-v1 (spend skip).
No legitimate agent has a reason to query one.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-canary-receipt-v1"
BYPASS_SPEC = "gate-bypass-canary-v1"
DISGUISES = ("near_threshold_case", "high_value_target", "weak_operator")
METHODS = ("verify_api", "link_graph_query", "leaderboard_lookup", "threshold_curve")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_HONEY_PATH") or Path(__file__).resolve().parent / "data" / "honey_receipts.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "canaries": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "canaries": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "canaries": []}
    data.setdefault("canaries", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def list_canaries() -> list[dict[str, Any]]:
    return list(_load().get("canaries") or [])


def get(canary_id: str) -> dict[str, Any] | None:
    cid = (canary_id or "").strip()
    for row in list_canaries():
        if row.get("canary_id") == cid:
            return row
    return None


def plant(*, disguised_as: str) -> dict[str, Any]:
    kind = (disguised_as or "").strip()
    if kind not in DISGUISES:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "disguise_unknown",
            "allowed": list(DISGUISES),
            "plain": "Plant a named decoy. This is not a real receipt.",
        }
    rec = {
        "spec": SPEC,
        "ok": True,
        "canary_id": "canary_" + uuid.uuid4().hex[:12],
        "disguised_as": kind,
        "real_receipt_id": None,
        "trigger_log": [],
        "tripped": False,
        "tripped_at": None,
        "never_counted_in_scores": True,
        "not_bypass_canary": True,
        "bypass_spec": BYPASS_SPEC,
        "plain": "Decoy. Querying it is hunting the boundary. Never a score input.",
    }
    store = _load()
    store["canaries"].append(rec)
    _save(store)
    return rec


def probe(
    *,
    canary_id: str,
    accessed_by: str,
    access_method: str,
) -> dict[str, Any]:
    method = (access_method or "").strip()
    if method not in METHODS:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "method_unknown",
            "allowed": list(METHODS),
            "plain": "verify_api, link_graph_query, leaderboard_lookup, or threshold_curve.",
        }
    store = _load()
    row = next((c for c in store["canaries"] if c.get("canary_id") == (canary_id or "").strip()), None)
    if not row:
        return {"spec": SPEC, "ok": False, "error": "canary_not_found", "plain": "Unknown canary_id."}
    who = sanitize_mod.strip_agent(accessed_by, limit=200) or "anonymous"
    hit = {
        "accessed_by": who,
        "accessed_at": _iso(),
        "access_method": method,
    }
    row.setdefault("trigger_log", []).append(hit)
    row["tripped"] = True
    row["tripped_at"] = hit["accessed_at"]
    row["real_receipt_id"] = None
    row["never_counted_in_scores"] = True
    row["plain"] = "Tripped. Not counted in CDPI, calibration, or anomaly."
    _save(store)
    return {**row, "ok": True}
