"""Priced act rents — keep-alive, query, silence lease.

Visa stacks several rents on one act. We had an acquirer stub
(hop + bps + floor + QIC). These three have a mouth now.

Not a sixth sibling. Not a /for/ plate. Not Being. Never sell may.
100% Nisaba LLC. They do not implement Gate.
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
    from gate import prefinality as prefinality_mod
except ImportError:
    import prefinality as prefinality_mod

SPEC = "gate-priced-act-rents-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None
PAYEE = "Nisaba LLC"
NO_SPLIT = True

KEEPALIVE_LABEL = "$1,200/mo"
KEEPALIVE_CENTS = 120_000
QUERY_LABEL = "$2,000/mo"
QUERY_CENTS = 200_000
SILENCE_LABEL = "$1,500/mo"
SILENCE_CENTS = 150_000

IDENTITY = "the same act is rented more than once"
THESIS = (
    "A network charges the same act several times. We had hop + bps + floor. "
    "Keep-alive rents the unspent window. Query rents the ask after. "
    "Silence lease rents the no that must stay live. 100% Nisaba. "
    "They never implement. Cancel and the window dies, the ask goes dark, "
    "the no goes stale."
)

EMAIL_LINE = (
    "Keep a GO window live — $1,200/mo. Ask what remained — $2,000/mo. "
    "Keep a named agent unshipped — $1,500/mo. Not hops. Not a weld."
)

SKUS: dict[str, dict[str, Any]] = {
    "prefinality_keepalive": {
        "id": "prefinality_keepalive",
        "name": "Prefinality keep-alive",
        "label": KEEPALIVE_LABEL,
        "cents": KEEPALIVE_CENTS,
        "interval": "month",
        "on": "unspent may",
        "stripe_name": "Prefinality keep-alive — one job, monthly",
        "stripe_desc": "We refresh the 300s GO window on one named job so unspent may does not die.",
        "who": "A deployer whose agent waits on a live evaluate and cannot re-buy the window every five minutes",
        "deliverable": (
            "Monthly keep-alive for one job_id. TTL refresh of an unspent may. "
            "May is not sold. The window is rented. Stops when they cancel."
        ),
        "why_now": (
            "Prefinality already exists. TTL is 300s. Nobody paid to keep the "
            "window from dying. That is rent on the act before flow."
        ),
        "surpasses": (
            "Standing is the folio kept true. This is thinner: only the window. "
            "$1,200/mo and they never weld."
        ),
        "stacks": "N jobs × $1,200/mo. Ten waiting agents = $12,000/mo to the mouth.",
        "subject": "job_id",
        "subject_placeholder": "job id (or later)",
    },
    "query_remaining": {
        "id": "query_remaining",
        "name": "Query of remaining",
        "label": QUERY_LABEL,
        "cents": QUERY_CENTS,
        "interval": "month",
        "on": "after_act",
        "stripe_name": "Query of remaining — unmetered asks, monthly",
        "stripe_desc": "Unmetered stranger-openable asks of one remaining folio for one legal person.",
        "who": "Counsel / underwriter / counterpart who needs to *ask* what happened, not write it",
        "deliverable": (
            "Monthly query seat for one legal person on named remaining. "
            "They ask. We open the stock. Not a write. Not Standing."
        ),
        "why_now": (
            "Bloomberg does not charge you to issue a bond. It charges you to "
            "look. The folio exists. The ask was free."
        ),
        "surpasses": (
            "Standing $4,500/mo is we operate the write. This is $2,000/mo to "
            "ask. Read is not write."
        ),
        "stacks": "One seat = $2,000/mo. A book of six askers = $12,000/mo.",
        "subject": "legal_person",
        "subject_placeholder": "legal person (who asks)",
    },
    "silence_lease": {
        "id": "silence_lease",
        "name": "Silence lease",
        "label": SILENCE_LABEL,
        "cents": SILENCE_CENTS,
        "interval": "month",
        "on": "anti_act",
        "stripe_name": "Silence lease — keep the no live, monthly",
        "stripe_desc": "The Refusal souvenir ages. We keep one named agent unshipped every month.",
        "who": "Board / GC who already bought Refusal or will not ship an unbound agent",
        "deliverable": (
            "Monthly operated no for one named agent. Cancel and the next "
            "board pack is stale. Refusal is the souvenir. This is the lease."
        ),
        "why_now": (
            "Refusal is $7,500 once. Boards need the no to still be true at "
            "the next meeting. Anti-act as rent."
        ),
        "surpasses": "A signed PDF ages. A leased no does not — until they stop paying.",
        "stacks": "N agents × $1,500/mo. A killed slate of eight = $12,000/mo.",
        "subject": "named_agent",
        "subject_placeholder": "named agent we will not ship",
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


def keep_alive(job_id: str) -> dict[str, Any]:
    """Refresh an unspent window. May is not sold."""
    jid = (job_id or "").strip()[:160]
    ttl = int(getattr(prefinality_mod, "DEFAULT_TTL_SECONDS", 300))
    return {
        "spec": SPEC,
        "kind": "prefinality_keepalive",
        "sku": "prefinality_keepalive",
        "inventor": inventor_mod.stamp(),
        "job_id": jid or None,
        "ttl_seconds": ttl,
        "window_kept": True,
        "unspent_may_sold": False,
        "being_sold": False,
        "payee": PAYEE,
        "price": KEEPALIVE_LABEL,
        "interval": "month",
        "stale_if_canceled": True,
        "they_do_not_implement_gate": True,
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "their_production": False,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def query(job_id: str, legal_person: str = "") -> dict[str, Any]:
    """Pay to ask what remained. Not a write."""
    folio = remaining_mod.folio(job_id)
    who = (legal_person or "").strip()[:160]
    return {
        "spec": SPEC,
        "kind": "query_of_remaining",
        "sku": "query_remaining",
        "inventor": inventor_mod.stamp(),
        "legal_person": who or None,
        "write": False,
        "ask": True,
        "folio": folio,
        "payee": PAYEE,
        "price": QUERY_LABEL,
        "interval": "month",
        "stale_if_canceled": True,
        "they_do_not_implement_gate": True,
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "their_production": False,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def silence(named_agent: str) -> dict[str, Any]:
    """Lease of a named no. Refusal is the souvenir."""
    name = (named_agent or "").strip()[:160]
    return {
        "spec": SPEC,
        "kind": "silence_lease",
        "sku": "silence_lease",
        "inventor": inventor_mod.stamp(),
        "named_agent": name or None,
        "refusal_is_souvenir": True,
        "anti_act": True,
        "may_sold": False,
        "being_sold": False,
        "payee": PAYEE,
        "price": SILENCE_LABEL,
        "interval": "month",
        "stale_if_canceled": True,
        "they_do_not_implement_gate": True,
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "their_production": False,
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
    }


def run(sku: str, subject: str = "") -> dict[str, Any]:
    if sku == "prefinality_keepalive":
        return keep_alive(subject)
    if sku == "query_remaining":
        return query(subject, legal_person=subject)
    if sku == "silence_lease":
        return silence(subject)
    return keep_alive(subject)


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Priced act rents",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "thesis": THESIS,
        "email_line": EMAIL_LINE,
        "payee": PAYEE,
        "no_split": NO_SPLIT,
        "connect": False,
        "distribution": "none — 100% Nisaba LLC",
        "never_sell": list(inventor_mod.INVENTOR["never_sell"]),
        "skus": {k: dict(v) for k, v in SKUS.items()},
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "not_museum": True,
        "not_september_spray": True,
        "cash_door": f"{base}/acts",
        "checkout": f"{base}/acts/checkout",
        "map": f"{base}/flows",
        "links": {
            "page": f"{base}/acts",
            "flows": f"{base}/flows",
            "standing": f"{base}/standing",
            "refusal": f"{base}/refusal",
            "remaining": f"{base}/remaining",
            "prefinality": f"{base}/.well-known/prefinality.json",
        },
        "page": f"{base}/acts",
        "gatekeep": (
            "Act-rent cash door. Not a /for/ plate. Not a sixth sibling. "
            "Not interchange. Not a facilitator. September is still Bind."
        ),
    }
