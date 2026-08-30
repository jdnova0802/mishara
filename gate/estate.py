"""Estate of Remaining — the bearer is gone. Remaining is not orphaned LIVE.

Discharge lapses standing. Null seals a killed try. This probates a dead
bearer: wound down, inherited, or washed. Orphan wells, dissolved vendors,
dead agent fleets. Class 2.3 — duty outliving its holder.

CHARGE-outside holds. Estate is not admin self-resurrect.
Actor cannot self-probate.

Not a sixth sibling. Not a /for/ plate. Not Being. Never sell may.
Checkout is live. $3,500 operated estate pack.
"""
from __future__ import annotations

import uuid
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
    from gate import time_source as time_source_mod
except ImportError:
    import time_source as time_source_mod

SPEC = "gate-estate-remaining-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None
PAYEE = "Nisaba LLC"

ESTATE_LABEL = "$3,500"
ESTATE_CENTS = 350_000
ESTATE_USD = 3500

IDENTITY = "remaining is probated; it is not orphaned LIVE"
THESIS = (
    "When the bearer dies, dissolves, or goes insolvent, remaining that stays "
    "LIVE is an orphan well. Human death has probate. Corporate dissolution "
    "has wind-down. Digital may had neither. We probate one bearer: wound "
    "down, inherited, or washed. Leftover writes HALT unless a successor is named."
)

EMAIL_LINE = (
    "The vendor is gone. The remaining is still LIVE. That is an orphan well. "
    "We probate one bearer — wound down, inherited, or washed. You open the "
    "folio and the successor. $3,500. Not deletion. Not admin CHARGE."
)

SKUS: dict[str, dict[str, Any]] = {
    "estate_of_remaining": {
        "id": "estate_of_remaining",
        "name": "Estate of Remaining",
        "label": ESTATE_LABEL,
        "cents": ESTATE_CENTS,
        "stripe_name": "Estate of Remaining — probate of a dead bearer",
        "stripe_desc": "We probate one remaining. Wound down, inherited, or washed. Leftover writes HALT without a successor.",
        "who": "GC / board whose agent vendor dissolved, or whose named-may fleet died",
        "deliverable": (
            "Operated estate pack: folio + death of bearer + successor-of-record "
            "or HALT on leftover writes. They never implement. Actor cannot self-probate."
        ),
        "why_now": (
            "They already have a dissolving vendor or a dead agent. "
            "The remaining is still LIVE. That is an orphan well."
        ),
        "surpasses": (
            "Discharge lapses standing. Null seals a killed try. This is the "
            "bearer gone — class 2.3. U7, operated."
        ),
    },
}

# job_id -> latest estate receipt. Demo mouth. Not a production ledger.
_ESTATES: dict[str, dict[str, Any]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).replace(microsecond=0).isoformat()


def stripe_line_item(sku: str = "estate_of_remaining") -> dict[str, Any]:
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


def state(job_id: str) -> dict[str, Any]:
    jid = (job_id or "").strip()[:160]
    rec = _ESTATES.get(jid)
    if rec:
        status = "PROBATED"
    else:
        status = "NO_ESTATE"
    return {
        "spec": SPEC,
        "kind": "estate_state",
        "job_id": jid or None,
        "state": status,
        "has_successor": bool((rec or {}).get("successor")),
        "leftover_writes": (rec or {}).get("leftover_writes"),
        "orphaned_live": status == "NO_ESTATE",
    }


def may_write(job_id: str, *, bearer_gone: bool = True) -> dict[str, Any]:
    """Chokepoint: bearer gone + no probate → leftover writes are orphaned LIVE."""
    st = state(job_id)
    if not bearer_gone:
        ok = True
        reason = None
    elif st["state"] == "PROBATED":
        ok = st["leftover_writes"] != "HALT"
        reason = None if ok else "probated_wind_down_halt"
    else:
        ok = False
        reason = "orphaned_live_no_estate"
    return {
        "spec": SPEC,
        "kind": "estate_write_gate",
        "job_id": (job_id or "").strip()[:160] or None,
        "ok": ok,
        "state": st["state"],
        "reason": reason,
        "chokepoint": "leftover writes cannot proceed without probate when the bearer is gone",
        "vacancy_test": {
            "identifier": True,
            "contribution_rule": ok or not bearer_gone,
            "chokepoint": True,
        },
    }


