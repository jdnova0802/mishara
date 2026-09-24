"""Trusted Contact Hold — elder-fraud unlock/hold Diligence (bind-ticket reuse).

Mouth: may this irreversible unlock (transfer / payout / access) proceed without
a sealed trusted-contact hold firing first?

Surfaces:
  GET  /trusted-contact
  GET  /trusted-contact/one-pager.txt
  GET  /trusted-contact/offer.json
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-trusted-contact-offer-v1"
DEPOSIT_LABEL = "$2,500"
REVIEW_BAND = "$5,000–$8,000"
DELIVERY = "72h"


def offer(public_url: str, contact_email: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Trusted Contact Hold",
        "firm": "Nisaba LLC",
        "offer": (
            "May this irreversible unlock proceed without a sealed trusted-contact "
            "hold — and can a stranger verify the hold ticket?"
        ),
        "direction": "unlock_hold",
        "architecture": "Reuses bind-ticket / Positive Clear unlock mouth — named module for elder-fraud hold paths.",
        "not": [
            "Not a new core engine — bind-ticket pattern, elder-fraud label",
            "Not a brokerage Reg BI product reseller",
            "Not implementing CRM on this SKU",
        ],
        "price": {
            "deposit": DEPOSIT_LABEL,
            "review": REVIEW_BAND,
            "delivery": DELIVERY,
            "free_review": "Reply REVIEW — one unlock/hold path, 72h",
        },
        "targets": [
            "brokerage / RIA trusted-contact holds",
            "bank elder-fraud payout delays",
            "benefits release with nominated contact",
            "family-office treasury unlock",
        ],
        "deliverable": (
            "72h memo on one unlock path: where funds or access can still release "
            "without a stranger-verifiable trusted-contact hold ticket (who was "
            "notified, when, what was blocked)."
        ),
        "ask": "Reply REVIEW — no charge, no invoice, no obligation.",
        "urls": {
            "page": f"{base}/trusted-contact",
            "one_pager": f"{base}/trusted-contact/one-pager.txt",
            "offer": f"{base}/trusted-contact/offer.json",
            "positive_clear": f"{base}/positive-clear",
            "bind_room": f"{base}/bind-room",
            "diligence": f"{base}/diligence",
            "verify": "https://velaru.xyz/verify",
        },
        "contact": contact_email,
        "their_production": False,
    }


def one_pager(public_url: str, contact_email: str) -> str:
    base = (public_url or "").rstrip("/")
    return f"""TRUSTED CONTACT HOLD — Nisaba LLC
══════════════════════════════════

Mouth
  May this irreversible unlock proceed without a sealed trusted-contact
  hold — and can a stranger verify the hold ticket?

Architecture
  Same Clear / Seal / Go / Never unlock mouth as Positive Clear.
  Named module for elder-fraud / nominated-contact hold paths.
  Reuses bind-ticket pattern — not a new engine.

Offer
  Free 72h REVIEW of one unlock/hold path: brokerage trusted contact,
  bank elder-fraud delay, benefits release with nominated contact.

Ask
  Reply REVIEW — no charge, no invoice, no obligation.
  Or deposit: {base}/diligence
  Sibling unlock: {base}/positive-clear

Links
  {base}/trusted-contact
  {base}/trusted-contact/one-pager.txt
  {base}/trusted-contact/offer.json
  Stranger verify: https://velaru.xyz/verify

Contact
  {contact_email}

their_production: false
"""


def page_copy() -> dict[str, str]:
    return {
        "headline": "Trusted Contact Hold — Seal before the unlock",
        "sub": (
            "Elder-fraud / nominated-contact paths. May funds or access release "
            "without a stranger-verifiable hold ticket? Same unlock architecture "
            "as Positive Clear — named module, not a new engine."
        ),
    }
