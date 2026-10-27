"""Diligence — free REVIEW + paid deposit find.

First screen uses desk language (collateral confirmation, duty to defend,
binder authority) before Gate nouns. Surfaces for hustle outbound:
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
        "name": "Diligence — collateral, duty to defend, binder authority",
        "firm": "Nisaba LLC",
        "offer": "Where does the next bind still treat collateral, duty to defend, or binder authority as live?",
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
            "collateral confirmation (LOC / letter treated as live)",
            "duty to defend after refusal",
            "binder authority after the MGA walked",
            "bind desks (path review)",
        ],
        "deliverable": (
            "Free REVIEW: 72h memo on public pages (and anything you send) naming where "
            "the next placement still treats collateral, duty to defend, or binder "
            "authority as live without confirm. Paid deposit: deeper written map of "
            "the same gaps."
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
    return f"""DILIGENCE — Nisaba LLC
═══════════════════════════════════════

Offer
  Where does the next bind still treat collateral, duty to defend, or binder authority as live?

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
  A written find on collateral confirmation, duty to defend, and binder authority:
  where the next placement still treats the letter, the defense, or the binder as
  live without confirm. Keys, SOC, and policy answers are not the deliverable.

What this is not
  Not a pentest gym. Not a governance PDF. Not selling coverage.
  Not implementing the rail on this SKU.

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
        "headline": "Where does the next bind still treat collateral, duty to defend, or binder authority as live?",
        "sub": (
            "Free 72h REVIEW of public pages. As of the NAIC SVO List of Qualified "
            "U.S. Financial Institutions dated September 30, 2026, China Construction "
            "Bank does not appear (it was on the December 31, 2025 list). This issuer "
            "is off the current list, so the next evergreen/renewal cannot support "
            "surplus credit. Model 786 §11A(3) grandfathers an LOC acceptable at "
            "issuance until it is expired, extended, renewed, modified, or amended. "
            "Phone or email-on-the-instrument confirmation is not the check. Duty to "
            "defend after a refusal. Binder authority after the MGA walked. Or a paid "
            "deposit find on the same path."
        ),
        "free_blurb": (
            "Public pages only (+ anything you send). No charge. No invoice. "
            "No obligation. If it is useless, delete it."
        ),
    }
