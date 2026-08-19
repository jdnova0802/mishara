"""Optional counterpart fingerprint on the same bind ticket.

Not a second married write. If the hop names a counterpart, the ticket
binds to that fingerprint too. Redeem must present the same counterpart.
Omit the fields and the scanner behaves as it does today.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

SPEC = "gate-counterpart-v1"
REASON_REQUIRED = "counterpart_id_required"
REASON_MISMATCH = "counterpart_mismatch"
KEYS = ("counterpart_id", "counterpart_kind", "counterpart_path", "counterpart_method")


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def normalize_id(raw) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip()[:128]
    return s or None


def _token(raw) -> str:
    return (str(raw).strip()[:128] if raw is not None else "")


def write(
    *,
    counterpart_id: str,
    counterpart_kind: str | None = None,
    counterpart_path: str | None = None,
    counterpart_method: str | None = None,
) -> dict:
    return {
        "counterpart_id": counterpart_id,
        "counterpart_kind": _token(counterpart_kind),
        "counterpart_path": _token(counterpart_path),
        "counterpart_method": _token(counterpart_method).upper(),
    }


def fingerprint(write_obj: dict | None) -> str | None:
    if not isinstance(write_obj, dict):
        return None
    cid = normalize_id(write_obj.get("counterpart_id"))
    if not cid:
        return None
    body = write(
        counterpart_id=cid,
        counterpart_kind=write_obj.get("counterpart_kind"),
        counterpart_path=write_obj.get("counterpart_path"),
        counterpart_method=write_obj.get("counterpart_method"),
    )
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


def parse(body: dict | None) -> dict:
    """Omitted → not fused. Partial (fields without counterpart_id) → fail closed."""
    src = body if isinstance(body, dict) else {}
    present = any(_token(src.get(k)) for k in KEYS)
    if not present:
        return {"ok": True, "fused": False, "fingerprint": None, "write": None}
    cid = normalize_id(src.get("counterpart_id"))
    if not cid:
        return {"ok": False, "fused": True, "reason": REASON_REQUIRED, "fingerprint": None, "write": None}
    obj = write(
        counterpart_id=cid,
        counterpart_kind=src.get("counterpart_kind"),
        counterpart_path=src.get("counterpart_path"),
        counterpart_method=src.get("counterpart_method"),
    )
    return {"ok": True, "fused": True, "fingerprint": fingerprint(obj), "write": obj}


def spec(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Counterpart fingerprint",
        "what": "Optional second fingerprint on the same ticket. Not a second bind-only write.",
        "not": [
            "a second married spend path",
            "PII",
            "license_number",
        ],
        "optional_pas_keys": list(KEYS),
        "omit": "No counterpart fields → current scanner behavior.",
        "partial": "Any counterpart field without counterpart_id → no print.",
        "redeem": "If the ticket carries counterpart_fingerprint, redeem must present the same counterpart. Mismatch does not consume the ticket.",
        "fingerprint": {
            "alg": "sha256",
            "over": list(KEYS),
            "canonical_json": "sort_keys, separators=(',', ':')",
        },
        "married_write": "POST /job/v1/jobs/{job_id}/bind-only",
        "license_fuse": f"{base}/.well-known/license-fuse.json",
        "their_production": False,
    }
