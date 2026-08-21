"""Science + tech → Gate clearance — PRI, frontiers, named first weld.

Motive: contribute to Tier-S continuity with coordinators —
clearance path under their stacks, never replace state monopolies.
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

# Capability tech is exploding; scarce layer is non-bypassable LIVE/DENY.
TECH_THESIS = (
    "Frontiers multiply what systems *can* do. Gate owns the mouth between "
    "can and may — contribute under each stack; do not own their guns."
)

# Named first commercial driver — strategy lock for the night
FIRST_WELD = {
    "id": "withdraw_payout_clear",
    "write": "withdraw",
    "label": "Withdraw / payout — clear before wire",
    "why": (
        "First commercial path: irreversible money leave. "
        "Prove fail-closed clearance on one payout path before grid or programs."
    ),
    "example_path": "POST /v1/payouts/{id}/release",
    "checkout": "/operator?write=withdraw",
    "next_after_prove": "grid_shed_reconnect",
    "not": [
        "grid blackstart (step 2 / Tier-S-adjacent)",
        "milcomms release mouth (ladder step 4)",
        "nuclear C2 (state only)",
    ],
}


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
        "title": "Commercial driver weld — payout clear",
        "do": (
            "Weld Gate as PRI on withdraw/payout clear-before-wire. "
            "Prove DENY holds. This is the named first edge."
        ),
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

TECH = (
    {
        "id": "agent_control",
        "name": "AI agent control planes / MCP firewalls",
        "frontier": (
            "Agents invoke tools at machine speed. Signed decision certs and "
            "tool firewalls are rising — still often bypassable soft policy."
        ),
        "gate_mouth": (
            "LIVE/DENY on irreversible agent writes (spend, bind, release). "
            "MCP fuse is the hop; Gate is the mouth. Soft prompt policy ≠ DENY."
        ),
        "own": False,
        "contribute": "Clearance mouth under operator tool graphs — not the model vendor.",
    },
    {
        "id": "grid_forming",
        "name": "Grid-forming inverters + smart breakers",
        "frontier": (
            "GFM + autonomous blackstart hardware can reclose power without a "
            "human on every breaker — capability ahead of justified commit."
        ),
        "gate_mouth": (
            "PRI on shed/reconnect authorization edges. Hardware can; mouth may. "
            "Best near-term Tier-S-adjacent favor after commercial payout prove."
        ),
        "own": False,
        "contribute": "Under utilities ISO/RTO — never own the grid.",
    },
    {
        "id": "leo_mesh",
        "name": "Military LEO mesh / Space Data Network class",
        "frontier": (
            "Hardened LEO meshes and SDN-class programs multiply link + C2 restore "
            "options. Bandwidth is not authorization physics."
        ),
        "gate_mouth": (
            "Optional later: fail-closed clearance on irreversible link/priority/"
            "release ops under program offices — they keep the constellation."
        ),
        "own": False,
        "contribute": "Auth layer under milcomms programs — not Starshield replacement.",
    },
    {
        "id": "tee_mpc_hsm",
        "name": "TEE + MPC + HSM post-quantum custody",
        "frontier": (
            "Enclaves, MPC, and PQ HSM harden *who can sign*. Still need a mouth "
            "for *whether the irreversible act may fire*."
        ),
        "gate_mouth": (
            "Custody proves keys; Gate proves LIVE. Quorum + CHARGE + stranger "
            "receipt — soft HSM policy alone is not PRI."
        ),
        "own": False,
        "contribute": "Mouth beside custody stacks — not a competing vault product.",
    },
    {
        "id": "pd_kinetic",
        "name": "Planetary-defense kinetic GNC (DART lineage)",
        "frontier": (
            "Kinetic commit is one-shot irreversible. Guidance tech improves; "
            "unjustified commit remains civilization-scale PRI."
        ),
        "gate_mouth": (
            "Conceptual only: inhibit unjustified irreversible commit under "
            "state/program authority. Never private PD command."
        ),
        "own": False,
        "contribute": "Doctrine alignment / tiny component someday — state owns the shot.",
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
        "rule": "First weld is payout clear",
        "detail": (
            "Named edge: withdraw/payout clear-before-wire. Prove DENY. "
            "Grid shed/reconnect is next, not first."
        ),
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
    {
        "rule": "Ads floor before spend",
        "detail": "/privacy + /terms stubs live; their_production false on creative; pixels off by default.",
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
        "tech_thesis": TECH_THESIS,
        "science": list(SCIENCE),
        "tech": list(TECH),
        "first_weld": dict(FIRST_WELD),
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
            "privacy": f"{base}/privacy",
            "terms": f"{base}/terms",
            "page": f"{base}/science",
        },
        "page": f"{base}/science",
        "gatekeep": "Science + tech applied. Mouth only. First weld = payout clear. Contribute to S.",
    }


def page_blocks() -> list[dict[str, Any]]:
    blocks = [
        {"tag": "Science", "title": s["name"], "body": s["gate_law"], "id": s["id"]}
        for s in SCIENCE
    ]
    blocks.extend(
        {
            "tag": "Tech",
            "title": t["name"],
            "body": t["gate_mouth"],
            "id": t["id"],
        }
        for t in TECH
    )
    return blocks
