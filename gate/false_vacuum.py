"""False Vacuum DEAD — cheap LIVE is vacuum decay. CHARGE is the only legal tunneling.

DEAD is a false vacuum that is stable until a costly bubble (CHARGE)
nucleates true LIVE. Soft-yes LIVE is uncatalyzed decay — it eats the
true vacuum around it (skip-clear cascade). The mouth forbids spontaneous
decay. Earth wants 'just this once'. Once is a bubble that does not stop.

Not Earth-side: not change-management. Vacuum stability law.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-false-vacuum-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def nucleate(
    *,
    cheap_live: bool | None = None,
    charge_id: str | None = None,
) -> dict[str, Any]:
    cheap = bool(cheap_live)
    charge = bool((charge_id or "").strip())
    if cheap and not charge:
        posture = "uncatalyzed_decay"
        claim = "spontaneous_live_eats_the_true_vacuum"
    elif charge:
        posture = "legal_bubble"
        claim = "charge_nucleates_true_live"
    else:
        posture = "metastable_hold"
        claim = "dead_false_vacuum_held"
    return {
        "spec": SPEC,
        "name": "False Vacuum DEAD",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "cheap_live": cheap,
        "charge_present": charge,
        "posture": posture,
        "claim": claim,
        "thesis": "Just-this-once LIVE is vacuum decay. CHARGE is the only allowed bubble.",
        "gatekeep": "Proprietary false-vacuum law. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "False Vacuum DEAD",
        "inventor": INVENTOR,
        "example_hold": nucleate(),
        "example_decay": nucleate(cheap_live=True),
        "live": f"{base}/.well-known/false-vacuum.json",
        "metastable": f"{base}/.well-known/metastable.json",
        "their_production": False,
    }
