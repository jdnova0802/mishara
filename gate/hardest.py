"""Hardest bites on the globe — irreversible problems Gate exists to mouth.

Research sources (2024–2026): BIS Triennial FX settlement risk, CLS Herstatt,
Oxford OBLB legal finality vs technical finality, FedNow OC 8 irrevocability,
arXiv 2605.01415 control of irreversibility, Feaver always/never, Guidewire Bound.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-hardest-bites-v1"
INVENTOR = "Nisaba LLC / Gate"

# Ranked by: cost of reversal × opacity of single node × underserved by market.
HARDEST: tuple[dict[str, Any], ...] = (
    {
        "rank": 1,
        "id": "herstatt_fx",
        "name": "Herstatt / FX principal risk",
        "hardness": "civilizational",
        "scale": "~$1.4T/day still gross bilateral without PvP elimination (BIS 2025)",
        "why_hard": (
            "Pay one currency, never receive the other. Fifty years after Herstatt Bank. "
            "CLS covers majors; EME pairs, T+0 FX, and access gaps remain."
        ),
        "market_status": "CLS + bilateral DLT PvP experiments — still incomplete",
        "gate_bite": "pvp_mouth",
        "gate_claim": (
            "Gate does not replace CLS. It mouths each irreversible FX leg before release — "
            "PERMISSION and COUNTERPARTY legs linked like DvP. No solo pay-away."
        ),
    },
    {
        "rank": 2,
        "id": "legal_vs_technical_finality",
        "name": "Legal finality ≠ ledger finality",
        "hardness": "civilizational",
        "scale": "G20 cross-border 2027 goals blocked by law, not tech (Oxford OBLB 2026)",
        "why_hard": (
            "Zero-hour / insolvency can unwind a transfer that systems treated as complete. "
            "Technical LIVE is not legal irrevocability across jurisdictions."
        ),
        "market_status": "Settlement Finality Directive islands; EME gaps; wCBDC unfinished",
        "gate_bite": "legal_finality",
        "gate_claim": (
            "Mouth stamps technical regime separately from legal finality claims. "
            "CHARGE is the only costly witness that may change regime — not a court cosplay."
        ),
    },
    {
        "rank": 3,
        "id": "instant_rail_irrevocability",
        "name": "FedNow / RTP / instant-rail finality",
        "hardness": "systemic",
        "scale": "Settlement final when debits/credits record (Fed OC 8) — seconds",
        "why_hard": (
            "No ACH return window. No float. Post-hoc kill governs nothing — money is gone."
        ),
        "market_status": "Spend firewalls with soft caps; few CHARGE-only mouths",
        "gate_bite": "fednow_mouth",
        "gate_claim": (
            "Pre-release mouth on withdraw/payout to irrevocable rails. "
            "Timeout → HALT. Soft-yes cannot resurrect."
        ),
    },
    {
        "rank": 4,
        "id": "authority_vs_ability",
        "name": "Authority without ability (two-key / PAL)",
        "hardness": "systemic",
        "scale": "Nuclear NC2 pattern; agent production deletes without second key",
        "why_hard": (
            "Single opaque node holds both plan-authority and execute-ability. "
            "Always-work-when-ordered / never-when-not (Feaver) fails."
        ),
        "market_status": "Blog-tier two-person rules; rare as product physics",
        "gate_bite": "pal_charge",
        "gate_claim": (
            "Ability to execute sits behind exclusive door. Authority to LIVE is CHARGE only. "
            "Split identities — never one operator with both."
        ),
    },
    {
        "rank": 5,
        "id": "self_expansion",
        "name": "Self-expansion of LIVE authority",
        "hardness": "systemic",
        "scale": "arXiv 2605.01415 sovereignty boundary S_exp",
        "why_hard": (
            "Agents that can widen their own permissions, replicate credentials, or promote "
            "themselves past the mouth concentrate decision-energy fatally."
        ),
        "market_status": "Almost vacant as product invariant",
        "gate_bite": "self_expansion_ban",
        "gate_claim": (
            "Userspace cannot promote to LIVE. Privilege ring 0 is CHARGE. "
            "Self-issued LIVE is illegal opcode."
        ),
    },
    {
        "rank": 6,
        "id": "spent_bind_all_doors",
        "name": "All PAS spent-world doors",
        "hardness": "industry",
        "scale": "bind-only → Bound; UI Bind; midnight RenewalWF — three skip-clears",
        "why_hard": (
            "API wrappers miss UI and renewal. One leak path = legally Bound without mouth."
        ),
        "market_status": "Inventory/governance tools; incomplete door closure",
        "gate_bite": "all_doors",
        "gate_claim": (
            "One exclusive door across Cloud API bind-only, UI Bind paste, RenewalWF step. "
            "Not a happy-path integration."
        ),
    },
    {
        "rank": 7,
        "id": "instruction_before_exception",
        "name": "Instruction that becomes the exception",
        "hardness": "industry",
        "scale": "Europe T+1: 2–5hr exception window; SSI/enrichment after confirmation",
        "why_hard": (
            "ALERT fixes reference data. Exceptions still born from instructions admitted wrong."
        ),
        "market_status": "SSI automation + faster tickets — not refuse-to-admit",
        "gate_bite": "pre_net_clearance",
        "gate_claim": (
            "Filter gross before the net. Do not mint the exception ticket."
        ),
    },
    {
        "rank": 8,
        "id": "delegation_tree",
        "name": "Delegated authority kill tree",
        "hardness": "industry",
        "scale": "MGA pen, FedNow OC8 Service Providers, agent swarms",
        "why_hard": (
            "Revoking one session leaves children LIVE. Ruin lives in the tree."
        ),
        "market_status": "Per-agent kill; rare parent→child fuse",
        "gate_bite": "enabling",
        "gate_claim": (
            "Parent DEAD → children cannot spend until CHARGE. Enabling grip."
        ),
    },
    {
        "rank": 9,
        "id": "proof_of_restraint",
        "name": "Proof of non-spend (counterfactual)",
        "hardness": "legal",
        "scale": "NAIC decision-point; EU Art 12; examiner 'could they act?'",
        "why_hard": (
            "Absence in a log proves nothing. Courts need signed inaction within a boundary."
        ),
        "market_status": "Emerging papers; thin production artifacts",
        "gate_bite": "counterfactual",
        "gate_claim": (
            "Counterfactual spend receipt + stranger verify. HALT is evidence."
        ),
    },
    {
        "rank": 10,
        "id": "decision_energy_node",
        "name": "Single opaque decision-energy node",
        "hardness": "civilizational",
        "scale": "arXiv 2605.01415 — irreversibility control under rising decision density",
        "why_hard": (
            "Efficiency concentrates consequential decisions in one high-density node. "
            "Local error rates stay low while system-level loss rises."
        ),
        "market_status": "Academic framing; almost no commercial mouth",
        "gate_bite": "decision_energy",
        "gate_claim": (
            "Irreversible alphabet is finite: ALLOW/HALT/BLOCK/CHARGE. "
            "Bound decision-energy at the exclusive door — not soft dashboards."
        ),
    },
    {
        "rank": 11,
        "id": "always_never",
        "name": "Always when ordered / never when not",
        "hardness": "systemic",
        "scale": "Feaver NC2 property — 'mostly works' is broken",
        "why_hard": (
            "Mouth that works 99% and soft-yes the rest fails the never clause."
        ),
        "market_status": "Aspirational; timeout-as-LIVE common",
        "gate_bite": "always_never",
        "gate_claim": (
            "Fail-closed is the never. CHARGE is the only always-path to LIVE. "
            "Timeout/5xx → HALT — never UNREACHABLE as LIVE."
        ),
    },
    {
        "rank": 12,
        "id": "atomic_vs_netting",
        "name": "Atomic T+0 vs multilateral netting",
        "hardness": "industry",
        "scale": "Markets need both; atomic alone kills capital efficiency",
        "why_hard": (
            "Pure atomic settlement removes Herstatt but breaks CNS-style netting. "
            "Lying about replacing the net loses DTCC peers."
        ),
        "market_status": "Either/or hype; few honest dual stacks",
        "gate_bite": "t0_honesty",
        "gate_claim": (
            "We do not replace your net. Pre-net mouth + atomic honesty on irrevocable rails. "
            "Two modes, one alphabet."
        ),
    },
)


_SOLUTION_FILES = {
    "pvp_mouth": "pvp-mouth.json",
    "legal_finality": "legal-finality.json",
    "fednow_mouth": "fednow-mouth.json",
    "pal_charge": "pal-charge.json",
    "self_expansion_ban": "self-expansion-ban.json",
    "all_doors": "all-doors.json",
    "pre_net_clearance": "pre-net-clearance.json",
    "enabling": "enabling.json",
    "counterfactual": "counterfactual-spend.json",
    "decision_energy": "decision-energy.json",
    "always_never": "always-never.json",
    "t0_honesty": "t0-honesty.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    bites = []
    for h in HARDEST:
        fname = _SOLUTION_FILES.get(h["gate_bite"], h["gate_bite"].replace("_", "-") + ".json")
        bites.append(
            {
                **h,
                "solution_href": f"{base}/.well-known/{fname}" if base else None,
            }
        )
    return {
        "spec": SPEC,
        "name": "Hardest bites on the globe",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "thesis": (
            "Find the irreversible problems civilization cannot soft-yes away. "
            "Mouth each before anyone else ships a dashboard costume."
        ),
        "count": len(bites),
        "bites": bites,
        "public_face": f"{base}/.well-known/public-face.json" if base else None,
        "page": f"{base}/hardest" if base else None,
        "their_production": False,
        "gatekeep": "Proprietary hardest-bite catalog. Ours.",
    }
