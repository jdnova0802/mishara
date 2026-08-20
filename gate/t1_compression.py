"""T+1 Compression — mouth removes exception cycles from the settlement clock.

T+1 deletes the overnight excuse. Email confirmation, manual SSI fix, UW
soft-yes, dashboard override — each eats the same-day window. Gate compresses
by making the hop electronic, fail-closed, and receipted before the PAS/CCP
clock: allocation/confirmation discipline without another human queue.

Not cliche 'faster blockchain'. Less exception time, not faster fraud.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-t1-compression-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def budget(
    *,
    manual_exception_path: bool | None = None,
    electronic_hop: bool | None = None,
    receipt_fetchable: bool | None = None,
) -> dict[str, Any]:
    manual = bool(manual_exception_path)
    elec = bool(electronic_hop)
    fetch = bool(receipt_fetchable)
    if manual:
        posture = "clock_eaten"
        claim = "exception_cycle_consumes_t1_budget"
    elif elec and fetch:
        posture = "compressed"
        claim = "hop_and_receipt_same_day_no_email_queue"
    elif elec:
        posture = "partial"
        claim = "electronic_but_not_provable_to_third_party"
    else:
        posture = "unevaluated"
        claim = "no_compression_assay"
    return {
        "spec": SPEC,
        "name": "T+1 Compression",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "DTCC accelerated settlement · EU T+1 roadmap — same-day confirmation discipline",
            "Gate electronic hop + stranger verify — exception time removed",
        ],
        "manual_exception_path": manual,
        "electronic_hop": elec,
        "receipt_fetchable": fetch,
        "posture": posture,
        "claim": claim,
        "thesis": "T+1 does not need faster bad instructions. It needs fewer exception cycles.",
        "gatekeep": "Proprietary T+1 compression doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "T+1 Compression",
        "inventor": INVENTOR,
        "example_compressed": budget(electronic_hop=True, receipt_fetchable=True),
        "example_eaten": budget(manual_exception_path=True),
        "live": f"{base}/.well-known/t1-compression.json",
        "distribution": f"{base}/.well-known/distribution.json",
        "their_production": False,
    }
