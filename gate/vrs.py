"""Item 155 — verification router for cross-org shared_counterparty.

DSCSA VRS pattern: a phone book, not a shared ledger. An empty
directory is a valid, honest state. Confirmed/denied is the
responder's discretion; this module only routes the question.
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

SPEC = "gate-vrs-v1"
EDGE_SCOPE = ("shared_counterparty",)
RESPONSES = ("confirmed", "denied", "no_answer")


def _iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_VRS_PATH") or Path(__file__).resolve().parent / "data" / "vrs.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "directory": [], "requests": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "directory": [], "requests": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "directory": [], "requests": []}
    data.setdefault("directory", [])
    data.setdefault("requests", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def catalog() -> dict[str, Any]:
    store = _load()
    empty = not store["directory"]
    return {
        "spec": SPEC,
        "directory": store["directory"],
        "requests": store["requests"],
        "empty_directory_is_valid": True,
        "empty": empty,
        "plain": (
            "No counterparties registered. Empty directory, not a hidden hub."
            if empty
            else "Lookup directory only. It does not answer on a counterparty's behalf."
        ),
    }


def register(
    *,
    operator_org_id: str,
    responder_endpoint: str,
    verification_scope: list[str] | None = None,
) -> dict[str, Any]:
    org = sanitize_mod.strip_agent(operator_org_id, limit=200)
    endpoint = (responder_endpoint or "").strip()
    if not org or not endpoint:
        return {"spec": SPEC, "ok": False, "error": "fields_required", "plain": "Need operator_org_id and responder_endpoint."}
    scope = [s for s in (verification_scope or list(EDGE_SCOPE)) if s in EDGE_SCOPE]
    if not scope:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "scope_unsupported",
            "plain": "This router answers shared_counterparty only.",
        }
    rec = {
        "spec": SPEC,
        "ok": True,
        "directory_id": "dir_" + uuid.uuid4().hex[:12],
        "operator_org_id": org,
        "responder_endpoint": endpoint,
        "verification_scope": scope,
        "registered_at": _iso(),
        "plain": "Routable. This is not a merged ledger.",
    }
    store = _load()
    store["directory"].append(rec)
    _save(store)
    return rec


def request_verify(
    *,
    requesting_receipt_id: str,
    target_org_id: str,
    edge_type: str = "shared_counterparty",
) -> dict[str, Any]:
    rid = (requesting_receipt_id or "").strip()
    org = sanitize_mod.strip_agent(target_org_id, limit=200)
    et = (edge_type or "").strip()
    if et not in EDGE_SCOPE:
        return {"spec": SPEC, "ok": False, "error": "edge_type_unsupported", "plain": "shared_counterparty only."}
    if not rid or not org:
        return {"spec": SPEC, "ok": False, "error": "fields_required", "plain": "Need a receipt and a target org."}
    store = _load()
    entry = next((d for d in store["directory"] if d.get("operator_org_id") == org), None)
    rec = {
        "spec": SPEC,
        "ok": True,
        "request_id": "vr_" + uuid.uuid4().hex[:12],
        "requesting_receipt_id": rid,
        "target_org_id": org,
        "edge_type": et,
        "routed_to": entry["directory_id"] if entry else None,
        "response": "no_answer",
        "responded_at": None,
        "plain": (
            "No directory entry. Empty book, not a denial."
            if entry is None
            else "Routed. Waiting on the responder; this layer will not invent confirmed."
        ),
    }
    store["requests"].append(rec)
    _save(store)
    return rec


def answer(*, request_id: str, response: str) -> dict[str, Any]:
    resp = (response or "").strip()
    if resp not in RESPONSES:
        return {"spec": SPEC, "ok": False, "error": "response_unknown", "plain": "confirmed, denied, or no_answer."}
    store = _load()
    row = next((r for r in store["requests"] if r.get("request_id") == (request_id or "").strip()), None)
    if not row:
        return {"spec": SPEC, "ok": False, "error": "request_not_found", "plain": "Unknown request_id."}
    if not row.get("routed_to"):
        return {
            "spec": SPEC,
            "ok": False,
            "error": "not_routed",
            "plain": "No directory entry. A missing org cannot confirm.",
        }
    row["response"] = resp
    row["responded_at"] = _iso()
    row["plain"] = "Responder discretion recorded. Routing did not force a consistent schema on them."
    _save(store)
    return {**row, "ok": True}
