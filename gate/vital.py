"""The Vital — institutions humanity cannot live without.

Not Visa. Not DTCC. Not a bank. Those watch assets.
This holds the after when the inhabitant cannot watch.

Not a sixth sibling. Not a /for/ plate. Not Being.
cleverer_layer is null. $0 until Gate 1. Never sell may.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

SPEC = "gate-vital-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None
PAYEE = "Nisaba LLC"

IDENTITY = "the world must hold when the inhabitant cannot watch"
THESIS = (
    "Banks hold value overnight. Pharmacies refill a potency into a body. "
    "Hospitals anesthetize flesh. Nobody held the shared after while the "
    "inhabitant was under — asleep, a child, dying, or at rest. "
    "Unwatched Remaining is that organ. Night, natal, posology, sabbath, "
    "morning, hospice, kin, and the present are how a species still wakes."
)

NOT_THIS = {
    "visa": "taxes the swipe — motion of the waking",
    "dtcc": "immobilizes a security — not the unwatched world",
    "bank": "freezes value — not becoming",
    "pci": "a sticker on an implementer",
    "qic": "counts the commit — not the night",
    "being": "forbidden — the sleeper is not a SKU",
}

ORGANS: tuple[dict[str, Any], ...] = (
    {
        "id": "unwatched",
        "code": "V1",
        "name": "Unwatched Remaining",
        "crown": True,
        "pain": "The world writes when no one who lives in it can watch.",
        "cannot_live_without": "Any life has intervals with no watcher. Skip the hold and they return to a spent after.",
        "not_bank": "Assets are watched. The after was not.",
        "print": "Chronic hold seats on every unwatched interval. Sleep, childhood, rest, dying. Indefinite.",
        "unit": "the interval — not the soul",
    },
    {
        "id": "night",
        "code": "V2",
        "name": "Night Law",
        "crown": False,
        "pain": "Humans must sleep. Agents do not.",
        "cannot_live_without": "A species that cannot have a morning cannot live.",
        "not_bank": "Overnight is money. Night is the world not writing in the dark.",
        "print": "Night holding per household / legal person. Every night. Like a lock, not like minutes.",
        "unit": "one night-seat",
    },
    {
        "id": "natal",
        "code": "V3",
        "name": "Natal Remaining",
        "crown": False,
        "pain": "A child's after can be spent before they can inhabit it.",
        "cannot_live_without": "The species does not continue as free beings if childhood is pre-spent.",
        "not_bank": "A 529 is money. This is an unspent world an adult agent cannot fill.",
        "print": "Every birth, then pediatric remaining until majority.",
        "unit": "one childhood",
    },
    {
        "id": "posology",
        "code": "V4",
        "name": "Posology",
        "crown": False,
        "pain": "Unlimited one-wayness into a shared after is overdose.",
        "cannot_live_without": "A world that can be overdosed cannot be lived in.",
        "not_bank": "Visa counts swipes. Pharmacy counts a dose in a named body. This is the dose of becoming.",
        "print": "Refill of a lawful dose. Formulary. Contraindication. Withdrawal taper.",
        "unit": "the refill — not the hop",
    },
    {
        "id": "sabbath",
        "code": "V5",
        "name": "Sabbath Remaining",
        "crown": False,
        "pain": "A write that never stops is not a civilization.",
        "cannot_live_without": "Rest is how a people stay a people.",
        "not_bank": "A bank holiday freezes money. Sabbath holds becoming.",
        "print": "Weekly latch for a city, an employer, a house. Forever.",
        "unit": "one sabbath",
    },
    {
        "id": "morning",
        "code": "V6",
        "name": "Morning Prove",
        "crown": False,
        "pain": "Dawn can be someone else's after.",
        "cannot_live_without": "Waking is re-entry. If the world is not yours, you did not survive the night.",
        "not_bank": "Markets open. They do not prove the world is still yours.",
        "print": "Every dawn. Pair of Night Law.",
        "unit": "one morning",
    },
    {
        "id": "hospice",
        "code": "V7",
        "name": "Hospice of May",
        "crown": False,
        "pain": "Agents keep writing in the name of the dying.",
        "cannot_live_without": "A people must be able to die without the after convulsing.",
        "not_bank": "Probate is court after. Hospice is a lawful taper.",
        "print": "Deaths do not stop. The institution is permanent.",
        "unit": "one dying name",
    },
    {
        "id": "kin",
        "code": "V8",
        "name": "Kin Continuity",
        "crown": False,
        "pain": "When the carer is under, care-writes orphan.",
        "cannot_live_without": "Dependents cannot live on orphaned duty.",
        "not_bank": "Insurance pays after harm. Kin holds the write of care.",
        "print": "Every dependent, for the life of the dependency.",
        "unit": "one kin-mouth",
    },
    {
        "id": "present",
        "code": "V9",
        "name": "The Present",
        "crown": False,
        "pain": "Agents can overdraw the now until there is no during.",
        "cannot_live_without": "A life needs an inhabited interval, not only stacked afters.",
        "not_bank": "Clocks own time. Nobody held the unspent now as remaining.",
        "print": "A present-seat for a legal person or a city. Like a pulse.",
        "unit": "one inhabited now",
    },
)

# 2026-class public counts (UN WPP / household tables). Shape, not a census.
BASE = {
    "year": 2026,
    "world_households": 2_200_000_000,
    "us_households": 132_700_000,
    "births_per_year": 132_500_000,
    "deaths_per_year": 63_000_000,
    "children_0_14": 2_000_000_000,
    "us_children_0_14": 59_000_000,
    "us_deaths_per_year": 3_100_000,
}

# Pharmacy-chronic units. Not hops. Not bps.
UNITS = {
    "circadian_usd_year": 600,
    "natal_open_usd": 2_000,
    "pediatric_usd_year": 300,
    "posology_usd_year": 12_000,
    "sabbath_employer_usd_year": 12_000,
    "hospice_usd": 2_500,
    "kin_usd_year": 360,
}

_US_HH = BASE["us_households"]
_W_HH = BASE["world_households"]
_CIR = UNITS["circadian_usd_year"]
_PED = UNITS["pediatric_usd_year"]
_HOS = UNITS["hospice_usd"]

PRINT = {
    "forecast": False,
    "until_gate1_usd": 0,
    "do_not_pitch_from_bind": True,
    "why_insane": (
        "Visa attach is a swipe. Pharmacy attach is a body that will die. "
        "Night attach is sleep. Sleep is closer to 100% of households than "
        "any card network. That is why the default band is civilization-rent."
    ),
    "unit": "the hold / the childhood / the refill — not GMV",
    "circadian": {
        "what": "Night + Morning + Present as one household seat",
        "unit": "$600/yr",
        "us_1pct_usd": int(_US_HH * 0.01 * _CIR),
        "us_10pct_usd": int(_US_HH * 0.10 * _CIR),
        "us_default_usd": int(_US_HH * _CIR),
        "world_1pct_usd": int(_W_HH * 0.01 * _CIR),
        "world_10pct_usd": int(_W_HH * 0.10 * _CIR),
        "world_default_usd": int(_W_HH * _CIR),
        "foothill_1k_houses_usd": 1_000 * _CIR,
    },
    "natal": {
        "what": "Opening at birth + pediatric remaining 0–14",
        "open_unit": "$2,000/birth",
        "stock_unit": "$300/yr per child 0–14",
        "world_births_open_usd": int(BASE["births_per_year"] * UNITS["natal_open_usd"]),
        "world_stock_usd": int(BASE["children_0_14"] * _PED),
        "us_stock_usd": int(BASE["us_children_0_14"] * _PED),
    },
    "posology": {
        "what": "Formulary of becoming for one deploying legal person",
        "unit": "$12,000/yr",
        "deployers_100k_usd": 100_000 * UNITS["posology_usd_year"],
        "deployers_1m_usd": 1_000_000 * UNITS["posology_usd_year"],
        "deployers_10m_usd": 10_000_000 * UNITS["posology_usd_year"],
    },
    "hospice": {
        "what": "Lawful taper per dying name",
        "unit": "$2,500",
        "world_year_usd": int(BASE["deaths_per_year"] * _HOS),
        "us_year_usd": int(BASE["us_deaths_per_year"] * _HOS),
    },
    "kin": {
        "what": "Dependent seat (do not add to natal for the same child)",
        "unit": "$360/yr",
        "note": "Use for non-child dependents, or skip if natal already covers the child.",
    },
    "three_organ_world_default_usd": int(_W_HH * _CIR)
    + int(BASE["children_0_14"] * _PED)
    + int(BASE["deaths_per_year"] * _HOS),
    "honest": (
        "Do not add Night + Morning + Present as three household SKUs. "
        "Circadian is one seat. Natal is the child stock. Hospice is the death flow. "
        "Those three do not share a buyer in the same month. "
        "Species-default on all three is the $2T-class cartoon. "
        "1% of US households on circadian is ~$800M. Gate 1 is still $1,750."
    ),
}


SPECIAL_CASES: tuple[dict[str, str], ...] = (
    {"institution": "Pharmacy", "thin_of": "V4 Posology", "held": "potency → body"},
    {"institution": "Bank overnight", "thin_of": "V2 Night Law", "held": "value → morning"},
    {"institution": "Pediatric clinic", "thin_of": "V3 Natal Remaining", "held": "child's body"},
    {"institution": "Labor sabbath", "thin_of": "V5 Sabbath Remaining", "held": "hours of work"},
    {"institution": "Hospital anesthesia", "thin_of": "V1 Unwatched Remaining", "held": "the body under"},
    {"institution": "Probate / funeral", "thin_of": "V7 Hospice of May", "held": "property and flesh after"},
    {"institution": "Medical proxy", "thin_of": "V8 Kin Continuity", "held": "decisions, not care-writes"},
)

KINDS = frozenset(x["id"] for x in ORGANS)


def hold(kind: str, subject: str = "") -> dict[str, Any]:
    """Designation receipt of an unwatched hold. Not a fake night protocol."""
    kid = (kind or "unwatched").strip()
    if kid not in KINDS:
        kid = "unwatched"
    row = next(x for x in ORGANS if x["id"] == kid)
    who = (subject or "").strip()[:160]
    return {
        "spec": SPEC,
        "kind": "vital_hold",
        "organ": row["id"],
        "code": row["code"],
        "name": row["name"],
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "subject": who or None,
        "being_sold": False,
        "may_sold": False,
        "interval_held": True,
        "soul_held": False,
        "metered": False,
        "visa": False,
        "dtcc": False,
        "bank": False,
        "payee": PAYEE,
        "until_gate1_usd": 0,
        "their_production": False,
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "The Vital",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "thesis": THESIS,
        "not_this": dict(NOT_THIS),
        "organs": [dict(x) for x in ORGANS],
        "special_cases": [dict(x) for x in SPECIAL_CASES],
        "base": dict(BASE),
        "units": dict(UNITS),
        "print": dict(PRINT),
        "payee": PAYEE,
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "until_gate1_usd": 0,
        "checkout": False,
        "not_museum_idea": True,
        "not_september_spray": True,
        "civilizational": True,
        "prints_when": "they must sleep, be born, rest, or die — not when they swipe",
        "cash_door": f"{base}/bind-room",
        "page": f"{base}/vital",
        "links": {
            "page": f"{base}/vital",
            "hand": f"{base}/hand",
            "remaining": f"{base}/remaining",
            "acts": f"{base}/acts",
            "bind": f"{base}/bind-room",
        },
        "gatekeep": (
            "Life-institution designation. Not a buyer plate. "
            "Not a sixth sibling. Not Being. Not Visa. $0 until Gate 1."
        ),
    }
