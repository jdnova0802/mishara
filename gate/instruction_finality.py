"""Instruction Finality — irrevocable moment before settlement finality III.

SFD/PFMI name finality at the CSD window. Gate names instruction finality at
the hop: once ALLOW+act on the exclusive door, the instruction is not a
draft — it is the gross obligation your net will later collapse. UW approve
without CHARGE never reaches instruction finality; it is still revocable noise.

Not Earth-side cliche: not blockchain finality. Operational moment II before
your window's II.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-instruction-finality-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def moments(
    *,
    decision: str | None = None,
    acted: bool | None = None,
    charge_id: str | None = None,
    exclusive_door: bool | None = None,
) -> dict[str, Any]:
    d = (decision or "").upper()
    acted_b = bool(acted)
    charge = bool((charge_id or "").strip())
    door = True if exclusive_door is None else bool(exclusive_door)
    if acted_b and d == "ALLOW" and door:
        ii = True
        claim = "instruction_finality_ii_irrevocable_on_hop"
    elif d in ("HALT", "BLOCK") and door:
        ii = False
        claim = "instruction_never_entered_finality_stays_revocable_no"
    elif d == "ALLOW" and not door:
        ii = False
        claim = "no_exclusive_door_no_instruction_finality"
    else:
        ii = False
        claim = "draft_or_unevaluated"
    return {
        "spec": SPEC,
        "name": "Instruction Finality",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "SFD Finality I/II/III — adapted to pre-settlement instruction hop",
            "PFMI P8 — clear moment before third-party dispute",
            "Gate possibility finality — window hash is downstream",
        ],
        "moments": {
            "I_intent": {"reached": bool(d), "meaning": "Hop presented on door"},
            "II_irrevocable_instruction": {
                "reached": ii,
                "meaning": "ALLOW+act on exclusive door — gross obligation born",
            },
            "III_settlement_binding": {
                "reached": False,
                "meaning": "Deferred to settlement window finality hash",
            },
        },
        "decision": d or None,
        "acted": acted_b,
        "charge_present": charge,
        "exclusive_door": door,
        "claim": claim,
        "thesis": "Your CSD finality is downstream. Instruction finality is here — at the hop.",
        "gatekeep": "Proprietary instruction-finality doctrine. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["instruction_finality"] = moments(
        decision=row.get("decision"),
        acted=row.get("acted"),
        charge_id=row.get("charge_id"),
        exclusive_door=True,
    )
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Instruction Finality",
        "inventor": INVENTOR,
        "example_live": moments(decision="ALLOW", acted=True, exclusive_door=True),
        "example_halt": moments(decision="HALT", acted=False, exclusive_door=True),
        "live": f"{base}/.well-known/instruction-finality.json",
        "possibility_finality": f"{base}/.well-known/possibility-finality.json",
        "their_production": False,
    }
