"""Requisite Variety Mouth — Ashby × Beer attenuator on irreversible acts.

Ashby: only variety can destroy variety. The controller must match disturbance
variety — or attenuate what reaches the essential variables.

Gate: the environment of spend attempts has unbounded variety (agents, doors,
renewals, midnight jobs). The mouth attenuates that variety to a finite
decision alphabet {ALLOW, HALT, BLOCK} with one married write — so the
essential variable (irreversible spend world) stays controlled.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-variety-v1"
INVENTOR = "Nisaba LLC / Gate"

# Disturbance variety the mouth is built to absorb (attenuate).
DISTURBANCE_CLASSES = (
    "cloud_api_bind_only",
    "cloud_api_bind_and_issue",
    "ui_bind_button",
    "renewal_midnight_workflow",
    "agent_tool_call",
    "x402_paid_act",
    "stale_hop_replay",
    "uw_approve_without_charge",
    "duplicate_redeem",
    "dead_parent_child_spend",
)

DECISION_ALPHABET = ("ALLOW", "HALT", "BLOCK")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attenuate(
    *,
    disturbance: str | None = None,
    decision: str | None = None,
    doors_honored: int | None = None,
    doors_total: int | None = None,
) -> dict[str, Any]:
    """Map a high-variety disturbance into the mouth's decision alphabet."""
    d = (decision or "").upper()
    dist = (disturbance or "unspecified_spend_attempt").strip()
    absorbed = dist in DISTURBANCE_CLASSES or dist.startswith("spend_") or dist.startswith("door_")

    if d in DECISION_ALPHABET:
        outcome_variety = 1  # one essential outcome selected
        controlled = True
    else:
        outcome_variety = None
        controlled = False

    ratio = None
    if doors_total and doors_total > 0 and doors_honored is not None:
        ratio = round(doors_honored / doors_total, 4)

    return {
        "spec": SPEC,
        "name": "Requisite Variety Attenuation",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "disturbance": dist,
        "disturbance_absorbed": absorbed,
        "decision_alphabet": list(DECISION_ALPHABET),
        "decision": d or None,
        "outcome_variety": outcome_variety,
        "controlled": controlled,
        "exclusive_door_coverage": {
            "doors_honored": doors_honored,
            "doors_total": doors_total,
            "ratio": ratio,
            "note": "Coverage < 1.0 means residual disturbance variety bypasses the mouth.",
        },
        "law": "Only variety can destroy variety — mouth alphabet must cover irreversible-act disturbances.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Requisite Variety Mouth",
        "inventor": INVENTOR,
        "lineage": [
            "W. Ross Ashby — Law of Requisite Variety",
            "Stafford Beer — variety attenuation / amplification; Cybersyn",
            "Gate — one mouth, finite decision alphabet, exclusive doors",
        ],
        "thesis": (
            "Unbounded spend-door variety is attenuated to {ALLOW, HALT, BLOCK} "
            "before the essential variable — the irreversible world — flips."
        ),
        "disturbance_classes": list(DISTURBANCE_CLASSES),
        "decision_alphabet": list(DECISION_ALPHABET),
        "amplification": {
            "what": "Human CHARGE / weld amplifies regulatory variety when automation is insufficient",
            "note": "Ashby: regulation cannot be simply amplified; supplementation (human costly commit) is allowed",
        },
        "example": attenuate(disturbance="cloud_api_bind_only", decision="HALT", doors_honored=3, doors_total=3),
        "live": f"{base}/.well-known/variety.json",
        "gatekeep": "Proprietary Ashby attenuator framing for irreversible-spend control. Ours.",
        "their_production": False,
    }
