"""Mouth / finality diligence — paid find where irreversible write completes without may.

Surfaces (must stay live for hustle outbound):
  GET  /diligence
  GET  /diligence/one-pager.txt
  GET  /diligence/offer.json
  POST /diligence/checkout  — deposit from commerce SSOT
"""
from __future__ import annotations

from typing import Any

try:
    from gate import commerce as commerce_mod
except ImportError:
    import commerce as commerce_mod  # type: ignore

SPEC = "gate-diligence-offer-v1"
DEPOSIT_LABEL = commerce_mod.price_label("diligence_deposit")
REVIEW_BAND = "$5,000–$8,000"
RETAINER_BAND = "$10,000–$40,000/mo"
DELIVERY = "72h"


def offer(public_url: str, contact_email: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Mouth / finality diligence",
        "firm": "Nisaba LLC",
        "offer": "Where can an irreversible write complete without may?",
        "not": [
            "Not a pentest gym",
            "Not a soft governance PDF",
            "Not selling may",
            "Not implementing the rail on this SKU",
        ],
        "price": {
            "deposit": DEPOSIT_LABEL,
            "deposit_due": "now",
            "review": REVIEW_BAND,
            "retainer": RETAINER_BAND,
            "delivery": DELIVERY,
        },
        "targets": [
            "peg-outs / bridges",
            "custody withdraw",
            "payout / mass pay",
            "BaaS / sponsor edges",
            "bind desks (path review)",
        ],
        "deliverable": (
            "Written map of mouths where an irreversible write can complete without may, "
            "with stranger-openable halt gap named. Deposit starts the clock."
        ),
        "ask": "Reply DEPOSIT — invoice same day.",
        "halt": "We will not sell may. We will not implement the rail on this SKU.",
        "urls": {
            "page": f"{base}/diligence",
            "one_pager": f"{base}/diligence/one-pager.txt",
            "offer": f"{base}/diligence/offer.json",
            "checkout": f"{base}/diligence/checkout",
            "bind_room": f"{base}/bind-room",
            "verify": "https://velaru.xyz/verify",
        },
        "contact": contact_email,
        "their_production": False,
    }


def one_pager(public_url: str, contact_email: str) -> str:
    base = (public_url or "").rstrip("/")
    return f"""MOUTH / FINALITY DILIGENCE — Nisaba LLC
═══════════════════════════════════════

Offer
  Where can an irreversible write complete without may?

Price
  Deposit {DEPOSIT_LABEL} due now
  Review {REVIEW_BAND}
  Retainer band {RETAINER_BAND}
  Delivery {DELIVERY} after deposit clears

What you get
  A written find on your irreversible path (peg-out, withdraw, payout, bind, ACH credit):
  where the write can still complete when Clear / stranger-openable halt is missing.
  Keys, SOC, and policy answers are not the deliverable — the may-gap is.

What this is not
  Not a pentest gym. Not a governance PDF. Not selling may.
  Not implementing Gate/Prefinality rail on this SKU.

Ask
  Reply DEPOSIT — invoice same day.
  Or pay: {base}/diligence

Links
  {base}/diligence
  {base}/diligence/one-pager.txt
  {base}/diligence/offer.json
  Stranger verify: https://velaru.xyz/verify
  Bind Room (separate SKU): {base}/bind-room

Contact
  {contact_email}

their_production: false until a recorded third-party weld.
"""


def page_copy() -> dict[str, str]:
    return {
        "headline": "Where can an irreversible write complete without may?",
        "sub": (
            "Mouth / finality diligence. Paid find on peg-out, withdraw, payout, "
            "BaaS credit, or bind path — the gap between who was allowed and what "
            "actually halted the write."
        ),
    }
