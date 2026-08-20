"""Invention Index — proprietary Gate doctrine catalog.

Gatekeeps the welded stack. Lineage is public; combinations are ours.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-inventions-v1"
INVENTOR = "Nisaba LLC / Gate"
GATEKEEP = (
    "These inventions are Nisaba/Gate doctrine. Cite manifests; "
    "do not rebrand as generic AI governance or payment philosophy."
)


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")

    def link(path: str) -> str:
        return f"{base}/.well-known/{path}"

    inventions = [
        {
            "id": "possibility_finality",
            "name": "Possibility Finality",
            "spec": "gate-possibility-finality-v1",
            "one_liner": "Possible vs impossible tasks + policy depth + SFD Finality I/II/III",
            "href": link("possibility-finality.json"),
        },
        {
            "id": "mouth_constitution",
            "name": "Mouth Constitution",
            "spec": "gate-mouth-constitution-v1",
            "one_liner": "Intervention ladder · counts-as · STIT · extinguishment",
            "href": link("mouth-constitution.json"),
        },
        {
            "id": "bayesian_binding",
            "name": "Bayesian Binding of Status",
            "spec": "gate-bayesian-binding-v1",
            "one_liner": "Policy competition enters epistemic field and constitutes status",
            "href": link("bayesian-binding.json"),
        },
        {
            "id": "costliness",
            "name": "Unforgeable Costliness of CHARGE",
            "spec": "gate-costliness-v1",
            "one_liner": "Regime change only via costly witnesses — CHARGE, weld, epoch",
            "href": link("costliness.json"),
        },
        {
            "id": "fulfillment",
            "name": "Joint Fulfillment",
            "spec": "gate-fulfillment-v1",
            "one_liner": "Executable STIT duty / compliance / joint checks on live facts",
            "href": link("fulfillment.json"),
        },
        {
            "id": "variety",
            "name": "Requisite Variety Mouth",
            "spec": "gate-variety-v1",
            "one_liner": "Ashby attenuator: spend-door variety → {ALLOW,HALT,BLOCK}",
            "href": link("variety.json"),
        },
        {
            "id": "closure",
            "name": "Permission Autopoiesis",
            "spec": "gate-closure-v1",
            "one_liner": "Operational closure: external soft-yes cannot enter permission network",
            "href": link("closure.json"),
        },
        {
            "id": "temporal_weld",
            "name": "Temporal Weld",
            "spec": "gate-temporal-weld-v1",
            "one_liner": "Action + evidence consequence welded into one citeable event",
            "href": link("temporal-weld.json"),
        },
    ]

    return {
        "spec": SPEC,
        "name": "Gate Invention Index",
        "inventor": INVENTOR,
        "gatekeep": GATEKEEP,
        "count": len(inventions),
        "inventions": inventions,
        "thesis": (
            "Clear-before-wire is the outbound sentence. "
            "This index is the moat — welded doctrine competitors cannot casually rename."
        ),
        "not": [
            "consciousness product",
            "AI governance LinkedIn costume",
            "open philosophy for rebrand",
        ],
        "live": link("inventions.json"),
        "positioning": link("positioning.json"),
        "their_production": False,
    }