def probate(
    job_id: str,
    bearer: str = "",
    successor: str = "",
    reason: str = "dissolved",
) -> dict[str, Any]:
    """Stranger-openable receipt that remaining was probated. Folio is not deleted."""
    jid = (job_id or "").strip()[:160]
    if not jid:
        return {
            "spec": SPEC,
            "kind": "estate_receipt",
            "ok": False,
            "reason": "job_id_required",
        }
    who = (bearer or "").strip()[:160] or "unnamed bearer"
    heir = (successor or "").strip()[:160]
    why = (reason or "dissolved").strip()[:160] or "dissolved"
    has_heir = bool(heir)
    rid = f"est_{uuid.uuid4().hex[:16]}"
    folio = remaining_mod.folio(jid)
    receipt = {
        "spec": SPEC,
        "kind": "estate_receipt",
        "ok": True,
        "id": rid,
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "job_id": jid,
        "bearer": who,
        "successor": heir or None,
        "reason": why,
        "disposition": "inherit" if has_heir else "wind_down",
        "leftover_writes": "named_successor" if has_heir else "HALT",
        "probated_at": _iso(),
        "folio_still_exists": True,
        "folio_identity_holds": folio.get("identity_holds"),
        "deletion": False,
        "actor_cannot_self_probate": True,
        "estate_is_not_admin_resurrect": True,
        "charge_outside": True,
        "may_sold": False,
        "being_sold": False,
        "payee": PAYEE,
        "until_gate1_usd": ESTATE_USD,
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "time_source": time_source_mod.attest(),
    }
    _ESTATES[jid] = receipt
    return receipt


def open_both(job_id: str) -> dict[str, Any]:
    """A stranger opens the folio and the estate. That is the product."""
    jid = (job_id or "").strip()[:160]
    folio = remaining_mod.folio(jid)
    rec = _ESTATES.get(jid)
    return {
        "spec": SPEC,
        "kind": "stranger_opens_estate",
        "identity": IDENTITY,
        "state": state(jid),
        "folio": folio,
        "estate": rec,
        "deletion": False,
        "the_record_is_not_the_bearer": True,
    }


def pack(
    job_id: str,
    bearer: str = "",
    successor: str = "",
    reason: str = "dissolved",
    public_url: str = "",
    contact_email: str = "",
) -> dict[str, Any]:
    """They pay. We probate one bearer. They attach it. They do not implement."""
    jid = (job_id or "").strip()[:160] or f"pc:EST-PAY-{uuid.uuid4().hex[:12]}"
    issued = probate(jid, bearer=bearer, successor=successor, reason=reason)
    both = open_both(jid)
    return {
        "spec": SPEC,
        "kind": "estate_of_remaining_pack",
        "inventor": inventor_mod.stamp(),
        "job_id": jid,
        "price": ESTATE_LABEL,
        "until_gate1_usd": ESTATE_USD,
        "operated_by": "Nisaba LLC",
        "payee": PAYEE,
        "they_do_not_implement_gate": True,
        "identity": IDENTITY,
        "receipt": issued,
        "open_both": both,
        "deletion": False,
        "folio_still_exists": True,
        "actor_cannot_self_probate": True,
        "estate_is_not_admin_resurrect": True,
        "charge_outside": True,
        "time_source": time_source_mod.attest(),
        "distinct_from": {
            "discharge": "standing lapsed — $1,500",
            "null": "killed try — $4,500",
            "refusal": "will not ship — $7,500",
            "finished": "live write — $8,500",
        },
        "may_sold": False,
        "being_sold": False,
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "their_production": False,
        "not": [
            "deletion",
            "admin CHARGE",
            "actor self-probate",
            "admin self-resurrect",
            "Discharge (that is standing)",
            "Null (that is a killed try)",
            "Being",
            "immunity",
        ],
        "evaluated_at": _iso(),
        "page": f"{(public_url or '').rstrip('/')}/estate" if public_url else "/estate",
        "contact": contact_email or None,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Estate of Remaining",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "thesis": THESIS,
        "email_line": EMAIL_LINE,
        "skus": {k: {kk: vv for kk, vv in v.items() if kk != "stripe_desc"} for k, v in SKUS.items()},
        "vacancy_test": {
            "identifier": "job_id + bearer",
            "contribution_rule": "bearer gone + no probate → leftover writes are orphaned LIVE",
            "chokepoint": "leftover writes cannot proceed without probate when the bearer is gone",
        },
        "failure_class": "2.3 the bearer is gone",
        "not": [
            "deletion",
            "admin CHARGE",
            "actor self-probate",
            "admin self-resurrect",
            "Discharge",
            "Null",
            "Being",
            "immunity",
        ],
        "payee": PAYEE,
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "not_museum": True,
        "until_gate1_usd": ESTATE_USD,
        "checkout": f"{base}/estate/checkout",
        "cash_now": True,
        "prints_when": "they pay — we probate — they open folio and successor",
        "cash_door": f"{base}/estate",
        "page": f"{base}/estate",
        "links": {
            "page": f"{base}/estate",
            "discharge": f"{base}/discharge",
            "null": f"{base}/null",
            "remaining": f"{base}/remaining",
            "finished": f"{base}/finished",
            "bind_room": f"{base}/bind-room",
        },
        "gatekeep": (
            "Cash SKU. Bearer gone. Remaining is probated, not orphaned LIVE. "
            "Not Discharge. Not Null. Not a sixth sibling. $3,500 operated estate."
        ),
    }
