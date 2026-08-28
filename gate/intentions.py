"""Post-survey invention intentions — doctrine catalog only.

Competitive-aware naming for cells still empty after Aug 28 survey.
No demo routes. No L2 modules until Gate 1. See INTENTIONS.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Intention:
    id: str
    title: str
    one_line: str
    vs_survey: str
    rank: int = 0


INTENTIONS: tuple[Intention, ...] = (
    Intention(
        id="cold_standby_mirror",
        title="Cold Standby Mirror",
        one_line=(
            "Read-only witness during outage: proves last HALT + epoch; "
            "cannot mint LIVE or consume tickets."
        ),
        vs_survey="Proof vendors don't ship HALT witness without resurrection power.",
        rank=1,
    ),
    Intention(
        id="renewal_day_throat",
        title="Renewal Day Throat",
        one_line=(
            "Mouth on 03:00 renewal batch — every stick needs fresh ticket + redeem."
        ),
        vs_survey="Agent-mesh papers ignore carrier renewal calendar.",
        rank=2,
    ),
    Intention(
        id="ghost_renewal_snare",
        title="Ghost Renewal Snare",
        one_line="Auto-renew path that would stick without fresh may → CHOKE.",
        vs_survey="Pairs with shipped Ghost Bind; batch-scale soft yes.",
        rank=3,
    ),
    Intention(
        id="halt_cemetery",
        title="HALT Cemetery",
        one_line=(
            "Epoch-locked jobs leave admin-undeletable tombstones for examiners."
        ),
        vs_survey="Operator-revocable blocks everywhere else.",
        rank=4,
    ),
    Intention(
        id="bind_weather",
        title="Bind Weather",
        one_line=(
            "Public carrier dashboard: uptime, redeem p99, HALT depth, maintenance."
        ),
        vs_survey="SLA honesty after fail-closed — not five-nines cosplay.",
        rank=5,
    ),
    Intention(
        id="refuse_ledger",
        title="Refuse Ledger (ρ bind)",
        one_line="Refusal as carrier accounting — binds that didn't happen as line items.",
        vs_survey="PCAA names non_execution_proof; nobody sells ρ on bind.",
        rank=6,
    ),
    Intention(
        id="witness_seat_epoch",
        title="Witness Seat (epoch)",
        one_line="Auditor verifies HALT without CHARGE or consume power.",
        vs_survey="Splits prove from may — dual control.",
        rank=7,
    ),
    Intention(
        id="override_impossibility_packet",
        title="Override Impossibility Packet",
        one_line=(
            "Stranger-verifiable: no path lifts epoch without Velaru CHARGE."
        ),
        vs_survey="Patent prose as weld diligence deliverable.",
        rank=8,
    ),
    Intention(
        id="premium_mass_gate",
        title="Premium Mass Gate (μ bind)",
        one_line="Stick Meter → ticket strictness before redeem on heavy premium.",
        vs_survey="Sacred-media tier on bind mass.",
        rank=9,
    ),
    Intention(
        id="compliance_receipt_twin",
        title="Compliance Receipt Twin",
        one_line="ASQAV envelope welded to epoch lock + redeem in one stranger object.",
        vs_survey="IETF extend made concrete — not stance alone.",
        rank=10,
    ),
    Intention(
        id="interchange_spread_bind",
        title="Interchange Spread (bind)",
        one_line="Cross-mouth bind clearance takes automatic spread — Visa of permission.",
        vs_survey="INVISIBLE_SCALE bedrock applied to insurance.",
        rank=11,
    ),
    Intention(
        id="may_unit_bind_tick",
        title="May Unit Bind Tick (ɱ)",
        one_line="Every bind attempt meters in shared may-mass unit — weather not SKU.",
        vs_survey="ɱ bedrock — permission currency.",
        rank=12,
    ),
)


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    ranked = sorted(INTENTIONS, key=lambda x: x.rank)
    return {
        "spec": "gate-intentions-v1",
        "name": "Post-survey invention intentions",
        "status": "competitive_response_shipped",
        "mouth_ceiling": "Aug 28 survey exception — seven modules shipped; no further L2 until Gate 1.",
        "survey_date": "2026-08-28",
        "thesis": (
            "Crowded on proof. Empty on non-resurrecting HALT at bind + "
            "carrier renewal physics + refusal as accounting."
        ),
        "doc": "gate/INTENTIONS.md",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
        "pick_order_after_gate_1": [
            "cold_standby_mirror",
            "bind_weather",
            "halt_cemetery",
            "refuse_ledger",
            "renewal_day_throat",
        ],
        "intentions": [
            {
                "id": i.id,
                "title": i.title,
                "one_line": i.one_line,
                "vs_survey": i.vs_survey,
                "rank": i.rank,
            }
            for i in ranked
        ],
        "do_not_invent_here": [
            "agent_mesh_capability_tokens",
            "pre_execution_proof_saas",
            "fre_902_hero_receipts",
            "multi_spend_without_rcc",
        ],
    }
