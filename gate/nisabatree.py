"""Nisabatree — plain-English map of everything under Nisaba LLC.

Not a sixth sibling. Not a checkout. Explain-to-anyone surface.
Source of truth prose: NISABATREE.md
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

SPEC = "nisaba-nisabatree-v1"
INVENTOR = inventor_mod.INVENTOR["entity"]
INVENTOR_NAME = inventor_mod.INVENTOR["name"]
PATENT = inventor_mod.INVENTOR.get("patent", "64/124,027")

CLEVERER_LAYER = None
THEIR_PRODUCTION = False
FAMILY = ("Velaru", "Erra", "Verra", "Gate", "Mishara")
PRIMITIVE = ("may", "sheath", "prove")
NEVER_SELL = ("may", "the throat", "critical planetary capacity")

ONE_SENTENCE = (
    "I built a lock for irreversible computer actions — money moves, deletes, "
    "sends, binds — so a stranger can open a receipt that proves the action "
    "was allowed or stopped."
)

SHORTER = "Proof that an AI was allowed (or blocked) before it did something it can't undo."

BOTH = (
    "Work on the world's biggest remaining — clock, Moon, delay, the after — "
    "and do not neglect what a person needs to live: sleep, kin, a receipt when "
    "they couldn't watch, first cash so the inventor eats. Wonder without the "
    "body is abandonment. Body without wonder is a smaller company than this one."
)

BRANDS = (
    {
        "name": "Velaru",
        "question": "Did we record it right?",
        "job": "Proof engine. Receipts neither side forges alone.",
    },
    {
        "name": "Erra",
        "question": "Should we act?",
        "job": "Signal before money or force moves. ACT or HOLD.",
    },
    {
        "name": "Verra",
        "question": "Did both rails clear before we bind?",
        "job": "The room where signal + proof must both clear — one export.",
    },
    {
        "name": "Gate",
        "question": "Can this agent still act right now?",
        "job": "Mouth / kill door on irreversible writes. DENY is the scarcity.",
    },
    {
        "name": "Mishara",
        "question": "Was a person harmed?",
        "job": "Human path after harm — receipt + demand, not corporate Action OS.",
    },
)

ORGANS = (
    {"name": "May", "job": "Permission ticket for one irreversible act"},
    {"name": "Redeem", "job": "Spend the ticket at the irreversible moment"},
    {"name": "Prove", "job": "Stranger-openable receipt"},
    {"name": "Remaining", "job": "The world after the act (books, not just the journal line)"},
    {"name": "Inhabitant", "job": "Someone who lives in the consequences — they get a copy"},
)

CASH_NOW = (
    {"sku": "Bind Room", "price": "$1,750", "line": "Officer pack + stranger receipt. Highest-probability Gate 1."},
    {"sku": "Install sprint", "price": "$2,500", "line": "Kill-switch on one write in ~48 hours."},
    {"sku": "Broker three-pack", "price": "$4,500", "line": "One broker, three AI names."},
    {"sku": "Standing write / book / desk", "price": "$4,500–$25,000/mo", "line": "Keep remaining live every month."},
    {"sku": "Finished Remaining", "price": "$8,500", "line": "We operate one write; they attach the folio."},
    {"sku": "Refusal", "price": "$7,500", "line": "Signed will-not-ship unbound agent."},
    {"sku": "Null", "price": "$4,500", "line": "Sealed record of a killed project."},
    {"sku": "Estate", "price": "$3,500", "line": "Bearer gone — probate the remaining."},
    {"sku": "Discharge", "price": "$1,500", "line": "Standing lapses; record stays."},
    {"sku": "Operator weld", "price": "$25k + $5k/mo", "line": "Only if they implement payout/withdraw."},
)

GLOSSARY = (
    ("Gate 1", "First stranger paid + proved."),
    ("May", "Permission to do the irreversible thing this once."),
    ("Sheath", "Wrap that forces the action through the lock."),
    ("Prove", "A stranger can open the receipt without calling you."),
    ("Remaining", "What’s left in the world after the act."),
    ("Conformant", "Badge: this system meets Gate’s lock standard."),
    ("QIC", "Meter unit: one redeem + one irreversible write."),
    ("Bind Room", "$1,750 pack + stranger receipt for underwriters."),
    ("Bridge", "Forced attach. A close that cannot complete without redeem. Not a new SKU. /bridge"),
    ("Cleverer layer", "Forbidden. Null. Being is not a SKU."),
)

FIGHT_FOR_22 = {
    "bridge_liquid": "$5–40M",
    "aim_liquid": "$50–200M",
    "fat_liquid": "$200–800M",
    "padlock": "$0.5–2B",
}

ONE_BREATH = (
    "Nisaba is Demond Davis’s company. Five brands ask five questions about "
    "irreversible AI acts. The product this month is Bind $1,750. The lock words "
    "are may · sheath · prove. Never sell may. First stranger paid and proved = "
    "Gate 1. Everything prettier sits on the shelf until then."
)


def manifest(public_url: str = "") -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "nisabatree",
        "title": "Nisabatree — Nisaba in plain English",
        "thesis": ONE_SENTENCE,
        "shorter": SHORTER,
        "both": BOTH,
        "one_breath": ONE_BREATH,
        "inventor": {
            "name": INVENTOR_NAME,
            "entity": INVENTOR,
            "patent": PATENT,
        },
        "primitive": list(PRIMITIVE),
        "never_sell": list(NEVER_SELL),
        "family": list(FAMILY),
        "brands": list(BRANDS),
        "organs": list(ORGANS),
        "cash_now": list(CASH_NOW),
        "glossary": [{"term": t, "plain": p} for t, p in GLOSSARY],
        "fight_for_22": FIGHT_FOR_22,
        "cleverer_layer": CLEVERER_LAYER,
        "their_production": THEIR_PRODUCTION,
        "gate1": "stranger paid and proved",
        "not_a_product": True,
        "checkout": None,
        "page": f"{base}/nisabatree" if base else "/nisabatree",
        "well_known": f"{base}/.well-known/nisabatree.json" if base else "/.well-known/nisabatree.json",
        "source_md": "gate/NISABATREE.md",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


def page_blocks() -> list[dict[str, Any]]:
    return [
        {
            "id": "who",
            "heading": "Who",
            "body": (
                f"{INVENTOR_NAME} · {INVENTOR} (Wyoming) · patent {PATENT}. "
                "You stay named. Nisaba is the holding company — not a sixth public brand."
            ),
        },
        {
            "id": "one-sentence",
            "heading": "One sentence",
            "body": ONE_SENTENCE,
        },
        {
            "id": "both",
            "heading": "Wonders and necessities",
            "body": BOTH,
        },
        {
            "id": "family",
            "heading": "Five brands (always five)",
            "body": "Velaru proves. Erra asks should we. Verra forces both rails. Gate owns the door. Mishara is for the harmed human.",
        },
        {
            "id": "primitive",
            "heading": "Three baby words",
            "body": "may · sheath · prove. Never sell may. Never sell the throat.",
        },
        {
            "id": "cash",
            "heading": "This month",
            "body": "Bind Room $1,750 is the highest-probability Gate 1. Standing / Finished / Refusal / Null / Estate / Discharge are already seated. Operator only if they implement.",
        },
        {
            "id": "gate1",
            "heading": "Gate 1",
            "body": "First stranger paid and proved. Until then their_production is false and big doctrine is museum.",
        },
        {
            "id": "money",
            "heading": "Fight-for money (shapes)",
            "body": (
                f"Age ~22 Aim liquid {FIGHT_FOR_22['aim_liquid']} · Fat {FIGHT_FOR_22['fat_liquid']} · "
                f"Padlock {FIGHT_FOR_22['padlock']}. $0 without Gate 1."
            ),
        },
        {
            "id": "one-breath",
            "heading": "One breath",
            "body": ONE_BREATH,
        },
    ]
