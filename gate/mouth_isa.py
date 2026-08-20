"""Mouth ISA — alien instruction set: CHARGE, HALT, BLOCK, ALLOW. No illegal opcodes.

Software APIs accumulate verbs. Xenohardware does not. The mouth ISA is
tiny, closed, and costly. Soft-yes, dashboard-green, and admin-LIVE are
illegal opcodes — they trap. Copycats ship REST zoos; Gate ships four
instructions and a privilege ring.

Gatekeep only to ourselves: CPU ISA metaphor → closed mouth opcode set.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-mouth-isa-v1"
INVENTOR = "Nisaba LLC / Gate"

LEGAL_OPCODES = ("ALLOW", "HALT", "BLOCK", "CHARGE")
ILLEGAL_OPCODES = (
    "SOFT_YES",
    "ADMIN_LIVE",
    "UW_APPROVE",
    "DASHBOARD_GREEN",
    "RISK_SCORE_PASS",
    "AI_APPROVE",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def decode(*, opcode: str | None = None, privileged: bool | None = None) -> dict[str, Any]:
    op = (opcode or "").strip().upper()
    priv = bool(privileged)
    if op in ILLEGAL_OPCODES or op.startswith("SOFT_"):
        posture = "illegal_opcode_trap"
        claim = "instruction_does_not_exist_on_this_silicon"
    elif op == "CHARGE" and not priv:
        posture = "privilege_violation"
        claim = "charge_requires_ring0_costliness"
    elif op in LEGAL_OPCODES:
        posture = "legal_decode"
        claim = "mouth_isa_accepted"
    else:
        posture = "undefined"
        claim = "unknown_mnemonic"
    return {
        "spec": SPEC,
        "name": "Mouth ISA",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "CPU instruction sets — closed opcode space, illegal-instruction traps",
            "Gate variety mouth — finite alphabet, not REST sprawl",
        ],
        "legal_opcodes": list(LEGAL_OPCODES),
        "illegal_opcodes": list(ILLEGAL_OPCODES),
        "opcode": op or None,
        "privileged": priv,
        "posture": posture,
        "claim": claim,
        "thesis": "If your API has a verb for skip-clear, you do not have an ISA.",
        "gatekeep": "Proprietary mouth instruction-set doctrine. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    d = str(row.get("decision") or "").upper()
    acted = bool(row.get("acted"))
    opcode = "ALLOW" if acted and d == "ALLOW" else (d if d in {"HALT", "BLOCK", "ALLOW"} else None)
    out["mouth_isa"] = decode(opcode=opcode, privileged=bool(row.get("charge_id")))
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Mouth ISA",
        "inventor": INVENTOR,
        "example_legal": decode(opcode="HALT"),
        "example_trap": decode(opcode="SOFT_YES"),
        "live": f"{base}/.well-known/mouth-isa.json",
        "variety": f"{base}/.well-known/variety.json",
        "their_production": False,
    }
