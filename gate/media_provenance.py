"""Item 151 — C2PA media provenance on agent-submitted evidence.

A receipt hash does not prove the attached image/video/audio. Soft nulls
when no manifest exists. This mouth does not invent a CV model or run a
local c2pa-rs binary.
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

SPEC = "gate-media-provenance-v1"
STANDARD = "C2PA"


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(
        os.getenv("GATE_MEDIA_PROVENANCE_PATH")
        or Path(__file__).resolve().parent / "data" / "media_provenance.json"
    )


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "checks": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "checks": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "checks": []}
    data.setdefault("checks", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def _tri(value: Any) -> bool | None:
    if value is True or value is False:
        return value
    return None


def list_checks() -> list[dict[str, Any]]:
    return list(_load().get("checks") or [])


def check(
    *,
    receipt_id: str,
    media_hash: str,
    c2pa_manifest_present: Any = False,
    c2pa_signature_valid: Any = None,
    issuing_cert_chain_trusted: Any = None,
    ai_involvement_disclosed: Any = None,
    hard_binding_intact: Any = None,
) -> dict[str, Any]:
    rid = sanitize_mod.strip_agent(receipt_id, limit=200)
    mhash = (media_hash or "").strip().lower()
    if not rid or not mhash:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "fields_required",
            "plain": "Need the receipt this file is attached to and a hash of the file itself.",
        }
    present = bool(c2pa_manifest_present)
    if not present:
        rec = {
            "spec": SPEC,
            "ok": True,
            "standard": STANDARD,
            "check_id": "c2pa_" + uuid.uuid4().hex[:12],
            "receipt_id": rid,
            "media_hash": mhash,
            "c2pa_manifest_present": False,
            "c2pa_signature_valid": None,
            "issuing_cert_chain_trusted": None,
            "ai_involvement_disclosed": None,
            "hard_binding_intact": None,
            "checked_at": _iso(),
            "plain": "No C2PA manifest. Signature, cert, AI-disclosure, and hard-binding stay null. Absence is not a CV score.",
        }
        store = _load()
        store["checks"].append(rec)
        _save(store)
        return rec
    rec = {
        "spec": SPEC,
        "ok": True,
        "standard": STANDARD,
        "check_id": "c2pa_" + uuid.uuid4().hex[:12],
        "receipt_id": rid,
        "media_hash": mhash,
        "c2pa_manifest_present": True,
        "c2pa_signature_valid": _tri(c2pa_signature_valid),
        "issuing_cert_chain_trusted": _tri(issuing_cert_chain_trusted),
        "ai_involvement_disclosed": _tri(ai_involvement_disclosed),
        "hard_binding_intact": _tri(hard_binding_intact),
        "checked_at": _iso(),
        "plain": "Manifest present. Fields are recorded from the verifier, not invented here. No CV model.",
    }
    store = _load()
    store["checks"].append(rec)
    _save(store)
    return rec
