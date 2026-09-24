"""Payment-ops review — free 72h first. Deposit only after a real find.

Was: mouth/finality diligence with DEPOSIT-now. That pattern-matched a
disclosure shakedown. This SKU is a vendor review of one named payment
path from public docs + what they send. Not a vuln report. Not remaining sold.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-ops-review-v2"
DEPOSIT_LABEL = "$2,500"
REVIEW_BAND = "$5,000–$8,000"
RETAINER_BAND = "$10,000–$40,000/mo"
DELIVERY = "72h"


def offer(public_url: str, contact_email: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Payment-ops review",
        "firm": "Nisaba LLC",
        "offer": "Free 72-hour written review of one named payment path. No deposit, no obligation.",
        "not": [
            "Not a security disclosure",
            "Not a vulnerability report",
            "Not a pentest",
            "Not selling permission on your rail",
        ],
        "price": {
            "front": "free 72-hour review",
            "deposit": DEPOSIT_LABEL,
            "deposit_due": "only after the free review produces something you want to keep",
            "review": REVIEW_BAND,
            "retainer": RETAINER_BAND,
            "delivery": DELIVERY,
        },
        "targets": [
            "book transfer / hold-and-clear",
            "RTP / ACH origination",
            "payment-order approval vs posted",
            "mass-payout batch vs payee payable",
        ],
        "deliverable": (
            "A short written review of one path you name (or we pick from your public docs): "
            "where permission is supposed to sit before funds post. Draft. Not legal advice."
        ),
        "ask": "Reply REVIEW — no invoice until after the free review.",
        "halt": "We will not file this as a vulnerability. We will not implement your rail on this SKU.",
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
    return f"""PAYMENT-OPS REVIEW — Nisaba LLC
════════════════════════════════

Offer
  Free 72-hour written review of one named payment path.
  No deposit. No obligation. No reply token that invoices you.

What you get
  A short memo on where permission is supposed to sit before funds post,
  using your public docs plus anything you choose to send. One path only.

What this is not
  Not a security disclosure. Not a vulnerability report. Not a pentest.
  Not selling permission on your rail.

After the free review
  If the memo is useful, a paid follow-on is optional
  (deposit {DEPOSIT_LABEL} then review {REVIEW_BAND}; retainer {RETAINER_BAND}).
  That conversation happens after the review, not before.

Ask
  Reply REVIEW to {contact_email}
  Page: {base}/diligence

Links
  {base}/diligence
  {base}/diligence/one-pager.txt
  {base}/diligence/offer.json

their_production: false until a recorded third-party weld.
"""


def page_copy() -> dict[str, str]:
    return {
        "headline": "Free 72-hour review of one named payment path.",
        "sub": (
            "Payment ops, not a security inbox. We read the path you name — "
            "book transfer, RTP origination, payment order, mass payout — "
            "and write where permission is supposed to sit before funds post. "
            "No deposit to start."
        ),
    }
