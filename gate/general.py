"""The General — money is a special case of remaining.

Satoshi inverted still plays Satoshi's game: named inventor, rent the
padlock, beat Bitcoin at money. The General contains him. Coins, value,
emissions, indemnity, licensed spend — remaining classes. Bitcoin
conserved coins and gave the protocol away. Nobody conserved one-wayness.

Correspondent remaining was a two-line weld. This seats it.
Institutions park remaining here (nostro). Two books, one remaining.
Neither forges alone. Not a maycoin. 100% Nisaba LLC.

Nine figures the way SWIFT/DTCC print: tens-to-hundreds of seats, not
millions of consumers. $1,000,000/yr × 100 correspondents = $100M.
2 bps on $500B immobilized remaining = $100M. Not this month. Not $0
cosplay either — the books now exist.
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

SPEC = "gate-the-general-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None
PAYEE = "Nisaba LLC"
NO_SPLIT = True

SEAT_LABEL = "$1,000,000/yr"
SEAT_CENTS = 100_000_000
SEAT_SKU = "correspondent_seat"

IDENTITY = "money is a special case of remaining"
THESIS = (
    "Satoshi inverted still plays Satoshi's game. The General contains him. "
    "Bitcoin conserved coins. Double-entry conserved value. Carbon conserved "
    "emissions. Nobody conserved one-wayness. Remaining is the general. "
    "Every prior invention on this tree is a class."
)

EMAIL_LINE = (
    "Money is a special case of remaining. Correspondent remaining is the "
    "DTCC seat — $1,000,000/yr, 100% Nisaba. Two books, one remaining. "
    "Neither forges alone. Not a maycoin. A hundred seats is nine figures."
)

SPECIAL_CASES: tuple[dict[str, Any], ...] = (
    {
        "id": "bitcoin",
        "name": "Bitcoin / UTXO",
        "remaining_class": "coin",
        "what": "Digital signatures + append-only time + 21M cap.",
        "satoshi": "Conserved coins. Gave the protocol away. Hid. Could not cash.",
        "contained": "A journal of one remaining class. Not the general.",
    },
    {
        "id": "double_entry",
        "name": "Pacioli double-entry",
        "remaining_class": "value",
        "what": "Two sides or the books fail.",
        "satoshi": "Money as the only stock worth a trial balance.",
        "contained": "The method. The object was never only value.",
    },
    {
        "id": "carbon",
        "name": "Carbon remaining-budget",
        "remaining_class": "emission",
        "what": "Atmosphere as remaining after fire.",
        "satoshi": "No stock of machine one-wayness.",
        "contained": "One substrate of spent one-wayness.",
    },
    {
        "id": "indemnity",
        "name": "Insurance limit / E&O",
        "remaining_class": "indemnity",
        "what": "Remaining cover after a loss.",
        "satoshi": "Soft-yes on everything that is not money.",
        "contained": "A remaining class underwriters already speak.",
    },
    {
        "id": "conformant_qic",
        "name": "Gate Conformant™ + QIC",
        "remaining_class": "licensed spend",
        "what": "Padlock standard + meter on the commit.",
        "satoshi": "The inverse — rent the lock, stay named.",
        "contained": "Grammar and flow. Consolation SKU. Not the general.",
    },
    {
        "id": "standing_remaining",
        "name": "Standing Remaining",
        "remaining_class": "proved remaining",
        "what": "Operated folio kept true, monthly.",
        "satoshi": "Retail lease. Not correspondent books.",
        "contained": "How one write stays proved. Not how institutions clear stock.",
    },
)

PRINT = {
    "easy_nine_figure": {
        "engine": "correspondent remaining seats",
        "unit": SEAT_LABEL,
        "n_for_100m": 100,
        "why_easy": (
            "SWIFT / DTCC / Euroclear shape: tens to low hundreds of "
            "institutions, not millions of consumers. Seats compound."
        ),
        "this_year": False,
        "until_gate1_usd": 0,
        "payee": PAYEE,
        "no_split": NO_SPLIT,
    },
    "stock_nine_figure": {
        "engine": "immobilization 2 bps on remaining notional",
        "hundred_million": "2 bps on $500B immobilized remaining",
        "billion": "2 bps on $5T",
        "why_fatter": "Custody AUM fees dwarf seat rent once books exist.",
        "books_now": True,
        "meter_later": True,
    },
    "already_named_never_fleshed": (
        "correspondent_remaining",
        "correspondent_may",
        "remaining_custody",
        "act_clearinghouse",
        "trial_balance_of_may",
    ),
    "honest": (
        "Nine figures is structural ease after Gate 1 and a first correspondent, "
        "not a September wire. Without Gate 1 the shape is $0."
    ),
}


def stripe_line_item() -> dict[str, Any]:
    return {
        "price_data": {
            "currency": "usd",
            "unit_amount": SEAT_CENTS,
            "recurring": {"interval": "year"},
            "product_data": {
                "name": "Correspondent Remaining — institutional seat",
                "description": (
                    "Nostro of remaining at Nisaba. Two books, one remaining. "
                    "Neither forges alone. Not a maycoin."
                ),
            },
        },
        "quantity": 1,
    }


def correspondent_books(left_job: str, right_job: str) -> dict[str, Any]:
    """Two depositories, one remaining. Neither forges alone."""
    left = remaining_mod.folio((left_job or "").strip())
    right = remaining_mod.folio((right_job or "").strip())
    apostille_left = first_mod.apostille((left_job or "").strip())
    apostille_right = first_mod.apostille((right_job or "").strip())
    both_hold = bool(left.get("identity_holds")) and bool(right.get("identity_holds"))
    return {
        "spec": SPEC,
        "kind": "correspondent_remaining",
        "inventor": inventor_mod.stamp(),
        "identity": remaining_mod.IDENTITY,
        "the_general": IDENTITY,
        "payee": PAYEE,
        "no_split": NO_SPLIT,
        "not_a_maycoin": True,
        "neither_forges_alone": True,
        "both_identity_hold": both_hold,
        "left": {"job_id": (left_job or "").strip() or None, "folio": left, "apostille": apostille_left},
        "right": {"job_id": (right_job or "").strip() or None, "folio": right, "apostille": apostille_right},
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "their_production": False,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def containment() -> dict[str, Any]:
    return {
        "spec": SPEC,
        "identity": IDENTITY,
        "thesis": THESIS,
        "satoshi_inverse_is_not_enough": True,
        "why": (
            "The inverse stays named and rents the padlock. It still treats "
            "Bitcoin as the rival. The General treats Bitcoin as a class."
        ),
        "special_cases": [dict(x) for x in SPECIAL_CASES],
        "never_sell": list(inventor_mod.INVENTOR["never_sell"]),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "The General",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "thesis": THESIS,
        "email_line": EMAIL_LINE,
        "containment": containment(),
        "print": dict(PRINT),
        "payee": PAYEE,
        "no_split": NO_SPLIT,
        "connect": False,
        "distribution": "none — 100% Nisaba LLC",
        "not_a_maycoin": True,
        "sku": {
            "id": SEAT_SKU,
            "name": "Correspondent Remaining seat",
            "label": SEAT_LABEL,
            "cents": SEAT_CENTS,
            "interval": "year",
            "who": "Bank / carrier / cloud / payout desk / specialty book that cannot hold remaining alone",
            "deliverable": (
                "Nostro of remaining at Nisaba. Correspondent books against "
                "one other named mouth. Stranger-openable folios. Annual seat."
            ),
            "n_for_nine_figures": 100,
        },
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "not_museum": True,
        "civilizational": True,
        "prints_when": "first correspondent sits — then seats compound",
        "cash_door": f"{base}/general",
        "checkout": f"{base}/general/checkout",
        "links": {
            "page": f"{base}/general",
            "standing": f"{base}/standing",
            "finished": f"{base}/finished",
            "remaining": f"{base}/remaining",
            "first": f"{base}/first",
            "operator": f"{base}/operator",
        },
        "page": f"{base}/general",
        "gatekeep": (
            "Civilizational cash door. Correspondent remaining. "
            "Not a /for/ plate. Not a sixth sibling. Not a maycoin."
        ),
    }
