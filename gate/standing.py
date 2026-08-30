"""Standing Remaining — remaining lease. Recurring. 100% to the mouth.

A souvenir folio ages. The remaining has to stay true at the next
underwriter ask, the next board, the next renewal. Live stock is a lease.

Not a weld they run. Not Conformant rent they implement. Not bps they
clear through a desk. Not a split. Not Connect. Payee is Nisaba LLC.

Not a sixth sibling. Not a /for/ plate. Not Being-as-SKU.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

try:
    from gate import finished as finished_mod
except ImportError:
    import finished as finished_mod

try:
    from gate import remaining as remaining_mod
except ImportError:
    import remaining as remaining_mod

SPEC = "gate-standing-remaining-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None
PAYEE = "Nisaba LLC"
NO_SPLIT = True

WRITE_LABEL = "$4,500/mo"
WRITE_CENTS = 450_000
BOOK_LABEL = "$9,000/mo"
BOOK_CENTS = 900_000
DESK_LABEL = "$25,000/mo"
DESK_CENTS = 2_500_000

CATEGORY = "remaining_lease"
CATEGORY_NAME = "Remaining lease"

INVENTION = (
    "The remaining is a live stock. A one-shot folio is a souvenir. "
    "Live stock is a lease: you operate the mouth every month so the "
    "folio is still true. Cancel and it goes stale. 100% to Nisaba LLC. "
    "They do not implement Gate. No distribution to anyone else."
)

EMAIL_LINE = (
    "A folio ages. Standing Remaining keeps one write true — $4,500/mo. "
    "A broker book stays live — $9,000/mo. A company desk — $25,000/mo. "
    "We operate. You attach. Cancel and the next underwriter ask fails."
)

SKUS: dict[str, dict[str, Any]] = {
    "standing_write": {
        "id": "standing_write",
        "name": "Standing write",
        "label": WRITE_LABEL,
        "cents": WRITE_CENTS,
        "interval": "month",
        "stripe_name": "Standing Remaining — one write, monthly",
        "stripe_desc": "We operate and refresh the remaining folio for one named write every month.",
        "who": "GC / founder who already felt a folio go stale, or who will not buy a souvenir",
        "deliverable": (
            "Monthly operated remaining pack for one job_id. Refresh inside "
            "the billing period. Stranger-openable. Stops when they cancel."
        ),
        "why_now": (
            "E&O is not a one-time PDF. The underwriter asks again. "
            "A snapshot cannot answer a later now."
        ),
        "surpasses": (
            "Operator floor is $5k/mo after they weld a licensed desk. "
            "This is $4.5k/mo and they never implement. Recurring without a rail."
        ),
        "stacks": "N writes × $4,500/mo. Six writes = $27,000/mo to the mouth.",
    },
    "standing_book": {
        "id": "standing_book",
        "name": "Standing book",
        "label": BOOK_LABEL,
        "cents": BOOK_CENTS,
        "interval": "month",
        "stripe_name": "Standing Remaining — broker book, monthly",
        "stripe_desc": "Three named remaining folios kept live for one specialty book.",
        "who": "Specialty broker who sold a three-pack and now has a renewal calendar",
        "deliverable": "Three live remaining packs, refreshed monthly. You never cold the insured.",
        "why_now": "The book renews. Souvenir packs die. The broker needs the names still true.",
        "surpasses": "Broker three-pack is one invoice. This is the book as rent.",
        "stacks": "One book = $9,000/mo. Four books = $36,000/mo.",
    },
    "standing_desk": {
        "id": "standing_desk",
        "name": "Standing desk",
        "label": DESK_LABEL,
        "cents": DESK_CENTS,
        "interval": "month",
        "stripe_name": "Standing Remaining — company desk, monthly",
        "stripe_desc": "Operated remaining desk for one company. Up to eight named writes.",
        "who": "GC / CUO of a deployer with several irreversible writes and an E&O date",
        "deliverable": (
            "Up to eight named writes, operated and refreshed in the month. "
            "They send job_ids. You return packs. No weld in their house."
        ),
        "why_now": (
            "A company with more than one write will not buy eight souvenirs. "
            "They rent a desk. $25k/mo = $300k/yr, 100% Nisaba."
        ),
        "surpasses": (
            "Operator weld is $25k once + $5k/mo and they implement. "
            "This is $25k/mo and you operate. Same first check, then it prints every month."
        ),
        "stacks": "Four desks = $100,000/mo. No split.",
    },
}


def stripe_line_item(sku: str) -> dict[str, Any]:
    row = SKUS[sku]
    return {
        "price_data": {
            "currency": "usd",
            "unit_amount": int(row["cents"]),
            "recurring": {"interval": "month"},
            "product_data": {
                "name": row["stripe_name"],
                "description": row["stripe_desc"],
            },
        },
        "quantity": 1,
    }


def pack(job_id: str, public_url: str, contact_email: str = "", sku: str = "standing_write") -> dict[str, Any]:
    """This month's remaining, already run. Stale next month unless they stay."""
    row = SKUS.get(sku) or SKUS["standing_write"]
    base = finished_mod.pack(job_id, public_url, contact_email)
    base.update(
        {
            "spec": SPEC,
            "kind": "standing_remaining_pack",
            "sku": row["id"],
            "price": row["label"],
            "interval": "month",
            "payee": PAYEE,
            "no_split": NO_SPLIT,
            "connect": False,
            "category": CATEGORY,
            "standing": True,
            "souvenir": False,
            "stale_if_canceled": True,
            "they_do_not_implement_gate": True,
            "identity": remaining_mod.IDENTITY,
            "evaluated_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return base


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Standing Remaining",
        "category": CATEGORY,
        "category_name": CATEGORY_NAME,
        "inventor": inventor_mod.stamp(),
        "thesis": INVENTION,
        "email_line": EMAIL_LINE,
        "payee": PAYEE,
        "no_split": NO_SPLIT,
        "connect": False,
        "distribution": "none — 100% Nisaba LLC",
        "skus": {k: {kk: vv for kk, vv in v.items() if kk != "stripe_desc"} for k, v in SKUS.items()},
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "not_museum": True,
        "prints_when": "they stay — we operate every month — they attach",
        "existing_recurring_that_is_not_this": {
            "operator_floor": "$5,000/mo — they must weld a licensed desk first",
            "register_bps": "10 bps of cleared — they must clear through you",
            "gate_pro": "$99/mo seat — not the print",
            "conformant_qic": "$0 until Gate 1, then they implement the badge",
        },
        "cash_door": f"{base}/standing",
        "checkout": f"{base}/standing/checkout",
        "links": {
            "page": f"{base}/standing",
            "finished": f"{base}/finished",
            "bind_room": f"{base}/bind-room",
            "operator": f"{base}/operator",
            "remaining": f"{base}/remaining",
        },
        "page": f"{base}/standing",
        "gatekeep": "Recurring cash door. Not a buyer chrome plate. Not a split.",
    }
