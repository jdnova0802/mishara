"""Performative Mouth — speech-act / declaration theory of ALLOW and HALT.

Austin/Searle: some utterances do not describe — they *do*. Declarations
create institutional facts. Promises create obligations.

Gate: the mouth's ALLOW/HALT is a Status Function Declaration over the hop.
Saying HALT (with fail-closed enforcement) creates the institutional fact
that the irreversible write must not occur. Saying ALLOW+acted creates the
fact of permitted spend. Not commentary on risk — performative.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-performative-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def illocution(
    *,
    decision: str | None,
    acted: bool | None,
    enforced: bool = True,
) -> dict[str, Any]:
    d = (decision or "").upper()
    if d == "ALLOW" and acted is True:
        force = "declaration_of_permitted_spend"
        creates = "institutional_fact:permitted_irreversible_spend"
        felicity = enforced
    elif d in ("HALT", "BLOCK"):
        force = "declaration_of_restraint"
        creates = "institutional_fact:write_must_not_occur"
        felicity = enforced  # must actually block the door
    elif d == "ALLOW" and acted is not True:
        force = "declaration_without_uptake"
        creates = None
        felicity = False
    else:
        force = "non_performative_or_unevaluated"
        creates = None
        felicity = False

    return {
        "spec": SPEC,
        "name": "Performative Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Austin — How to Do Things with Words; performative utterances",
            "Searle — declarations / status-function declarations create institutional facts",
            "Gate counts-as — constitutive status; this layer names the speech-act force",
        ],
        "decision": d or None,
        "acted": acted,
        "illocutionary_force": force,
        "creates": creates,
        "felicity_conditions": {
            "enforced": enforced,
            "felicitous": felicity,
            "note": "A printed HALT that does not block the door is infelicitous theater.",
        },
        "not_constative": (
            "The mouth is not primarily describing risk. It is doing: permitting or forbidding."
        ),
        "thesis": "ALLOW and HALT are declarations — institutional facts with teeth.",
        "gatekeep": "Proprietary performative framing of mouth decisions. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: dict, row: dict) -> dict:
    payload["performative"] = illocution(
        decision=row.get("decision"),
        acted=row.get("acted"),
        enforced=True,
    )
    return payload


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Performative Mouth",
        "inventor": INVENTOR,
        "example_halt": illocution(decision="HALT", acted=False, enforced=True),
        "example_allow": illocution(decision="ALLOW", acted=True, enforced=True),
        "live": f"{base}/.well-known/performative.json",
        "mouth_constitution": f"{base}/.well-known/mouth-constitution.json",
        "their_production": False,
    }
