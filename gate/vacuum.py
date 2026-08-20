"""Vacuum Integrity — fail-closed as vacuum: any leak is HALT, not 'degraded LIVE'.

Alien craft run vacuum. A pinhole is not a yellow KPI. Gate's mouth is
vacuum hardware: timeout, 5xx, missing fuse, missing parent → HALT.
Degraded-mode LIVE is atmosphere loss. Copycats 'fail open for UX'.

Gatekeep only to ourselves: vacuum systems → fail-closed as integrity, not mood.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-vacuum-v1"
INVENTOR = "Nisaba LLC / Gate"

LEAKS = (
    "timeout_as_live",
    "unreachable_as_live",
    "5xx_as_live",
    "missing_fuse_as_live",
    "degraded_mode_allow",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def integrity(*, leak: str | None = None, fail_closed: bool | None = None) -> dict[str, Any]:
    l = (leak or "").strip().lower()
    fc = True if fail_closed is None else bool(fail_closed)
    if l in LEAKS or l.endswith("_as_live"):
        posture = "vacuum_loss"
        claim = "leak_treated_as_atmosphere"
    elif fc and not l:
        posture = "hard_vacuum"
        claim = "unknown_and_error_are_halt"
    else:
        posture = "unevaluated"
        claim = "insufficient_seal_data"
    return {
        "spec": SPEC,
        "name": "Vacuum Integrity",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Spacecraft vacuum / pressure integrity — leaks are not yellow",
            "Gate fail-closed — UNREACHABLE is never LIVE",
        ],
        "leaks": list(LEAKS),
        "leak": l or None,
        "fail_closed": fc,
        "posture": posture,
        "claim": claim,
        "thesis": "Fail-open is hull breach. HALT is the seal.",
        "gatekeep": "Proprietary vacuum-integrity doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Vacuum Integrity",
        "inventor": INVENTOR,
        "example_seal": integrity(fail_closed=True),
        "example_leak": integrity(leak="timeout_as_live"),
        "live": f"{base}/.well-known/vacuum.json",
        "xenohardware": f"{base}/.well-known/xenohardware.json",
        "their_production": False,
    }
