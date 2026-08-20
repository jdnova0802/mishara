"""Pre-Net Clearance — gross must pass the mouth before CNS collapses it.

DTCC CNS nets continuous gross into net. Gate's job is earlier: reject or
clear gross obligations at the instruction layer so bad gross never enters
the window. Netting 98% efficiency is worthless if the 2% that slipped
through was skip-clear.

Not cliche: we are not a CCP. We are the gross filter your net assumes exists.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-pre-net-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def admit(
    *,
    mouth_cleared: bool | None = None,
    entered_settlement_window: bool | None = None,
) -> dict[str, Any]:
    cleared = bool(mouth_cleared)
    entered = bool(entered_settlement_window)
    if entered and not cleared:
        posture = "gross_contamination"
        claim = "bad_gross_entered_net_will_hide_it"
    elif cleared and entered:
        posture = "pre_net_cleared"
        claim = "gross_admitted_to_window_after_mouth"
    elif cleared:
        posture = "cleared_not_yet_windowed"
        claim = "ready_for_settlement_obligation"
    else:
        posture = "rejected_at_gross"
        claim = "never_reaches_cns"
    return {
        "spec": SPEC,
        "name": "Pre-Net Clearance",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "DTCC CNS continuous net settlement — gross before net",
            "Gate settlement obligations — only mouth-cleared gross enters",
        ],
        "mouth_cleared": cleared,
        "entered_settlement_window": entered,
        "posture": posture,
        "claim": claim,
        "thesis": "Netting is not a filter. We filter gross. Then you net.",
        "gatekeep": "Proprietary pre-net clearance. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Pre-Net Clearance",
        "inventor": INVENTOR,
        "example_ok": admit(mouth_cleared=True, entered_settlement_window=True),
        "example_bad": admit(mouth_cleared=False, entered_settlement_window=True),
        "live": f"{base}/.well-known/pre-net-clearance.json",
        "settlement": f"{base}/.well-known/settlement.json",
        "distribution": f"{base}/.well-known/distribution.json",
        "their_production": False,
    }
