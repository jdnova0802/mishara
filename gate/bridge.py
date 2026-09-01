"""Meter → Aim bridge — forced attach at irreversibility.

Not a new SKU. Not a sixth sibling. Not an L2 museum module.
Cash still lives on Bind / Standing / Operator. This door names the gap
and points at those checkouts.

$0 until Gate 1. Never sell may. Never sell interchange from Bind.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

try:
    from gate import bind_room as bind_room_mod
except ImportError:
    import bind_room as bind_room_mod

try:
    from gate import operator_invoice as operator_mod
except ImportError:
    import operator_invoice as operator_mod

SPEC = "nisaba-bridge-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
THEIR_PRODUCTION = False
CLEVERER_LAYER = None
CASH_USD = 0

THESIS = (
    "Meter is hops. Aim is a buyer. The bridge is forced attach — "
    "a close that cannot complete without redeem."
)

HALT = (
    "We will not sell may. We will not sell interchange from this page. "
    "We will not implement the whole rail on Bind."
)

SEATS = (
    {
        "id": "s4_insurability",
        "name": "Insurability gate",
        "job": "No act+remaining folio ⇒ uninsurable. You are not the carrier.",
        "door": "/bind-room",
        "also": "/standing",
        "pick": "Bind / Standing as the required pack",
    },
    {
        "id": "s3_hosted_redeem",
        "name": "Hosted redeem",
        "job": "You are the hop. 10 bps + QIC on one live desk.",
        "door": "/operator",
        "also": None,
        "pick": "Operator weld — they implement",
    },
    {
        "id": "closing_dependency",
        "name": "Closing dependency",
        "job": "Redeemed may is the act. No redeem, no binder / withdraw.",
        "door": "/operator",
        "also": "/finished",
        "pick": "Same throat as the seat you picked",
    },
)

BANDS = {
    "miss": {"liquid": "$0", "when": "No Gate 1"},
    "meter": {
        "liquid": "$0.1–20M",
        "when": "S03 / QIC / one small–mid desk",
    },
    "bridge": {
        "liquid": "$5–40M",
        "when": (
            "One close depends on you before June — bps + standing + evidence, "
            "or an option mark on that attach. Sale not required."
        ),
    },
    "aim": {
        "liquid": "$50–200M",
        "when": "Conformant foothold + rail + secondary/acq",
    },
}

ASKS = (
    {
        "sku": "Bind Room",
        "price": "$1,750",
        "door": "/bind-room",
        "line": "Gate 1. No pack, no cover.",
    },
    {
        "sku": "Standing write",
        "price": "$4,500/mo",
        "door": "/standing",
        "line": "They stay. We keep the remaining true.",
    },
    {
        "sku": "Operator weld",
        "price": "$25,000 + $5,000/mo",
        "door": "/operator",
        "line": "Only if they implement payout / withdraw.",
    },
)


def _base(public_url: str) -> str:
    return (public_url or "").rstrip("/")


def manifest(public_url: str = "") -> dict[str, Any]:
    base = _base(public_url)
    return {
        "spec": SPEC,
        "name": "bridge",
        "title": "The Bridge — forced attach at irreversibility",
        "thesis": THESIS,
        "halt": HALT,
        "inventor": inventor_mod.INVENTOR["name"],
        "entity": inventor_mod.INVENTOR["entity"],
        "patent": inventor_mod.INVENTOR.get("patent", "64/124,027"),
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "their_production": THEIR_PRODUCTION,
        "cash_usd": CASH_USD,
        "until_gate1_usd": 0,
        "new_sku": False,
        "new_price_id": False,
        "pick_one_seat": True,
        "seats": [dict(s) for s in SEATS],
        "bands": BANDS,
        "asks": [dict(a) for a in ASKS],
        "stranger_two": bind_room_mod.stranger_two(public_url),
        "operator": {
            "weld": getattr(operator_mod, "WELD_PRICE_LABEL", "$25,000"),
            "floor": getattr(operator_mod, "FLOOR_PRICE_LABEL", "$5,000/mo"),
        },
        "not": [
            "a new checkout",
            "interchange sold from Bind",
            "Afterweb as a store",
            "a sixth sibling",
            "a June-only wire",
        ],
        "page": f"{base}/bridge" if base else "/bridge",
        "well_known": f"{base}/.well-known/bridge.json" if base else "/.well-known/bridge.json",
        "cash_doors": {
            "bind_room": f"{base}/bind-room" if base else "/bind-room",
            "standing": f"{base}/standing" if base else "/standing",
            "operator": f"{base}/operator" if base else "/operator",
            "finished": f"{base}/finished" if base else "/finished",
        },
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
    }


def page_blocks() -> list[dict[str, Any]]:
    return [
        {
            "id": "gap",
            "heading": "The gap",
            "body": (
                "Meter is $0.10 hops and a small book. Aim is $50–200M because "
                "someone buys the HoldCo or a $50B desk exists. Bind volume "
                "does not walk that. Forced attach can print $5–40M before June "
                "if one close depends on redeem."
            ),
        },
        {
            "id": "mouth",
            "heading": "One mouth",
            "body": (
                "Insurability (no folio, no cover) or hosted redeem (you are the hop). "
                "Closing dependency is the same throat. Pick one seat. Do not spray."
            ),
        },
        {
            "id": "halt",
            "heading": "Halt",
            "body": HALT,
        },
    ]
