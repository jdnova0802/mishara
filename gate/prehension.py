"""Prehension Receipt — Whitehead: the receipt prehends the spent world.

Prehension: an actual occasion feels / takes account of other occasions.
A Gate receipt is not a log line — it prehends the hop, the weld, the
inhabitant trail, the restraint inventory membership. Stranger verify is
public prehension. Copycats ship logs that feel nothing.

Gatekeep only to ourselves: Whitehead prehension → receipt as feeling of spend.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-prehension-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def prehend(row: Mapping[str, Any] | None = None) -> dict[str, Any]:
    r = row or {}
    felt = {
        "event_id": bool(r.get("id") or r.get("event_id")),
        "decision": bool(r.get("decision")),
        "receipt_hash": bool(r.get("receipt_hash")),
        "verify_url": bool(r.get("verify_url")),
        "job_id": bool(r.get("job_id")),
    }
    intensity = sum(1 for v in felt.values() if v)
    return {
        "spec": SPEC,
        "name": "Prehension Receipt",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "A.N. Whitehead — Process and Reality; prehension",
            "Gate — receipt as public feeling of the irreversible occasion",
        ],
        "felt": felt,
        "prehension_intensity": intensity,
        "public_prehension": bool(r.get("verify_url")),
        "thesis": "A receipt that cannot be fetched does not prehend. It forgets.",
        "gatekeep": "Proprietary Whitehead framing of receipts. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["prehension"] = prehend(row)
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Prehension Receipt",
        "inventor": INVENTOR,
        "example": prehend(
            {
                "id": "e1",
                "decision": "HALT",
                "receipt_hash": "abc",
                "verify_url": "https://velaru.xyz/verify",
                "job_id": "pc:1",
            }
        ),
        "live": f"{base}/.well-known/prehension.json",
        "custody": f"{base}/.well-known/custody.json",
        "their_production": False,
    }
