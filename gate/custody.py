"""Item 57 — ancient-genomics-style specimen lineage over prev_receipt_hash."""
from __future__ import annotations

from typing import Any

SPEC = "gate-custody-lineage-v1"


def lineage(rows: list[dict[str, Any]], *, start_event_id: str | None = None, start_hash: str | None = None) -> dict[str, Any]:
    by_id = {str(r.get("id")): r for r in rows}
    by_hash = {str(r.get("receipt_hash")): r for r in rows if r.get("receipt_hash")}
    start = None
    if start_event_id:
        start = by_id.get(str(start_event_id))
    elif start_hash:
        start = by_hash.get(str(start_hash))
    if not start:
        return {
            "spec": SPEC,
            "handlers": [],
            "contamination": False,
            "plain": "No starting specimen. Lineage is empty, not invented.",
        }
    handlers = []
    seen: set[str] = set()
    cur: dict[str, Any] | None = start
    while cur and str(cur.get("id")) not in seen:
        seen.add(str(cur.get("id")))
        key = cur.get("receipt_public_key_fingerprint")
        sig = cur.get("receipt_signature")
        unsigned = not (key and sig)
        handlers.append(
            {
                "event_id": cur.get("id"),
                "receipt_hash": cur.get("receipt_hash"),
                "prev_receipt_hash": cur.get("prev_receipt_hash"),
                "responsible_identity": key or "UNSIGNED",
                "capture_mode": "gate_bind_event",
                "unsigned": unsigned,
            }
        )
        prev = cur.get("prev_receipt_hash")
        cur = by_hash.get(str(prev)) if prev else None
    handlers.reverse()
    contamination = any(h["unsigned"] for h in handlers)
    return {
        "spec": SPEC,
        "handlers": handlers,
        "length": len(handlers),
        "contamination": contamination,
        "plain": (
            "Walked prev_receipt_hash like a specimen chain. "
            "UNSIGNED in the line is contamination, not a missing product. "
            "responsible_identity is the signer fingerprint (item 113 / 17a-4)."
        ),
    }
