"""Null Remaining — failure has a remaining. The killed try is the stock.

Refusal is a will-not-ship. Finished is a live write. This is the sealed
remaining of a try that already failed. Boards buy CYA on a killed agent
project. Clinical trials invented the null result. Engineering never sold it.

They do not implement Gate. We seal one failed try. They attach the folio.

Not a sixth sibling. Not a /for/ plate. Not Being. Never sell may.
Checkout is live. $4,500 operated null pack.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import uuid

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

SPEC = "gate-null-remaining-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None
PAYEE = "Nisaba LLC"

NULL_LABEL = "$4,500"
NULL_CENTS = 450_000
NULL_USD = 4500

IDENTITY = "failure has a remaining"
THESIS = (
    "A killed try without a remaining is a postmortem PDF. The board cannot "
    "open it. Clinical trials invented the null result so generation does not "
    "rerun blind. We seal the folio of the failed try. Distinct from Refusal "
    "(will not ship) and Finished (live write)."
)

EMAIL_LINE = (
    "You killed the agent. The minutes need a remaining, not another postmortem. "
    "Null Remaining is the sealed folio of the failed try — $4,500. "
    "Not a will-not-ship. Not a live write."
)

SKUS: dict[str, dict[str, Any]] = {
    "null_remaining": {
        "id": "null_remaining",
        "name": "Null Remaining",
        "label": NULL_LABEL,
        "cents": NULL_CENTS,
        "stripe_name": "Null Remaining — sealed remaining of a killed try",
        "stripe_desc": "Failure has a remaining. We seal the try that did not succeed. Board can open it.",
        "who": "Board / GC who killed an agent project and needs a remaining that is not a will-not-ship",
        "deliverable": (
            "Operated null pack: remaining folio of the failed try, sealed, "
            "stranger-openable. They never implement."
        ),
        "why_now": (
            "They already killed it. The minutes need a remaining, not another "
            "postmortem PDF."
        ),
        "surpasses": (
            "Refusal is absence of a future act. This is the stock of a past failure. "
            "Clinical trials invented this. Engineering never sold it."
        ),
    },
}


def stripe_line_item(sku: str = "null_remaining") -> dict[str, Any]:
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


def pack(job_id: str, tried: str = "", public_url: str = "", contact_email: str = "") -> dict[str, Any]:
    """They pay. We seal the failed try. They attach it. They do not implement."""
    jid = (job_id or "").strip()[:160] or f"pc:NULL-PAY-{uuid.uuid4().hex[:12]}"
    what = (tried or "").strip()[:200] or "killed agent write"
    sealed = remaining_mod.null_result(jid, what)
    return {
        "spec": SPEC,
        "kind": "null_remaining_pack",
        "inventor": inventor_mod.stamp(),
        "job_id": jid,
        "tried": what,
        "price": NULL_LABEL,
        "until_gate1_usd": NULL_USD,
        "operated_by": "Nisaba LLC",
        "payee": PAYEE,
        "they_do_not_implement_gate": True,
        "identity": IDENTITY,
        "sealed": sealed,
        "succeeded": False,
        "not_a_win": True,
        "generation_does_not_rerun_blind": True,
        "time_source": time_source_mod.attest(),
        "distinct_from": {
            "refusal": "will not ship — $7,500",
            "finished": "live write — $8,500",
            "discharge": "standing lapsed — $1,500",
            "estate": "bearer gone — $3,500",
        },
        "may_sold": False,
        "being_sold": False,
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "their_production": False,
        "not": [
            "a will-not-ship (that is Refusal)",
            "a live write (that is Finished)",
            "a postmortem PDF",
            "Being",
            "immunity",
        ],
        "evaluated_at": datetime.now(timezone.utc).isoformat(),
        "page": f"{(public_url or '').rstrip('/')}/null" if public_url else "/null",
        "contact": contact_email or None,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Null Remaining",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "thesis": THESIS,
        "email_line": EMAIL_LINE,
        "skus": {k: {kk: vv for kk, vv in v.items() if kk != "stripe_desc"} for k, v in SKUS.items()},
        "payee": PAYEE,
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "not_museum": True,
        "until_gate1_usd": NULL_USD,
        "checkout": f"{base}/null/checkout",
        "cash_now": True,
        "prints_when": "they pay — we seal the failed try — they attach",
        "cash_door": f"{base}/null",
        "page": f"{base}/null",
        "links": {
            "page": f"{base}/null",
            "remaining": f"{base}/remaining",
            "discharge": f"{base}/discharge",
            "refusal": f"{base}/refusal",
            "finished": f"{base}/finished",
            "bind_room": f"{base}/bind-room",
        },
        "gatekeep": (
            "Cash SKU. Failure has a remaining. Not Refusal. Not Finished. "
            "Not a sixth sibling. $4,500 operated null pack."
        ),
    }
