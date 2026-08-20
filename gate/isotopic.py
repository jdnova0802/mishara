"""Isotopic CHARGE — CHARGE cannot be synthesized from demo feedstock.

Alien hardware uses isotopes you cannot cook in a garage. Gate's CHARGE
is isotopic: weld-paid, named witness, epoch-bound. Demo hops, AI badges,
and admin toggles are abundant isotopes — they do not fuse to LIVE.
Copycats dilute CHARGE into a boolean.

Gatekeep only to ourselves: isotope / enrichment metaphor → unforgeable CHARGE.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-isotopic-charge-v1"
INVENTOR = "Nisaba LLC / Gate"

FEEDSTOCK = (
    "demo_hop",
    "uw_approve",
    "admin_toggle",
    "ai_badge",
    "dashboard_green",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def enrich(
    *,
    charge_id: str | None = None,
    weld_paid: bool | None = None,
    feedstock: str | None = None,
) -> dict[str, Any]:
    cid = bool((charge_id or "").strip())
    paid = bool(weld_paid)
    feed = (feedstock or "").strip().lower()
    if feed in FEEDSTOCK and not cid:
        posture = "abundant_isotope"
        claim = "feedstock_cannot_enrich_to_live"
    elif cid and paid:
        posture = "enriched_charge"
        claim = "isotopic_witness_under_weld"
    elif cid and not paid:
        posture = "witness_without_weld_mass"
        claim = "charge_id_without_skin_is_not_fully_enriched"
    else:
        posture = "no_enrichment"
        claim = "dead_remains_natural_abundance"
    return {
        "spec": SPEC,
        "name": "Isotopic CHARGE",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Isotopic enrichment — rare species cannot be faked from common feedstock",
            "Gate costliness + costly signal — CHARGE is not a boolean",
        ],
        "rejected_feedstock": list(FEEDSTOCK),
        "charge_present": cid,
        "weld_paid": paid,
        "feedstock": feed or None,
        "posture": posture,
        "claim": claim,
        "thesis": "You cannot cook LIVE from demo feedstock. CHARGE is an isotope.",
        "gatekeep": "Proprietary isotopic CHARGE doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Isotopic CHARGE",
        "inventor": INVENTOR,
        "example_enriched": enrich(charge_id="chg_1", weld_paid=True),
        "example_feedstock": enrich(feedstock="demo_hop"),
        "live": f"{base}/.well-known/isotopic-charge.json",
        "costly_signal": f"{base}/.well-known/costly-signal.json",
        "their_production": False,
    }
