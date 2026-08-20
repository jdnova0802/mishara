"""Unskippable Layer — Bratton: the mouth is a Stack layer you cannot route around.

Benjamin Bratton's Stack: planetary layers (Earth, Cloud, City, Address,
Interface, User). Gate adds an unskippable clearance layer between
Interface and irreversible User-act. Integrations that 'skip Gate' are
claiming to skip a layer the way you skip Earth. You don't.

Gatekeep only to ourselves: The Stack → mouth as non-optional layer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-stack-layer-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def route(*, skip_mouth: bool | None = None, exclusive_door: bool | None = None) -> dict[str, Any]:
    skip = bool(skip_mouth)
    door = bool(exclusive_door)
    if skip:
        posture = "illegal_route"
        claim = "you_cannot_skip_earth_or_the_mouth"
    elif door:
        posture = "layer_honored"
        claim = "traffic_enters_through_clearance_layer"
    else:
        posture = "layer_missing"
        claim = "no_door_no_stack_position"
    return {
        "spec": SPEC,
        "name": "Unskippable Layer",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Benjamin Bratton — The Stack (layers you do not skip)",
            "Gate exclusive door as clearance layer under Interface",
        ],
        "skip_mouth": skip,
        "exclusive_door": door,
        "posture": posture,
        "claim": claim,
        "thesis": "Skip-Gate is not an integration strategy. It is a layer violation.",
        "gatekeep": "Proprietary unskippable-layer doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Unskippable Layer",
        "inventor": INVENTOR,
        "example_ok": route(exclusive_door=True),
        "example_skip": route(skip_mouth=True),
        "live": f"{base}/.well-known/stack-layer.json",
        "iommu": f"{base}/.well-known/iommu.json",
        "their_production": False,
    }
