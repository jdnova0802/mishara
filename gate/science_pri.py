"""Science → Gate mouth — PRI, fail-closed, thermo intervention, driver nodes.

Motive: contribute massively to Tier-S continuity *with* coordinators —
collaborate as the clearance mouth, never replace state monopolies.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "nisaba-science-pri-v1"
INVENTOR = "Nisaba LLC / Gate"

# Contribution altitude — not ownership
MOTIVE = (
    "Contribute massively to Tier-S continuity as a favor to global coordinators. "
    "Collaborate. Do not replace C2, nukes, grid, or link monopolies."
)

FORMULA = (
    "Inhibit unjustified irreversible acts (PRI) — fail-closed — "
    "as a driver-node mouth on the act graph, not a hub dashboard."
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


SCIENCE = (
    {
        "id": "pri",
        "name": "Pre-Irreversibility Inhibition (PRI)",
        "claim": (
            "Catastrophe often comes from acting when epistemic adequacy cannot "
            "justify irreversible commitment. PRI makes restraint an architectural primitive."
        ),
        "refs": [
            {
                "title": "Pre-Irreversibility Inhibition (PRI)",
                "url": "https://doi.org/10.5281/zenodo.18013606",
            }
        ],
        "gate_law": (
            "execute(a) iff LIVE(a) and justified(a); else DENY. bypass(a)=empty. "
            "CHARGE-only re-open."
        ),
    },
    {
        "id": "fail_closed",
        "name": "Fail-closed (fail-secure) under uncertainty",
        "claim": (
            "Under control failure, default DENY. Attackers manufacture uncertainty "
            "to fish for fail-open. Availability loss beats silent LIVE."
        ),
        "refs": [
            {
                "title": "Fail-open vs fail-closed authorization",
                "url": "https://authzed.com/blog/fail-open",
            }
        ],
        "gate_law": "uncertainty(u) => DENY. Life-safety overrides are explicit coordinator lanes, not soft-yes.",
    },
    {
        "id": "thermo_intervention",
        "name": "Thermodynamic cost of causal intervention",
        "claim": (
            "Pearl-perfect surgical do(.) is physically impossible. Real intervention "
            "is measure+control+dissipation; causation rides the entropy arrow."
        ),
        "refs": [
            {
                "title": "Classical and Quantum Causal Interventions",
                "url": "https://doi.org/10.3390/e20090687",
            }
        ],
        "gate_law": (
            "intervention = measure(evidence) -> control(LIVE|DENY) -> record(receipt). "
            "Silent free yes is illegal. Weld + bps price authority dissipation."
        ),
    },
    {
        "id": "driver_nodes",
        "name": "Driver nodes (Liu–Slotine–Barabási)",
        "claim": (
            "Network controllability needs a minimum driver set. Drivers often avoid hubs. "
            "Sparse heterogeneous systems are hard to control."
        ),
        "refs": [
            {
                "title": "Controllability of complex networks",
                "url": "https://doi.org/10.1038/nature10011",
            }
        ],
        "gate_law": (
            "Gate is a driver on InstitutionalActGraph edges (irreversible writes). "
            "Hub dashboards are not drivers. Weld one act-edge at a time."
        ),
    },
    {
        "id": "quorum_mouth",
        "name": "Quorum / unfireable mouth",
        "claim": (
            "Authority as structured quorum, not one charismatic key. Safety kernels "
            "must sit outside the actor's invoke path — fail-closed externally."
        ),
        "refs": [
            {
                "title": "Threshold / quorum authorization (distributed custody)",
                "url": "https://arxiv.org/html/2607.08226v1",
            }
        ],
        "gate_law": (
            "LIVE <= quorum(policy) AND CHARGE(packet) AND mouth(Gate). "
            "Stranger-verify evidence outside actor trust boundary (Velaru)."
        ),
    },
)

# Tier S — contribute, do not own
TIER_S = (
    {
        "id": "nuclear_c2",
        "name": "Nuclear C2 / launch auth",
        "own": False,
        "contribute": (
            "Nearly closed. Possible only as tiny subcontracted component under state/"
            "primes someday — never Gate-as-football."
        ),
        "priority": 0,
    },
    {
        "id": "mil_comms",
        "name": "Strategic military comms / C2 restore",
        "own": False,
        "contribute": (
            "Long-term: fail-closed clearance mouth on release/authorize edges under "
            "DoD/prime programs. They keep C2; we inhibit unjustified irreversible release."
        ),
        "priority": 2,
    },
    {
        "id": "grid",
        "name": "Grid blackstart / shed-reconnect",
        "own": False,
        "contribute": (
            "Best near-term Tier-S-adjacent favor: PRI on shed/reconnect authorization "
            "with utilities — irreversible power acts."
        ),
        "priority": 3,
    },
    {
        "id": "link",
        "name": "Global hardened link (satcom class)",
        "own": False,
        "contribute": (
            "Do not rebuild constellations. Optional later: auth layer on irreversible "
            "link/priority ops — collaborate with link operators."
        ),
        "priority": 1,
    },
)

CONTRIBUTE_LADDER = (
    {
        "step": 1,
        "title": "Commercial driver weld",
        "do": "Weld Gate as PRI on one irreversible money/bind write. Prove DENY holds.",
        "tier": "foundation",
    },
    {
        "step": 2,
        "title": "Critical infra mouth",
        "do": "Offer the same mouth on grid shed/reconnect or wholesale settlement finality.",
        "tier": "A/S-adjacent",
    },
    {
        "step": 3,
        "title": "Named COOP function",
        "do": "Get 'clears via Gate' into coordinator continuity docs. Cleared custodians.",
        "tier": "continuity",
    },
    {
        "step": 4,
        "title": "Defense/comms release mouth",
        "do": "Collaborate under programs — inhibit unjustified release. force_production_weld stays false until real.",
        "tier": "S-contribute",
    },
)

DISTRIBUTION = (
    {
        "rule": "Sell PRI to coordinators",
        "detail": "Operators who already clear writes — banks, utilities, program offices — not consumers.",
    },
    {
        "rule": "Land on the weld",
        "detail": "/operator — one door. Fail-closed story. No Tier-S ownership cosplay in ads.",
    },
    {
        "rule": "Find driver edges, not hubs",
        "detail": "Map ActGraph; weld unmatched irreversible writes. Skip vanity logos off the write path.",
    },
    {
        "rule": "Price dissipation",
        "detail": "Weld + bps = thermodynamic toll on sorting LIVE/DENY — not seat licenses.",
    },
    {
        "rule": "Contribute path explicit",
        "detail": "Copy and contracts say collaborate with state/monopoly holders; mouth only.",
    },
)


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Science → mouth (PRI)",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "motive": MOTIVE,
        "formula": FORMULA,
        "science": list(SCIENCE),
        "tier_s": list(TIER_S),
        "contribute_ladder": list(CONTRIBUTE_LADDER),
        "distribution": list(DISTRIBUTION),
        "own_tier_s": False,
        "force_production_weld": False,
        "their_production": False,
        "one_liner": (
            "Massive Tier-S contribution = PRI mouth welded under coordinators — "
            "favor, not throne."
        ),
        "links": {
            "action_os": f"{base}/.well-known/action-os.json",
            "proof": f"{base}/.well-known/proof-suite.json",
            "operator": f"{base}/operator",
            "runbook": f"{base}/runbook",
            "page": f"{base}/science",
        },
        "page": f"{base}/science",
        "gatekeep": "Science applied. Mouth only. Contribute to S. Ours.",
    }


def page_blocks() -> list[dict[str, Any]]:
    return [
        {"tag": "Science", "title": s["name"], "body": s["gate_law"], "id": s["id"]}
        for s in SCIENCE
    ]
