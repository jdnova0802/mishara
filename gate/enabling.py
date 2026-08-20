"""Enabling Grip — dead-man's / enabling-device theory of the license fuse.

Industrial safety: enabling devices require continuous intentional hold;
release or panic-squeeze → machine stops (fail-safe).

Gate: the license parent is the enabling grip on child spend. Parent LIVE
= mid-position enable. Parent DEAD/UNSIGNED = released → children cannot
spend. CHARGE re-grips. Blow releases. Not optional soft-policy — enabling.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-enabling-v1"
INVENTOR = "Nisaba LLC / Gate"

POSITIONS = {
    "released": "UNSIGNED|DEAD — no enable; children cannot spend",
    "enabled": "LIVE — intentional hold; tickets may print/redeem while parent LIVE",
    "armed": "LIVE with outstanding children — grip held under load",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def grip(
    *,
    parent_state: str | None = None,
    outstanding_tickets: int | None = None,
    fused: bool | None = None,
) -> dict[str, Any]:
    st = (parent_state or "").upper()
    outstanding = int(outstanding_tickets or 0)
    is_fused = bool(fused) if fused is not None else bool(st)

    if not is_fused:
        position = "not_in_circuit"
        enable = False
        claim = "no_license_id_scanner_path_without_parent_grip"
    elif st in ("UNSIGNED", "DEAD"):
        position = "released"
        enable = False
        claim = "parent_released_children_cannot_spend"
    elif st == "LIVE" and outstanding > 0:
        position = "armed"
        enable = True
        claim = "parent_live_grip_under_outstanding_children"
    elif st == "LIVE":
        position = "enabled"
        enable = True
        claim = "parent_live_enables_child_path"
    elif st == "ARMED":
        position = "armed"
        enable = True
        claim = "public_armed_means_live_with_outstanding"
    else:
        position = "unknown_fail_safe"
        enable = False
        claim = "unknown_parent_state_treated_as_released"

    return {
        "spec": SPEC,
        "name": "Enabling Grip",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Dead man's switch / enabling device — continuous intentional enable",
            "IEC 60947-5-8 — three-position enabling switches (adjacent safety framing)",
            "Gate license fuse — children cannot outlive parent; CHARGE-only re-grip",
        ],
        "positions": POSITIONS,
        "parent_state": st or None,
        "outstanding_tickets": outstanding,
        "position": position,
        "enable_spend_path": enable,
        "claim": claim,
        "fail_safe": "Release (DEAD) stops child spend — no need for active deny of each child.",
        "thesis": "The parent license is an enabling grip, not a directory lookup.",
        "gatekeep": "Proprietary enabling-device framing of license fuse. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Enabling Grip",
        "inventor": INVENTOR,
        "example_enabled": grip(parent_state="LIVE", outstanding_tickets=0, fused=True),
        "example_released": grip(parent_state="DEAD", outstanding_tickets=2, fused=True),
        "live": f"{base}/.well-known/enabling.json",
        "license_fuse": f"{base}/.well-known/license-fuse.json",
        "their_production": False,
    }
