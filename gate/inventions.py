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
    # Wave 5 — hyperobject / via negativa / signal / rebound / Goodhart / clinamen / moat
    ("hyperobject", "Hyperobject Mouth", "gate-hyperobject-v1",
     "Irreversible spend as viscous nonlocal hyperobject — not a click", "hyperobject.json"),
    ("via_negativa", "Via Negativa Mouth", "gate-via-negativa-v1",
     "Strengthen by subtraction; barbell fail-closed + costly CHARGE tip", "via-negativa.json"),
    ("costly_signal", "Costly Signal Weld", "gate-costly-signal-v1",
     "Paid weld + production flag as unforgeable production signal", "costly-signal.json"),
    ("jevons", "Jevons Restraint", "gate-jevons-v1",
     "Automation rebound attenuated by the mouth alphabet", "jevons.json"),
    ("goodhart", "Goodhart Mouth", "gate-goodhart-v1",
     "Restraint is evidence — never a HALT-volume KPI to hack", "goodhart.json"),
    ("clinamen", "Clinamen CHARGE", "gate-clinamen-v1",
     "CHARGE as Lucretian swerve that breaks soft-yes fate chains", "clinamen.json"),
    ("moat", "Moat Fingerprint", "gate-moat-v1",
     "SHA-256 of the invention identity set — partial clones fail", "moat.json"),
    # Wave 6 — conjugate / adversary / horizon / sign / antifragile / loop / morphism
    ("complementarity", "Complementarity Mouth", "gate-complementarity-v1",
     "CHARGE and HALT as conjugate observables — mouth forces the choice", "complementarity.json"),
    ("adversarial", "Adversarial Weld", "gate-adversarial-v1",
     "Mouth sized for worst licensed skip-clear actor — minimax default", "adversarial.json"),
    ("irreversibility_horizon", "Irreversibility Horizon", "gate-irreversibility-horizon-v1",
     "Measured distance from intention to irreversible act", "irreversibility-horizon.json"),
    ("semiotics", "Semiotics of the Mouth", "gate-semiotics-v1",
     "CHARGE as icon+index+symbol — badges without weld are empty signs", "semiotics.json"),
    ("antifragile_halt", "Antifragile HALT", "gate-antifragile-halt-v1",
     "HALT as strengthening event — buried nos train fragility", "antifragile-halt.json"),
    ("recursive_mouth", "Recursive Mouth", "gate-recursive-mouth-v1",
     "Bounded strange loop: self-clearing economics end at CHARGE", "recursive-mouth.json"),
    ("category_mouth", "Category Mouth", "gate-category-mouth-v1",
     "Clearance as morphism — policies are objects without arrows", "category-mouth.json"),
    # Wave 7 — composure / parasite / apophatic / exergy
    ("negative_capability", "Negative Capability Mouth", "gate-negative-capability-v1",
     "Hold HALT under soft-yes without irritable reaching for CHARGE", "negative-capability.json"),
    ("parasite", "Parasite Filter", "gate-parasite-v1",
     "Exclude soft-yes that feeds on the channel without weld cost", "parasite.json"),
    ("apophatic", "Apophatic Clearance", "gate-apophatic-v1",
     "LIVE speakable only via CHARGE — everything else is not-LIVE", "apophatic.json"),
    ("exergy", "Exergy of Clearance", "gate-exergy-v1",
     "Useful work of status change vs dashboard waste heat", "exergy.json"),
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
