"""Curry-Howard Mouth — HALT is a proof of no; CHARGE is a proof of LIVE.

Propositions as types: a proof is a program. Gate: a HALT receipt is a
proof inhabitant of 'this hop is not permitted spend'. CHARGE is a proof
of LIVE. Dashboards are uninhabited types — they assert without proof
terms. Copycats publish theorems with no witnesses.

Gatekeep only to ourselves: Curry-Howard → receipts as proof terms.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-curry-howard-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def inhabit(
    *,
    decision: str | None = None,
    acted: bool | None = None,
    receipt_hash: str | None = None,
    charge_id: str | None = None,
) -> dict[str, Any]:
    d = (decision or "").upper()
    acted_b = bool(acted)
    proof = bool((receipt_hash or "").strip())
    charge = bool((charge_id or "").strip())
    if d in ("HALT", "BLOCK") and proof:
        posture = "proof_of_no"
        claim = "halt_receipt_inhabits_not_permitted"
    elif acted_b and d == "ALLOW" and charge and proof:
        posture = "proof_of_live"
        claim = "charge_plus_receipt_inhabits_live"
    elif (d in ("HALT", "BLOCK", "ALLOW") or acted_b) and not proof:
        posture = "uninhabited_assertion"
        claim = "dashboard_theorem_without_proof_term"
    else:
        posture = "empty_context"
        claim = "no_proposition"
    return {
        "spec": SPEC,
        "name": "Curry-Howard Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Curry-Howard correspondence — proofs as programs / inhabitants",
            "Gate receipts + CHARGE witnesses as proof terms",
        ],
        "decision": d or None,
        "acted": acted_b,
        "proof_term": proof,
        "charge_present": charge,
        "posture": posture,
        "claim": claim,
        "thesis": "No proof term, no LIVE. Assertions are not inhabitants.",
        "gatekeep": "Proprietary Curry-Howard mouth doctrine. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["curry_howard"] = inhabit(
        decision=row.get("decision"),
        acted=row.get("acted"),
        receipt_hash=row.get("receipt_hash"),
        charge_id=row.get("charge_id"),
    )
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Curry-Howard Mouth",
        "inventor": INVENTOR,
        "example_no": inhabit(decision="HALT", receipt_hash="abc"),
        "example_empty": inhabit(decision="ALLOW", acted=True),
        "live": f"{base}/.well-known/curry-howard.json",
        "nonrepudiation": f"{base}/.well-known/nonrepudiation.json",
        "their_production": False,
    }
