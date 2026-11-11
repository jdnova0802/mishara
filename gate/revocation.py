"""Item 157 — revocation registry schema.

Mechanism (bitstring_status_list vs accumulator_witness) is stored,
not executed. Checking a bit or verifying a witness is a second build
after that choice. Status here is the local recorded current_status.
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

SPEC = "gate-revocation-v1"
MECHANISMS = ("bitstring_status_list", "accumulator_witness")
PURPOSES = ("revocation", "suspension")
ATTESTATION_TYPES = (
    "eidas_seal",
    "transparency_log_entry",
    "media_provenance",
    "counterparty_directory_entry",
)
STATUSES = ("valid", "revoked", "suspended")
DEFAULT_REFRESH_TTL_MS = 86_400_000  # Nisaba default; W3C WD has none.


def _iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_REVOCATION_PATH") or Path(__file__).resolve().parent / "data" / "revocation.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "registries": [], "entries": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "registries": [], "entries": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "registries": [], "entries": []}
    data.setdefault("registries", [])
    data.setdefault("entries", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def catalog() -> dict[str, Any]:
    store = _load()
    return {
        "spec": SPEC,
        "mechanism_executed": False,
        "w3c_bitstring_is_working_draft": True,
        "real_time": False,
        "default_refresh_ttl_ms": DEFAULT_REFRESH_TTL_MS,
        "registries": store["registries"],
        "entries": store["entries"],
        "plain": "Schema only. Bit lookup and accumulator witness are not implemented until the mechanism is picked.",
    }


def open_registry(
    *,
    issuer_org_id: str,
    mechanism: str,
    purpose: str = "revocation",
    status_list_url: str | None = None,
    accumulator_state_ref: str | None = None,
) -> dict[str, Any]:
    mech = (mechanism or "").strip()
    if mech not in MECHANISMS:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "mechanism_unknown",
            "plain": "bitstring_status_list or accumulator_witness. Pick one before check logic.",
        }
    purpose_n = (purpose or "").strip()
    if purpose_n not in PURPOSES:
        return {"spec": SPEC, "ok": False, "error": "purpose_unknown"}
    org = sanitize_mod.strip_agent(issuer_org_id, limit=200)
    if not org:
        return {"spec": SPEC, "ok": False, "error": "issuer_required"}
    rec = {
        "spec": SPEC,
        "ok": True,
        "registry_id": "rr_" + uuid.uuid4().hex[:12],
        "issuer_org_id": org,
        "mechanism": mech,
        "status_list_url": (status_list_url or "").strip() or None,
        "accumulator_state_ref": (accumulator_state_ref or "").strip() or None,
        "purpose": purpose_n,
        "created_at": _iso(),
        "check_logic_built": False,
        "plain": "Registry recorded. No bit was fetched. No witness was verified.",
    }
    store = _load()
    store["registries"].append(rec)
    _save(store)
    return rec


def track(
    *,
    registry_id: str,
    attestation_type: str,
    attestation_ref_id: str,
    status_list_index: int | None = None,
    refresh_ttl_ms: int | None = None,
) -> dict[str, Any]:
    kind = (attestation_type or "").strip()
    if kind not in ATTESTATION_TYPES:
        return {"spec": SPEC, "ok": False, "error": "attestation_type_unknown"}
    ref = (attestation_ref_id or "").strip()
    if not ref:
        return {"spec": SPEC, "ok": False, "error": "attestation_ref_required"}
    store = _load()
    reg = next((r for r in store["registries"] if r.get("registry_id") == (registry_id or "").strip()), None)
    if not reg:
        return {"spec": SPEC, "ok": False, "error": "registry_not_found"}
    ttl = DEFAULT_REFRESH_TTL_MS if refresh_ttl_ms is None else int(refresh_ttl_ms)
    rec = {
        "spec": SPEC,
        "ok": True,
        "entry_id": "st_" + uuid.uuid4().hex[:12],
        "attestation_type": kind,
        "attestation_ref_id": ref,
        "registry_id": reg["registry_id"],
        "status_list_index": status_list_index,
        "current_status": "valid",
        "status_changed_at": _iso(),
        "refresh_ttl_ms": ttl,
        "plain": "Tracked as valid until a named status change. Freshness is issuer-chosen, not sub-second.",
    }
    store["entries"].append(rec)
    _save(store)
    return rec


def set_status(*, entry_id: str, current_status: str) -> dict[str, Any]:
    st = (current_status or "").strip()
    if st not in STATUSES:
        return {"spec": SPEC, "ok": False, "error": "status_unknown", "plain": "valid, revoked, or suspended."}
    store = _load()
    row = next((e for e in store["entries"] if e.get("entry_id") == (entry_id or "").strip()), None)
    if not row:
        return {"spec": SPEC, "ok": False, "error": "entry_not_found"}
    row["current_status"] = st
    row["status_changed_at"] = _iso()
    row["plain"] = "Local status written. Bitstring/accumulator check is still unbuilt."
    _save(store)
    return {**row, "ok": True}


def lookup(*, attestation_ref_id: str) -> dict[str, Any]:
    ref = (attestation_ref_id or "").strip()
    store = _load()
    hits = [e for e in store["entries"] if e.get("attestation_ref_id") == ref]
    return {
        "spec": SPEC,
        "ok": True,
        "attestation_ref_id": ref,
        "entries": hits,
        "mechanism_executed": False,
        "plain": "Recorded status only. Not a live bitstring fetch.",
    }
