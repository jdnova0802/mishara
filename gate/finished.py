"""Finished Remaining — they buy the folio, not the padlock.

Padlocks, meters, rails, books, mandates, ontology: those print after
someone implements you. This prints when they pay and you operate
the mouth for one write.

Not a sixth sibling. Not a /for/ plate. Not Being-as-SKU.
Checkout is live. $8,500 operated folio · $4,500 broker three-pack.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

try:
    from gate import remaining as remaining_mod
except ImportError:
    import remaining as remaining_mod

try:
    from gate import first as first_mod
except ImportError:
    import first as first_mod

try:
    from gate import bind_room as bind_room_mod
except ImportError:
    import bind_room as bind_room_mod

SPEC = "gate-finished-remaining-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None

FINISHED_LABEL = "$8,500"
FINISHED_CENTS = 850_000
BROKER_LABEL = "$4,500"
BROKER_CENTS = 450_000

INVENTION = (
    "They do not implement Gate. You operate may · redeem-or-silence · remaining "
    "· apostille · inhabitant copy for one named write, and they attach the pack "
    "to E&O / CGL after CG 40 47. The product is the finished remaining, not a rail."
)

EMAIL_LINE = (
    "Don't buy another padlock. Buy the finished remaining for one write — "
    "we operate the mouth, you attach the folio the underwriter can open. $8,500. "
    "Or a broker three-pack of Bind Rooms for $4,500."
)

SKUS: dict[str, dict[str, Any]] = {
    "finished_remaining": {
        "id": "finished_remaining",
        "name": "Finished Remaining",
        "label": FINISHED_LABEL,
        "cents": FINISHED_CENTS,
        "stripe_name": "Finished Remaining — operated folio for one write",
        "stripe_desc": "We operate may, remaining, apostille, inhabitant copy. You attach the pack.",
        "who": "GC / CUO-adjacent / founder facing E&O this cycle",
        "deliverable": (
            "Operated remaining pack for one job_id: folio + apostille + vital "
            "+ officer pack. 48hr after pay + job_id. Stranger-openable."
        ),
        "why_now": (
            "They already have a renewal date. They will not implement a rail "
            "before the binder. They will pay for a finished artifact."
        ),
        "surpasses": (
            "Bind Room is a template they fill. This is the remaining already "
            "run. Ticket is 5× Bind. First time the SKU is the stock, not the lock."
        ),
    },
    "broker_three_pack": {
        "id": "broker_three_pack",
        "name": "Broker three-pack",
        "label": BROKER_LABEL,
        "cents": BROKER_CENTS,
        "stripe_name": "Broker three-pack — three Bind Rooms",
        "stripe_desc": "Three Bind Room officer packs for three AI names on one book.",
        "who": "Specialty broker placing agent E&O",
        "deliverable": "Three Bind Room officer packs. You never cold the insured.",
        "why_now": "Broker already has the relationship. One checkout, three names.",
        "surpasses": "Volume printer on the $1,750 SKU without a new plate.",
    },
}


def stripe_line_item(sku: str) -> dict[str, Any]:
    row = SKUS[sku]
    return {
        "price_data": {
            "currency": "usd",
            "unit_amount": int(row["cents"]),
            "product_data": {
                "name": row["stripe_name"],
                "description": row["stripe_desc"],
            },
        },
        "quantity": 1,
    }


def pack(job_id: str, public_url: str, contact_email: str = "") -> dict[str, Any]:
    """The thing they attach. Not a padlock. The remaining, already run."""
    jid = (job_id or "").strip()
    folio = remaining_mod.folio(jid)
    return {
        "spec": SPEC,
        "kind": "finished_remaining_pack",
        "inventor": inventor_mod.stamp(),
        "job_id": jid or None,
        "price": FINISHED_LABEL,
        "operated_by": "Nisaba LLC",
        "they_do_not_implement_gate": True,
        "identity": remaining_mod.IDENTITY,
        "folio": folio,
        "apostille": first_mod.apostille(jid),
        "vital": first_mod.death_certificate(jid),
        "officer_pack": bind_room_mod.officer_pack(public_url, contact_email),
        "the_act_is_not_the_object": True,
        "not": [
            "a padlock they implement",
            "a meter they integrate",
            "a rail they weld first",
            "a mandate they wait for",
            "an ontology they read",
            "a sixth sibling",
        ],
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "their_production": False,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Finished Remaining",
        "inventor": inventor_mod.stamp(),
        "thesis": INVENTION,
        "email_line": EMAIL_LINE,
        "skus": {k: {kk: vv for kk, vv in v.items() if kk != "stripe_desc"} for k, v in SKUS.items()},
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "not_museum": True,
        "prints_when": "they pay — we operate — they attach",
        "cash_door": f"{base}/finished",
        "checkout": f"{base}/finished/checkout",
        "broker_checkout": f"{base}/finished/broker-checkout",
        "links": {
            "page": f"{base}/finished",
            "bind_room": f"{base}/bind-room",
            "refusal": f"{base}/refusal",
            "operator": f"{base}/operator",
            "remaining": f"{base}/remaining",
            "standing": f"{base}/standing",
            "cash_now": "CASH_NOW.md still names Bind $1,750 as highest-probability. One-shot is /finished. Recurring lease is /standing.",
        },
        "page": f"{base}/finished",
        "gatekeep": "Cash SKU. Not a buyer chrome plate for ontology.",
    }
