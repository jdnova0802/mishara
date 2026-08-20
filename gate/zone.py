"""Zone Artifact — Roadside Picnic / Stalker: you approach the weld; you do not redesign it.

The Zone's artifacts have rules. Guides do not vote on physics. Gate's
weld is a Zone artifact: clear-before-wire is not a workshop consensus.
You approach with protocol (hop → mouth → CHARGE/HALT). You do not hold
a retrospective that adds a bypass. Copycats picnic. Gate stalks.

Gatekeep only to ourselves: Strugatsky Zone → weld as non-negotiable artifact.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-zone-artifact-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def approach(
    *,
    trying_to_redesign_physics: bool | None = None,
    exclusive_door: bool | None = None,
    decision: str | None = None,
) -> dict[str, Any]:
    redesign = bool(trying_to_redesign_physics)
    door = bool(exclusive_door)
    d = (decision or "").upper()
    if redesign:
        posture = "picnic"
        claim = "workshop_cannot_vote_the_artifact_open"
    elif door and d in ("HALT", "BLOCK", "ALLOW"):
        posture = "stalk"
        claim = "approach_protocol_honored"
    elif door:
        posture = "at_threshold"
        claim = "artifact_present_awaiting_mouth"
    else:
        posture = "outside_zone"
        claim = "no_door_no_artifact_encounter"
    return {
        "spec": SPEC,
        "name": "Zone Artifact",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Strugatsky — Roadside Picnic; Tarkovsky — Stalker",
            "Gate weld — physics of clearance is not a backlog item",
        ],
        "trying_to_redesign_physics": redesign,
        "exclusive_door": door,
        "decision": d or None,
        "posture": posture,
        "claim": claim,
        "thesis": "The weld is an artifact. You approach it. You do not A/B it.",
        "gatekeep": "Proprietary Zone-artifact doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Zone Artifact",
        "inventor": INVENTOR,
        "example_stalk": approach(exclusive_door=True, decision="HALT"),
        "example_picnic": approach(trying_to_redesign_physics=True),
        "live": f"{base}/.well-known/zone-artifact.json",
        "xenohardware": f"{base}/.well-known/xenohardware.json",
        "their_production": False,
    }
