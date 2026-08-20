"""Convivial Mouth — Illich/Ellul complement: tools that enlarge competence, not dependence.

Convivial tools: usable by persons, not only by systems that replace them.
Gate's mouth enlarges licensed operator competence to refuse — it does not
replace judgment with an opaque score. CHARGE remains human-costly.
Copycats sell dependence: more dashboard, less mouth.

Gatekeep only to ourselves: conviviality → mouth enlarges refusal competence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-convivial-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def assay(
    *,
    opaque_score_permission: bool | None = None,
    human_charge_required: bool | None = None,
    public_alphabet: bool | None = None,
) -> dict[str, Any]:
    opaque = bool(opaque_score_permission)
    human = True if human_charge_required is None else bool(human_charge_required)
    pub = True if public_alphabet is None else bool(public_alphabet)
    if opaque:
        posture = "anti_convivial"
        claim = "opaque_score_replaces_refusal_competence"
    elif human and pub:
        posture = "convivial"
        claim = "public_alphabet_plus_human_charge_enlarges_competence"
    else:
        posture = "partial"
        claim = "missing_human_charge_or_public_alphabet"
    return {
        "spec": SPEC,
        "name": "Convivial Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Ivan Illich — Tools for Conviviality",
            "Gate — ALLOW/HALT/BLOCK as public competence, CHARGE as human cost",
        ],
        "opaque_score_permission": opaque,
        "human_charge_required": human,
        "public_alphabet": pub,
        "posture": posture,
        "claim": claim,
        "thesis": "The mouth teaches refusal. Scores teach dependence.",
        "gatekeep": "Proprietary conviviality doctrine for Gate. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Convivial Mouth",
        "inventor": INVENTOR,
        "example_ok": assay(opaque_score_permission=False, human_charge_required=True, public_alphabet=True),
        "example_bad": assay(opaque_score_permission=True),
        "live": f"{base}/.well-known/convivial.json",
        "technique_limit": f"{base}/.well-known/technique-limit.json",
        "their_production": False,
    }
