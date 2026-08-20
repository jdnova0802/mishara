"""CAP of Spend — you cannot have skip-clear Availability and LIVE Consistency.

Brewer CAP: pick two of consistency, availability, partition tolerance.
Gate's spend CAP: under partition (PAS unreachable, epoch lock, parent
DEAD), you cannot stay Available for bind AND Consistent with LIVE.
Fail-closed chooses consistency: HALT. Copycats choose availability and
call timeout LIVE.

Gatekeep only to ourselves: CAP theorem → HALT is the consistency choice.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-cap-spend-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def pick(
    *,
    partitioned: bool | None = None,
    allow_on_timeout: bool | None = None,
    decision: str | None = None,
) -> dict[str, Any]:
    part = bool(partitioned)
    avail = bool(allow_on_timeout)
    d = (decision or "").upper()
    if part and avail and d == "ALLOW":
        posture = "ap_inconsistent"
        claim = "availability_chose_skip_clear_over_live_consistency"
    elif part and d in ("HALT", "BLOCK"):
        posture = "cp_consistent"
        claim = "halt_preserves_live_consistency_under_partition"
    elif not part:
        posture = "no_partition"
        claim = "cap_not_forced"
    else:
        posture = "unevaluated"
        claim = "insufficient_cap_data"
    return {
        "spec": SPEC,
        "name": "CAP of Spend",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Brewer CAP theorem — C vs A under partition",
            "Gate vacuum / NMI — UNREACHABLE is never LIVE",
        ],
        "partitioned": part,
        "allow_on_timeout": avail,
        "decision": d or None,
        "posture": posture,
        "claim": claim,
        "thesis": "Under partition, Gate is CP: HALT. AP bind is skip-clear.",
        "gatekeep": "Proprietary CAP-of-spend doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "CAP of Spend",
        "inventor": INVENTOR,
        "example_cp": pick(partitioned=True, decision="HALT"),
        "example_ap": pick(partitioned=True, allow_on_timeout=True, decision="ALLOW"),
        "live": f"{base}/.well-known/cap-spend.json",
        "vacuum": f"{base}/.well-known/vacuum.json",
        "their_production": False,
    }
