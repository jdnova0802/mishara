"""Positive Clear — unlock-direction diligence (inverse of deny-side Clear/Seal/Go/Never).

Same architecture, zero new eng. Mouth: may this irreversible *unlock* proceed?

Surfaces:
  GET  /positive-clear
  GET  /positive-clear/one-pager.txt
  GET  /positive-clear/offer.json
  POST /positive-clear/checkout  — same $2,500 deposit rail as /diligence
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-positive-clear-offer-v1"
DEPOSIT_LABEL = "$2,500"
REVIEW_BAND = "$5,000–$8,000"
RETAINER_BAND = "$10,000–$40,000/mo"
DELIVERY = "72h"


def offer(public_url: str, contact_email: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Positive Clear — unlock diligence",
        "firm": "Nisaba LLC",
        "offer": "May this irreversible unlock proceed — and can a stranger verify the Clear?",
        "direction": "unlock",  # inverse of deny-side Halt / Never
        "not": [
            "Not a new core product — same Clear/Seal/Go mouth, unlock side",
            "Not benefits/payroll software",
            "Not selling may without a Seal",
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
            "benefits / claims release",
            "payroll / mass-pay push",
            "access provisioning / entitlement unlock",
            "Bind Room–shaped release paths",
            "treasury unlock after hold",
        ],
        "deliverable": (
            "Written map of where an irreversible unlock (release, push, provision) "
            "can still fire without Clear + stranger-openable Seal — halt gap named. "
            "Deposit starts the clock. Free REVIEW maps one path."
        ),
        "ask": "Reply REVIEW (one unlock path, free 72h) or DEPOSIT — invoice same day.",
        "halt": "We will not sell may. Unlock without Seal is still Never.",
        "sibling": {
            "deny_side": f"{base}/diligence",
            "bind_room": f"{base}/bind-room",
            "clear": f"{base}/clear",
        },
        "urls": {
            "page": f"{base}/positive-clear",
            "one_pager": f"{base}/positive-clear/one-pager.txt",
            "offer": f"{base}/positive-clear/offer.json",
            "checkout": f"{base}/positive-clear/checkout",
            "diligence": f"{base}/diligence",
            "bind_room": f"{base}/bind-room",
            "verify": "https://velaru.xyz/verify",
        },
        "contact": contact_email,
        "their_production": False,
    }


def one_pager(public_url: str, contact_email: str) -> str:
    base = (public_url or "").rstrip("/")
    return f"""POSITIVE CLEAR — unlock diligence — Nisaba LLC
══════════════════════════════════════════════

Offer
  May this irreversible unlock proceed — and can a stranger verify the Clear?

Direction
  Deny-side Gate asks: may this irreversible write proceed? (halt / Never)
  Positive Clear asks the inverse: may this irreversible *unlock* proceed?
  Same Clear / Seal / Go / Never mouth. Zero new engineering.

Price
  Deposit {DEPOSIT_LABEL} due now
  Review {REVIEW_BAND}
  Retainer band {RETAINER_BAND}
  Delivery {DELIVERY} after deposit clears
  Free REVIEW: one unlock path, 72h memo — reply REVIEW

What you get
  A written find on benefits release, payroll push, access provision, or
  Bind Room–shaped unlock: where the release can still fire when Clear +
  stranger-openable Seal is missing.

What this is not
  Not a new core product. Not benefits/payroll software. Not selling may.
  Not implementing Gate rail on this SKU.

Ask
  Reply REVIEW — free 72h on one unlock path.
  Reply DEPOSIT — invoice same day.
  Or pay: {base}/positive-clear

Links
  {base}/positive-clear
  {base}/positive-clear/one-pager.txt
  {base}/positive-clear/offer.json
  Deny-side sibling: {base}/diligence
  Bind Room: {base}/bind-room
  Stranger verify: https://velaru.xyz/verify

Contact
  {contact_email}

their_production: false until a recorded third-party weld.
"""


def page_copy() -> dict[str, str]:
    return {
        "headline": "May this irreversible unlock proceed?",
        "sub": (
            "Positive Clear — the unlock side of Clear / Seal / Go / Never. "
            "Benefits release, payroll push, access provision, Bind Room–shaped "
            "unlock: where the release can still fire without a stranger-verifiable Clear."
        ),
    }
