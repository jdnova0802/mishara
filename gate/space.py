"""Space Academy remaining — not the school, not C2.

White House EO 28 Aug 2026: Presidential Commission on the United States
Space Academy. NASA-led. Cadets, operators, entrepreneurs, civil servants,
warfighters. Service obligations. Not an academy yet — a commission.

We do not run it. We do not train warfighters. We do not sell the throat.
Nuclear C2 and battlefield release stay unmouthed.

The academy creates people who will radiate irreversible commands past
human watch (light-delay) under a time-bounded commission. West Point
never needed a remaining of that. Space does.

Two mouths:
  Delay Unwatched — remaining that must hold across light-time
  Commission Remaining — write-classes a commission may spend, then discharge

Not a sixth sibling. Not a /for/ plate. Not Being. $0 until Gate 1.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

try:
    from gate import vital as vital_mod
except ImportError:
    import vital as vital_mod

try:
    from gate import discharge as discharge_mod
except ImportError:
    import discharge as discharge_mod

SPEC = "gate-space-academy-remaining-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None
PAYEE = "Nisaba LLC"

IDENTITY = "we record the commission and the delay; we do not own the sky"
THESIS = (
    "A Space Academy will mint operators who write when Earth cannot watch. "
    "West Point commissioned officers at human speed. Light-delay makes the "
    "cadet unwatched by geometry. The EO also mixes entrepreneurs and "
    "warfighters in one school — the sheath class of the commission must "
    "be proveable. State issues rank. We record remaining. We do not radiate."
)

NEVER = (
    "run the academy",
    "train warfighters",
    "sell C2",
    "sell nuclear CLTU",
    "own launch licensing",
    "sell may",
    "Being as a SKU",
)

INVENTIONS: tuple[dict[str, Any], ...] = (
    {
        "id": "delay_unwatched",
        "code": "SA1",
        "name": "Delay Unwatched",
        "what": (
            "When round-trip light time exceeds a human watch, the vehicle's "
            "after is unwatched by geometry. Night Law is sleep. This is c."
        ),
        "chokepoint": "launch license / hull insurance cannot bind a solo without a delay hold",
        "who_pays": "insurer or launch licensor — not the cadet (issuer-pays trap)",
        "print": "Per-mission delay hold. Fat when cited. Not household attach.",
        "not": "C2. We hold remaining across the delay. We do not command the burn.",
    },
    {
        "id": "commission_remaining",
        "code": "SA2",
        "name": "Commission Remaining",
        "what": (
            "The EO requires service-obligation terms. A commission is a "
            "status function: this graduate may spend these write-classes "
            "until discharge. State issues the rank. We record the remaining."
        ),
        "chokepoint": "no commission folio, no solo — academy honor + insurer cite",
        "who_pays": "the service, the agency, or the insurer. Never the cadet.",
        "print": "Per graduate, then annual remaining while obligated. Discharge at end of term.",
        "not": "We do not commission. We do not wear the uniform.",
    },
    {
        "id": "sheath_class",
        "code": "SA3",
        "name": "Sheath class of the commission",
        "what": (
            "One academy, two priesthoods: entrepreneur and warfighter. "
            "A civil operator must not radiate a military write. The sheath "
            "class is proveable remaining."
        ),
        "chokepoint": "wrong sheath → radiation abort. Already the uplink mouth.",
        "who_pays": "the academy or the service — appropriation, then sticky",
        "print": "Per obligated graduate / year. Small N. High attach if the school cites it.",
        "not": "C2. Unmouthed write-classes stay unmouthed.",
    },
)


def delay_hold(vehicle: str, light_s: float = 0) -> dict[str, Any]:
    """Unwatched remaining across light-time. Not a command."""
    name = (vehicle or "").strip()[:160]
    rt = max(0.0, float(light_s or 0))
    unwatched = rt > 2.0
    base = vital_mod.hold("unwatched", name)
    base.update(
        {
            "spec": SPEC,
            "kind": "delay_unwatched",
            "vehicle": name or None,
            "round_trip_s": rt,
            "unwatched_by_geometry": unwatched,
            "c2": False,
            "command_sold": False,
            "may_sold": False,
            "payee": PAYEE,
            "until_gate1_usd": 0,
        }
    )
    return base


def commission(graduate: str, sheath: str = "civil", years: int = 5) -> dict[str, Any]:
    """Record write-class remaining of a commission. State issued the rank."""
    who = (graduate or "").strip()[:160]
    klass = (sheath or "civil").strip().lower()
    if klass not in ("civil", "service"):
        klass = "civil"
    yr = max(1, min(int(years or 5), 20))
    job = f"commission:{who or 'unnamed'}:{klass}"
    rail = discharge_mod.schedule(job, days=yr * 365)
    return {
        "spec": SPEC,
        "kind": "commission_remaining",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "graduate": who or None,
        "sheath_class": klass,
        "obligation_years": yr,
        "state_issues_rank": True,
        "we_record_remaining": True,
        "we_do_not_commission": True,
        "c2": False,
        "warfighter_trained": False,
        "discharge_rail": rail.get("ok"),
        "standing_until": rail.get("standing_until"),
        "may_sold": False,
        "being_sold": False,
        "payee": PAYEE,
        "until_gate1_usd": 0,
        "cleverer_layer": CLEVERER_LAYER,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Space Academy remaining",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "thesis": THESIS,
        "source": (
            "White House EO 2026-08-28 — Presidential Commission on the "
            "United States Space Academy. Commission, not an academy yet."
        ),
        "inventions": [dict(x) for x in INVENTIONS],
        "never": list(NEVER),
        "payee": PAYEE,
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "until_gate1_usd": 0,
        "checkout": False,
        "appropriation_class": True,
        "not_september_spray": True,
        "cash_door": f"{base}/bind-room",
        "page": f"{base}/space",
        "links": {
            "page": f"{base}/space",
            "uplink": f"{base}/uplink",
            "vital": f"{base}/vital",
            "discharge": f"{base}/discharge",
        },
        "gatekeep": (
            "Not the academy. Not C2. Record the commission and the delay. "
            "$0 until Gate 1."
        ),
    }
