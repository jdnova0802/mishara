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
    # Wave 8 — individuation / exception / bind / cut / mimesis / Illich / Ellul / Whitehead / spheres / modes
    ("metastable", "Metastable HALT", "gate-metastable-v1",
     "DEAD as supersaturated potential; CHARGE as costly nucleation", "metastable.json"),
    ("sovereign_exception", "Sovereign Exception CHARGE", "gate-sovereign-exception-v1",
     "DEAD is the norm; CHARGE is the sole lawful exception to LIVE", "sovereign-exception.json"),
    ("double_bind", "Double-Bind Dissolver", "gate-double-bind-v1",
     "Mouth alphabet cuts fail-closed vs never-block-revenue binds", "double-bind.json"),
    ("agential_cut", "Agential Cut CHARGE", "gate-agential-cut-v1",
     "CHARGE enacts the cut that makes LIVE/DEAD matter — not observation", "agential-cut.json"),
    ("mimetic", "Mimetic Soft-Yes Breaker", "gate-mimetic-v1",
     "Break the race to imitate cheap approval with focal clear-before-wire", "mimetic.json"),
    ("counterproductivity", "Counterproductivity Threshold", "gate-counterproductivity-v1",
     "Past a point, more controls worsen bypass — mouth is the threshold", "counterproductivity.json"),
    ("technique_limit", "Technique Limit", "gate-technique-limit-v1",
     "Mouth as exterior limit on autonomous automation technique", "technique-limit.json"),
    ("prehension", "Prehension Receipt", "gate-prehension-v1",
     "Receipt publicly feels the spent world — not a mute log line", "prehension.json"),
    ("immunological", "Immunological Weld", "gate-immunological-v1",
     "Weld as immune membrane; production without it is autoimmune", "immunological.json"),
    ("convivial", "Convivial Mouth", "gate-convivial-v1",
     "Public alphabet + human CHARGE enlarges refusal competence", "convivial.json"),
    ("modes", "Modes of Clearance", "gate-modes-v1",
     "TEC hop success is not LAW permission — refuse mode smuggling", "modes.json"),
    # Wave 9 — xenohardware: alien apparatus, not dashboard fauna
    ("xenohardware", "Xenohardware Chassis", "gate-xenohardware-v1",
     "Mouth as sealed apparatus with illegal-port traps — not a themeable UI", "xenohardware.json"),
    ("mouth_isa", "Mouth ISA", "gate-mouth-isa-v1",
     "Closed opcode set ALLOW/HALT/BLOCK/CHARGE — soft-yes traps", "mouth-isa.json"),
    ("privilege_rings", "Privilege Rings of Spend", "gate-privilege-rings-v1",
     "Ring 0 is CHARGE; userspace cannot promote itself to LIVE", "privilege-rings.json"),
    ("isotopic_charge", "Isotopic CHARGE", "gate-isotopic-charge-v1",
     "LIVE cannot be cooked from demo feedstock — CHARGE is an isotope", "isotopic-charge.json"),
    ("monolith", "Monolith Interface", "gate-monolith-v1",
     "Two ports only: exclusive door + CHARGE — no dashboard fauna", "monolith.json"),
    ("zone_artifact", "Zone Artifact", "gate-zone-artifact-v1",
     "Weld physics is not a backlog item — you approach, you do not picnic", "zone-artifact.json"),
    ("contact_protocol", "Contact Protocol", "gate-contact-protocol-v1",
     "First contact with irreversible spend is a handshake, not Slack LGTM", "contact-protocol.json"),
    ("event_horizon", "Event Horizon Fuse", "gate-event-horizon-v1",
     "Past CHARGE, skip-clear rewrites do not return", "event-horizon.json"),
    ("nonorientable", "Non-Orientable Door", "gate-nonorientable-v1",
     "Möbius exclusive door — no backside for skip-clear", "nonorientable.json"),
    ("vacuum", "Vacuum Integrity", "gate-vacuum-v1",
     "Fail-closed as hard vacuum — timeout-as-LIVE is hull breach", "vacuum.json"),
    ("stranger_antenna", "Stranger Antenna", "gate-stranger-antenna-v1",
     "Verify as public xenoreceiver — login walls kill the beacon", "stranger-antenna.json"),
    ("incommensurable", "Incommensurable Alphabet", "gate-incommensurable-v1",
     "ALLOW/HALT/BLOCK does not gloss into KPI English", "incommensurable.json"),
    ("firmware_fuse", "Firmware Fuse", "gate-firmware-fuse-v1",
     "LIVE is write-once flash — runtime flags are jailbreaks", "firmware-fuse.json"),
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
