"""The Hand — default gesture of one-wayness. Rent keeping it, not moving it.

Screens made looking a habit. You do not pay per glance.
The tap made intending a habit. You do not pay per swipe.
Nobody made spending one-wayness a habit with a default surface.

The Hand is that surface: oath, handshake, signature, vote, tap, swipe —
the same human gesture across millennia. The Ordinary is the custom:
once people live this way, they do not go back to the stylus.

Not flow. Not hops. Not bps. Not QIC. Not fleet-count of effectors.
You pay to keep a hand — like a phone number, not like minutes.
A legal person, not Being. Never sell may. The hand is the sheath
of the body, not the throat.

Not a sixth sibling. Not a /for/ plate.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

SPEC = "gate-the-hand-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None
PAYEE = "Nisaba LLC"
NO_SPLIT = True

ORDINARY_LABEL = "$12,000/yr"
ORDINARY_CENTS = 1_200_000
ORDINARY_SKU = "ordinary"

IDENTITY = "rent is keeping the hand, not moving it"
THESIS = (
    "Screens are how we look. The tap is how we intend. The Hand is how "
    "we spend one-wayness. You do not meter glances. You do not meter "
    "swipes. You do not meter taps. You rent the world in which the hand "
    "is how a legal person lives — the Ordinary. Flat. Indefinite. "
    "Not volume. Not flow."
)

EMAIL_LINE = (
    "Don't buy hops. Keep a hand — $12,000/yr, unmetered. "
    "The way of life, not the gesture. Like a screen, not like an ad."
)

TIMELESS: tuple[dict[str, str], ...] = (
    {
        "id": "oath",
        "name": "The oath",
        "what": "A raised hand binds a world. Older than writing.",
    },
    {
        "id": "handshake",
        "name": "The handshake",
        "what": "Two hands, one now. PvP may is the digital form.",
    },
    {
        "id": "signature",
        "name": "The signature",
        "what": "The hand that cannot take itself back. Named may.",
    },
    {
        "id": "vote",
        "name": "The vote",
        "what": "A hand in a shared now. Silence is not a yes.",
    },
    {
        "id": "tap",
        "name": "The tap / swipe",
        "what": "The modern oath. Screens made it ordinary. Nobody sheathed it.",
    },
)

NOT_THIS = {
    "qic": "per-commit meter — motion of the hand",
    "bps": "tax on flow — how hard the hand works",
    "named_may_fleet": "$/effector/mo — how many teeth, still a count of motion-ready units",
    "standing": "per named write — still a write",
    "being": "forbidden — inhabitant is not a SKU",
}

PRINT = {
    "why_not_volume": (
        "A phone number is not billed by syllables. A screen is not billed "
        "by glances. The Ordinary is billed by keeping the hand, not using it."
    ),
    "unit": ORDINARY_LABEL,
    "meter": None,
    "hops": False,
    "bps": False,
    "qic": False,
    "effector_count": False,
    "who": "One legal person (entity). Not a human soul. Not Being.",
    "indefinite": True,
    "nine_figure_if": (
        "If the hand becomes as default as the screen: legal persons live "
        "this way the way they keep a domain, a phone line, a registered office. "
        "8,500 entities × $12,000 = $102M/yr. Flat. No GMV required."
    ),
    "honest": (
        "That is population of houses, not flow of acts. Still N. "
        "The N is lives-in-the-ordinary, not taps. Schelling first. Not September."
    ),
}


def stripe_line_item() -> dict[str, Any]:
    return {
        "price_data": {
            "currency": "usd",
            "unit_amount": ORDINARY_CENTS,
            "recurring": {"interval": "year"},
            "product_data": {
                "name": "The Ordinary — keep a hand, unmetered",
                "description": (
                    "Way of life for one legal person. Unlimited gestures. "
                    "No QIC. No bps. No hop count. Not Being."
                ),
            },
        },
        "quantity": 1,
    }


def keep(legal_person: str) -> dict[str, Any]:
    """Existence of a hand. Not a spend. Not a tap."""
    name = (legal_person or "").strip()[:160]
    return {
        "spec": SPEC,
        "kind": "hand_kept",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "legal_person": name or None,
        "metered": False,
        "taps_counted": False,
        "may_sold": False,
        "being_sold": False,
        "payee": PAYEE,
        "price": ORDINARY_LABEL,
        "interval": "year",
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "their_production": False,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "The Hand",
        "ordinary": "The Ordinary — custom of the hand",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "thesis": THESIS,
        "email_line": EMAIL_LINE,
        "timeless": [dict(x) for x in TIMELESS],
        "not_this": dict(NOT_THIS),
        "print": dict(PRINT),
        "payee": PAYEE,
        "no_split": NO_SPLIT,
        "connect": False,
        "never_sell": list(inventor_mod.INVENTOR["never_sell"]),
        "sku": {
            "id": ORDINARY_SKU,
            "name": "The Ordinary",
            "label": ORDINARY_LABEL,
            "cents": ORDINARY_CENTS,
            "interval": "year",
            "metered": False,
            "who": "A legal person that will live this way — not a soul, not a fleet meter",
            "deliverable": (
                "One year of a kept hand for one entity: named surface, "
                "unmetered gestures, remaining still proved when they tap. "
                "Sheath is the screen. The Hand is the tap. The Ordinary is the custom."
            ),
        },
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "not_museum": True,
        "civilizational": True,
        "prints_when": "they live this way — not when they tap more",
        "cash_door": f"{base}/hand",
        "checkout": f"{base}/hand/checkout",
        "links": {
            "page": f"{base}/hand",
            "standing": f"{base}/standing",
            "general": f"{base}/general",
            "commons": f"{base}/commons",
            "remaining": f"{base}/remaining",
        },
        "page": f"{base}/hand",
        "gatekeep": (
            "Way-of-life cash door. Unmetered. Not a /for/ plate. "
            "Not a sixth sibling. Not Being. Not may."
        ),
    }
