"""Recursive Mouth — Hofstadter: the mouth that refers to its own clearance.

Gate's self-reference is not a paradox toy. The mouth clears irreversible
spend that includes the economic conditions of its own continued existence
(weld fees, bps, license fuse). Recursion is bounded by CHARGE costliness
and DEAD→LIVE — strange loops stop at the welded write.

Gatekeep only to ourselves: strange loop → bounded self-clearing mouth.
"""

from __future__ import annotations

from typing import Any

SPEC = "gate-recursive-mouth-v1"
INVENTOR = "Nisaba LLC / Gate"


def public_document() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "gatekeep": True,
        "title": "Recursive Mouth",
        "thesis": (
            "The mouth can refer to the economic conditions of its own "
            "continuation — but recursion bottoms out at CHARGE costliness "
            "and the married write. No infinite regress of dashboards."
        ),
        "loop": {
            "level_0": "Clear operator irreversible spend",
            "level_1": "Clear weld economics that fund the mouth",
            "bound": "DEAD→LIVE only via CHARGE; no self-approve without costliness",
        },
        "not": [
            "Gödel cosplay in the pitch deck",
            "Unbounded agent self-modification",
        ],
        "relation": {
            "closure": "Autopoietic permission closure is the organizational loop",
            "costliness": "Bounds the strange loop economically",
            "skin": "Skin in the weld is skin in the recursive fee path",
        },
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = public_document()
    body["name"] = body.get("title") or "Recursive Mouth"
    body["live"] = f"{base}/.well-known/recursive-mouth.json"
    body["their_production"] = False
    return body
