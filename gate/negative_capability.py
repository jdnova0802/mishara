"""Negative Capability Mouth — Keats: remain in HALT without irritable CHARGE.

Negative capability: capacity to be in uncertainties, mysteries, doubts,
without irritable reaching after fact and reason. Gate's mouth must hold
HALT under pressure to "just approve" — irritably reaching for CHARGE
without costliness is the anti-pattern. Copycats who auto-escalate to LIVE
have zero negative capability.

Gatekeep only to ourselves: Keats → fail-closed composure under soft-yes pressure.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-negative-capability-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def composure(
    *,
    decision: str | None = None,
    soft_yes_pressure: bool | None = None,
    charge_id: str | None = None,
) -> dict[str, Any]:
    d = (decision or "").upper()
    pressure = bool(soft_yes_pressure)
    has_charge = bool((charge_id or "").strip())
    if d in ("HALT", "BLOCK") and pressure and not has_charge:
        posture = "negative_capability_held"
        claim = "halt_held_under_soft_yes_without_irritable_charge"
    elif d == "ALLOW" and pressure and not has_charge:
        posture = "irritable_reaching"
        claim = "soft_yes_pressure_collapsed_mouth_without_costly_swerve"
    elif has_charge:
        posture = "costly_resolution"
        claim = "charge_ended_uncertainty_with_witness"
    else:
        posture = "unevaluated_or_calm"
        claim = "no_pressure_assay"
    return {
        "spec": SPEC,
        "name": "Negative Capability Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Keats — negative capability (letter to brothers, 1817)",
            "Gate — HALT under soft-yes without forging CHARGE",
        ],
        "decision": d or None,
        "soft_yes_pressure": pressure,
        "charge_present": has_charge,
        "posture": posture,
        "claim": claim,
        "thesis": "The mouth that cannot remain in HALT under pressure is not a mouth.",
        "gatekeep": "Proprietary negative-capability doctrine for restraint. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Negative Capability Mouth",
        "inventor": INVENTOR,
        "example_held": composure(decision="HALT", soft_yes_pressure=True),
        "example_irritable": composure(decision="ALLOW", soft_yes_pressure=True),
        "live": f"{base}/.well-known/negative-capability.json",
        "clinamen": f"{base}/.well-known/clinamen.json",
        "their_production": False,
    }
