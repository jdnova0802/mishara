"""Category Mouth — morphisms of clearance, not objects of policy.

Objects: DEAD, LIVE, HALT states. Morphisms: CHARGE, expire, extinguish.
Functors: map operator intent into welded status without smuggling PII
onto PAS. Natural transformations: license fuse swaps without breaking
clear-before-wire. Copycats ship objects (policies); Gate ships morphisms.

Gatekeep only to ourselves: category theory → morphism-first mouth.
"""

from __future__ import annotations

from typing import Any

SPEC = "gate-category-mouth-v1"
INVENTOR = "Nisaba LLC / Gate"


def public_document() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "inventor": INVENTOR,
        "gatekeep": True,
        "title": "Category Mouth",
        "thesis": (
            "Clearance is a morphism, not an object. Policies are objects "
            "without arrows; Gate's product is the arrow that changes status."
        ),
        "category": {
            "objects": ["DEAD", "LIVE", "HALT", "extinguished"],
            "morphisms": [
                {"name": "CHARGE", "from": "DEAD", "to": "LIVE", "requires": "costliness"},
                {"name": "HALT", "from": "intent", "to": "HALT", "requires": "fail_closed"},
                {"name": "extinguish", "from": "LIVE", "to": "extinguished", "requires": "settlement"},
            ],
            "functor": "operator_intent → welded_status (no PII on PAS)",
            "natural_transformation": "license_fuse swap preserving clear-before-wire",
        },
        "not": [
            "Academic CT lecture on the marketing site",
            "A claim that money is a topos",
        ],
        "relation": {
            "constitution": "Counts-as and STIT sit on morphisms, not PDFs",
            "fulfillment": "Joint fulfillment is composition of morphisms",
            "possibility_finality": "Finality is morphism that kills further arrows",
        },
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = public_document()
    body["name"] = body.get("title") or "Category Mouth"
    body["live"] = f"{base}/.well-known/category-mouth.json"
    body["their_production"] = False
    return body
