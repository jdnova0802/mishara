"""Interlock Ladder — every rung must be true; no jumper wires to LIVE.

Machine safety: interlocks in series. Gate's rungs: exclusive door, fuse
LIVE, parent LIVE, epoch unlocked, exclusion ok, CHARGE for resurrection.
A jumper (admin LIVE, UW approve) around one rung is a lockout tag
removed. Copycats parallelize rungs 'for availability'.

Gatekeep only to ourselves: safety interlocks → series mouth, no jumpers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-interlock-v1"
INVENTOR = "Nisaba LLC / Gate"

RUNGS = (
    "exclusive_door",
    "fuse_live",
    "license_parent_live",
    "epoch_unlocked",
    "exclusion_ok",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ladder(
    *,
    rungs_true: int | None = None,
    jumper: bool | None = None,
    charge_id: str | None = None,
) -> dict[str, Any]:
    n = int(rungs_true) if rungs_true is not None else 0
    jump = bool(jumper)
    charge = bool((charge_id or "").strip())
    total = len(RUNGS)
    if jump:
        posture = "jumper_illegal"
        claim = "lockout_tag_removed"
    elif n < total:
        posture = "open_interlock"
        claim = "series_break_is_halt"
    elif n >= total and charge:
        posture = "interlocks_plus_charge"
        claim = "series_closed_and_witnessed"
    else:
        posture = "rungs_closed_awaiting_charge"
        claim = "interlocks_necessary_not_sufficient_for_live"
    return {
        "spec": SPEC,
        "name": "Interlock Ladder",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Machine-safety interlock chains / LOTO",
            "Gate enabling grip + capability conversion factors",
        ],
        "rungs": list(RUNGS),
        "rungs_true": n,
        "rungs_total": total,
        "jumper": jump,
        "charge_present": charge,
        "posture": posture,
        "claim": claim,
        "thesis": "Rungs are series. Jumpers are how people die — and how skip-clear ships.",
        "gatekeep": "Proprietary interlock-ladder doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Interlock Ladder",
        "inventor": INVENTOR,
        "example_open": ladder(rungs_true=3),
        "example_jumper": ladder(rungs_true=5, jumper=True),
        "live": f"{base}/.well-known/interlock.json",
        "enabling": f"{base}/.well-known/enabling.json",
        "their_production": False,
    }
