"""Hyperobject Mouth — Morton-shaped irreversibility.

Hyperobjects: massively distributed in time/space — viscous, nonlocal,
temporally undulating. Irreversible spend is not a local hop event alone;
it is a hyperobject that sticks to inhabitants, phases across verify/receipts,
and undulates across generations (parent license, afterward letters).

Gate names that mass so partners stop treating the wire as a click.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-hyperobject-v1"
INVENTOR = "Nisaba LLC / Gate"

PROPERTIES = (
    ("viscosity", "Spend sticks to inhabitant — harm does not restore; money does not un-leave"),
    ("nonlocality", "Local hop is a footprint; the hyperobject is the spent world + evidence trail"),
    ("temporal_undulation", "License parent / afterward / settlement windows outlive the actor's session"),
    ("phasing", "Appears as HALT receipt, verify URL, restraint leaf — never one dashboard pixel"),
    ("interobjectivity", "Shared by carrier, operator, stranger attestor, inhabitant — relations, not one user"),
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def map_hop(*, decision: str | None = None, acted: bool | None = None) -> dict[str, Any]:
    d = (decision or "").upper()
    if acted is True and d == "ALLOW":
        claim = "hyperobject_instantiated_spent_world"
    elif d in ("HALT", "BLOCK"):
        claim = "hyperobject_averted_local_footprint_is_the_no"
    else:
        claim = "hyperobject_unevaluated"
    return {
        "spec": SPEC,
        "name": "Hyperobject Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Timothy Morton — hyperobjects (viscosity, nonlocality, temporal undulation, phasing, interobjectivity)",
            "Gate floor / inhabitant — irreversible that isn't only yours",
        ],
        "properties": [{"id": a, "gate_meaning": b} for a, b in PROPERTIES],
        "decision": d or None,
        "acted": acted,
        "claim": claim,
        "thesis": "The wire is a local footprint of a nonlocal spent world.",
        "gatekeep": "Proprietary hyperobject framing of irreversible spend. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: dict, row: dict) -> dict:
    payload["hyperobject"] = map_hop(decision=row.get("decision"), acted=row.get("acted"))
    return payload


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Hyperobject Mouth",
        "inventor": INVENTOR,
        "example": map_hop(decision="HALT", acted=False),
        "live": f"{base}/.well-known/hyperobject.json",
        "inhabitant": f"{base}/.well-known/inhabitant.json",
        "their_production": False,
    }
