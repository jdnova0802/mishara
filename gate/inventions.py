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

# (id, name, spec, one_liner, well-known filename)
CATALOG = (
    ("possibility_finality", "Possibility Finality", "gate-possibility-finality-v1",
     "Possible vs impossible tasks + policy depth + SFD Finality I/II/III", "possibility-finality.json"),
    ("mouth_constitution", "Mouth Constitution", "gate-mouth-constitution-v1",
     "Intervention ladder · counts-as · STIT · extinguishment", "mouth-constitution.json"),
    ("bayesian_binding", "Bayesian Binding of Status", "gate-bayesian-binding-v1",
     "Policy competition enters epistemic field and constitutes status", "bayesian-binding.json"),
    ("costliness", "Unforgeable Costliness of CHARGE", "gate-costliness-v1",
     "Regime change only via costly witnesses — CHARGE, weld, epoch", "costliness.json"),
    ("fulfillment", "Joint Fulfillment", "gate-fulfillment-v1",
     "Executable STIT duty / compliance / joint checks on live facts", "fulfillment.json"),
    ("variety", "Requisite Variety Mouth", "gate-variety-v1",
     "Ashby attenuator: spend-door variety → {ALLOW,HALT,BLOCK}", "variety.json"),
    ("closure", "Permission Autopoiesis", "gate-closure-v1",
     "Operational closure: external soft-yes cannot enter permission network", "closure.json"),
    ("temporal_weld", "Temporal Weld", "gate-temporal-weld-v1",
     "Action + evidence consequence welded into one citeable event", "temporal-weld.json"),
    ("nonrepudiation", "Non-Repudiation Ladder", "gate-nonrepudiation-v1",
     "NRI/NRO/NRT/NRC for mouth evidence — hash≠authorship honesty", "nonrepudiation.json"),
    ("regime_function", "Regime Function", "gate-regime-function-v1",
     "Mouth as published fixed function; CHARGE-only regime change", "regime-function.json"),
    ("custody", "Custody Chain", "gate-custody-v1",
     "Identify→hash→sign→chain→publish→verify for hop evidence", "custody.json"),
    ("option_halt", "Option Value of HALT", "gate-option-halt-v1",
     "Real-options: HALT preserves wait value; ALLOW kills it", "option-halt.json"),
    ("performative", "Performative Mouth", "gate-performative-v1",
     "ALLOW/HALT as status-function declarations — not risk commentary", "performative.json"),
    ("schelling", "Schelling Default", "gate-schelling-v1",
     "Clear-before-wire as focal point; weld makes commitment credible", "schelling.json"),
    ("skin", "Skin in the Weld", "gate-skin-v1",
     "Taleb symmetry: weld + Gate capital + mutualized fund", "skin.json"),
    ("proof_restraint", "Proof of Restraint", "gate-proof-restraint-v1",
     "PoR-inverse: Merkle-style commitment to published nos", "proof-restraint.json"),
    ("enabling", "Enabling Grip", "gate-enabling-v1",
     "License parent as enabling device; release → children cannot spend", "enabling.json"),
    ("capability", "Capability Conversion", "gate-capability-v1",
     "Ticket is resource; conversion factors decide real freedom to spend", "capability.json"),
)


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")

    def link(path: str) -> str:
        return f"{base}/.well-known/{path}"

    inventions = [
        {
            "id": i[0],
            "name": i[1],
            "spec": i[2],
            "one_liner": i[3],
            "href": link(i[4]),
        }
        for i in CATALOG
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
