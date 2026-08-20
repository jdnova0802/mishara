"""Privilege Rings of Spend — ring 0 is CHARGE; software cannot promote itself.

Ring 3: hop attempts, PAS binds, agent calls.
Ring 2: exclusive door + epoch lock.
Ring 1: license fuse / parent LIVE.
Ring 0: CHARGE. Only ring 0 writes LIVE. A userspace 'approve' is not a
syscall. Copycats flatten rings into one admin panel.

Gatekeep only to ourselves: CPU rings → spend privilege hardware.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-privilege-rings-v1"
INVENTOR = "Nisaba LLC / Gate"

RINGS = (
    (3, "userspace_hop", "bind attempts, agent calls, PAS 200s"),
    (2, "door_epoch", "exclusive door + epoch lock"),
    (1, "license_fuse", "parent LIVE / enabling grip"),
    (0, "charge", "DEAD→LIVE witness — unforgeable costliness"),
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ring(
    *,
    claimed_live: bool | None = None,
    charge_id: str | None = None,
    from_userspace: bool | None = None,
) -> dict[str, Any]:
    claimed = bool(claimed_live)
    charge = bool((charge_id or "").strip())
    user = True if from_userspace is None else bool(from_userspace)
    if claimed and user and not charge:
        posture = "ring_violation"
        claim = "userspace_cannot_promote_to_live"
    elif claimed and charge:
        posture = "ring0_write"
        claim = "charge_syscall_produced_live"
    elif not claimed:
        posture = "stayed_in_userspace_or_halt"
        claim = "no_privilege_escalation"
    else:
        posture = "unevaluated"
        claim = "insufficient_ring_data"
    return {
        "spec": SPEC,
        "name": "Privilege Rings of Spend",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "x86/ARM privilege rings / syscalls",
            "Gate CHARGE-only DEAD→LIVE — ring 0 is not an admin screen",
        ],
        "rings": [{"ring": a, "id": b, "meaning": c} for a, b, c in RINGS],
        "claimed_live": claimed,
        "charge_present": charge,
        "from_userspace": user,
        "posture": posture,
        "claim": claim,
        "thesis": "LIVE is a privileged write. Approvals are ring 3 noise.",
        "gatekeep": "Proprietary privilege-ring doctrine for spend. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Privilege Rings of Spend",
        "inventor": INVENTOR,
        "example_violation": ring(claimed_live=True, from_userspace=True, charge_id=None),
        "example_ok": ring(claimed_live=True, from_userspace=False, charge_id="chg_1"),
        "live": f"{base}/.well-known/privilege-rings.json",
        "costliness": f"{base}/.well-known/costliness.json",
        "their_production": False,
    }
