"""Mouth / finality diligence — free REVIEW + paid deposit find.

Surfaces (must stay live for hustle outbound):
  GET  /diligence              — free REVIEW hero + paid deposit
  GET  /diligence/one-pager.txt
  GET  /diligence/offer.json
  POST /diligence/checkout     — $2,500 deposit (paid SKU)
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-diligence-offer-v2"
DEPOSIT_LABEL = "$2,500"
REVIEW_BAND = "$5,000–$8,000"
RETAINER_BAND = "$10,000–$40,000/mo"
DELIVERY = "72h"
FREE_ASK = "Reply REVIEW"
PAID_ASK = "Reply DEPOSIT — invoice same day."


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
        "paths": {
            "free_review": {
                "ask": FREE_ASK,
                "price": "$0",
                "scope": "Public pages only (+ anything you send). 72h memo.",
                "obligation": "None. No invoice.",
            },
            "paid_deposit": {
                "ask": PAID_ASK,
                "deposit": DEPOSIT_LABEL,
                "deposit_due": "now",
                "review": REVIEW_BAND,
                "retainer": RETAINER_BAND,
                "delivery": f"{DELIVERY} after deposit clears",
            },
        },
        # Keep legacy price block for older readers; paid path only.
        "price": {
            "deposit": DEPOSIT_LABEL,
            "deposit_due": "now",
            "review": REVIEW_BAND,
            "retainer": RETAINER_BAND,
            "delivery": DELIVERY,
            "free_review": "$0",
        },
        "targets": [
            "peg-outs / bridges",
            "custody withdraw",
            "payout / mass pay",
            "BaaS / sponsor edges",
            "bind desks (path review)",
        ],
        "deliverable": (
            "Free REVIEW: 72h memo on public pages (and anything you send) naming where "
            "the next irreversible placement still treats collateral / authority as live "
            "without confirm. Paid deposit: deeper written map of mouths where an "
            "irreversible write can complete without may."
        ),
        "ask": FREE_ASK,
        "ask_paid": PAID_ASK,
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
    }


def one_pager(public_url: str, contact_email: str) -> str:
    base = (public_url or "").rstrip("/")
    return f"""MOUTH / FINALITY DILIGENCE — Nisaba LLC
═══════════════════════════════════════

Offer
  Where can an irreversible write complete without may?

PATH 1 — FREE REVIEW (cold outbound / Monday pack)
  Price     $0 · no invoice · no obligation
  Scope     Public pages only (+ anything you send)
  Delivery  72h memo
  Ask       {FREE_ASK}
  Contact   {contact_email}

PATH 2 — PAID DEPOSIT (deeper find)
  Deposit   {DEPOSIT_LABEL} due now
  Review    {REVIEW_BAND}
  Retainer  {RETAINER_BAND}
  Delivery  {DELIVERY} after deposit clears
  Ask       {PAID_ASK}
  Or pay    {base}/diligence

What you get (either path)
  A written find on the irreversible path (peg-out, withdraw, payout, bind, ACH credit /
  collateral / authority): where the write can still complete when Clear / stranger-openable
  halt is missing. Keys, SOC, and policy answers are not the deliverable — the may-gap is.

What this is not
  Not a pentest gym. Not a governance PDF. Not selling may.
  Not implementing Gate/Prefinality rail on this SKU.

Links
  {base}/diligence
  {base}/diligence/one-pager.txt
  {base}/diligence/offer.json
  Stranger verify: https://velaru.xyz/verify
  Bind Room (separate SKU): {base}/bind-room

Contact
  {contact_email}
"""


def page_copy() -> dict[str, str]:
    return {
        "headline": "Where can an irreversible write complete without may?",
        "sub": (
            "Mouth / finality diligence. Free 72h REVIEW on public pages — or a paid "
            "deposit find on peg-out, withdraw, payout, BaaS credit, or bind path. "
            "The gap between who was allowed and what actually halted the write."
        ),
        "free_blurb": (
            "Public pages only (+ anything you send). No charge. No invoice. "
            "No obligation. If it is useless, delete it."
        ),
    }
