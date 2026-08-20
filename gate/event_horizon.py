"""Event Horizon Fuse — past CHARGE, skip-clear information does not return.

A horizon: signals from inside cannot rewrite the outside story. Once
CHARGE writes LIVE and the hop acts, you cannot un-spend by editing a
dashboard. HALT keeps you outside the horizon. Copycats sell 'undo'.
Gate sells a horizon.

Gatekeep only to ourselves: GR event horizon → CHARGE as one-way membrane.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-event-horizon-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def horizon(
    *,
    decision: str | None = None,
    acted: bool | None = None,
    trying_to_undo: bool | None = None,
) -> dict[str, Any]:
    d = (decision or "").upper()
    acted_b = bool(acted)
    undo = bool(trying_to_undo)
    if acted_b and d == "ALLOW":
        posture = "inside_horizon"
        claim = "spent_world_does_not_return_skip_clear_rewrites"
        if undo:
            claim = "undo_is_not_a_port_on_this_chassis"
    elif d in ("HALT", "BLOCK"):
        posture = "outside_horizon"
        claim = "halt_preserves_returnability"
    else:
        posture = "approach"
        claim = "not_yet_across"
    return {
        "spec": SPEC,
        "name": "Event Horizon Fuse",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "General relativity — event horizon / one-way causal membrane",
            "Gate possibility finality + hyperobject spend",
        ],
        "decision": d or None,
        "acted": acted_b,
        "trying_to_undo": undo,
        "posture": posture,
        "claim": claim,
        "thesis": "CHARGE crosses a horizon. Dashboards do not pull you back.",
        "gatekeep": "Proprietary event-horizon doctrine. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["event_horizon"] = horizon(decision=row.get("decision"), acted=row.get("acted"))
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Event Horizon Fuse",
        "inventor": INVENTOR,
        "example_inside": horizon(decision="ALLOW", acted=True, trying_to_undo=True),
        "example_outside": horizon(decision="HALT", acted=False),
        "live": f"{base}/.well-known/event-horizon.json",
        "possibility_finality": f"{base}/.well-known/possibility-finality.json",
        "their_production": False,
    }
