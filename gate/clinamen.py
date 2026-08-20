"""Clinamen CHARGE — Lucretian swerve as regime break.

Clinamen: minimal atomic swerve at no fixed time/place — breaks the endless
causal chain; without it, only rain of parallel fate.

Gate: soft-yes chains (UW approve → hop → bind) are the rain of fate.
CHARGE is the clinamen — minimal costly deviation that snaps the chain and
opens a new regime. Not random volition theater; named witness swerve.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-clinamen-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def swerve(
    *,
    charge_id: str | None = None,
    prior_halt: bool | None = None,
    soft_yes_present: bool | None = None,
) -> dict[str, Any]:
    cid = (charge_id or "").strip() or None
    if cid and prior_halt:
        posture = "clinamen_fired"
        claim = "charge_swerve_broke_halt_fate_chain"
    elif soft_yes_present and not cid:
        posture = "fate_chain_intact"
        claim = "soft_yes_without_charge_is_parallel_rain_not_swerve"
    elif cid:
        posture = "swerve_without_prior_context"
        claim = "charge_present_regime_may_change"
    else:
        posture = "no_swerve"
        claim = "deterministic_soft_path_or_unevaluated"
    return {
        "spec": SPEC,
        "name": "Clinamen CHARGE",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Lucretius / Epicurus — clinamen (atomic swerve) breaks fate's bonds",
            "Gate epoch — charge_id is the sole admissible regime witness",
            "Gate costliness — swerve must be unforgeably costly",
        ],
        "charge_id_present": bool(cid),
        "prior_halt": prior_halt,
        "soft_yes_present": soft_yes_present,
        "posture": posture,
        "claim": claim,
        "thesis": "Without CHARGE, approve-chains fall like rain. CHARGE is the swerve.",
        "gatekeep": "Proprietary clinamen framing of CHARGE. Ours.",
        "not_consciousness": "Not free-will metaphysics — regime-change physics for permission.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Clinamen CHARGE",
        "inventor": INVENTOR,
        "example_swerve": swerve(charge_id="chg_1", prior_halt=True),
        "example_fate": swerve(charge_id=None, soft_yes_present=True, prior_halt=True),
        "live": f"{base}/.well-known/clinamen.json",
        "costliness": f"{base}/.well-known/costliness.json",
        "epoch_note": "Epoch lock keeps the rain falling until the swerve.",
        "their_production": False,
    }
