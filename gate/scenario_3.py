"""FIN-2016-A003 Scenario 3 Check — named vendor bank-change Diligence SKU.

Headline is the FinCEN typology itself. Same REVIEW/deposit rails as /diligence.

Surfaces:
  GET  /scenario-3
  GET  /scenario-3/one-pager.txt
  GET  /scenario-3/offer.json
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-scenario-3-offer-v1"
DEPOSIT_LABEL = "$2,500"
REVIEW_BAND = "$5,000–$8,000"
DELIVERY = "72h"
FINCEN = "FIN-2016-A003"
SCENARIO = "Scenario 3 — Criminal Impersonates a Supplier"


def offer(public_url: str, contact_email: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "FIN-2016-A003 Scenario 3 Check",
        "firm": "Nisaba LLC",
        "primary": {
            "advisory": FINCEN,
            "scenario": SCENARIO,
            "url": "https://www.fincen.gov/resources/advisories/fincen-advisory-fin-2016-a003",
        },
        "offer": (
            "Before AP updates vendor bank details or releases ACH/wire — "
            "prove out-of-band callback + dual approve as a stranger-verifiable Seal, "
            "or the master-data write is Never."
        ),
        "not": [
            "Not a new fraud product — FinCEN already named the pattern",
            "Not an account-validation API reseller",
            "Not implementing the rail on this SKU",
        ],
        "price": {
            "deposit": DEPOSIT_LABEL,
            "review": REVIEW_BAND,
            "delivery": DELIVERY,
            "free_review": "Reply REVIEW — one vendor pay path, 72h",
        },
        "deliverable": (
            "72h memo on one supplier master-data / pay path: where Scenario 3 "
            "(email → new account number → update vendor record → wire) can still "
            "complete without sealed callback + dual approve."
        ),
        "ask": "Reply REVIEW — no charge, no invoice, no obligation.",
        "urls": {
            "page": f"{base}/scenario-3",
            "one_pager": f"{base}/scenario-3/one-pager.txt",
            "offer": f"{base}/scenario-3/offer.json",
            "diligence": f"{base}/diligence",
            "checkout": f"{base}/diligence/checkout",
            "verify": "https://velaru.xyz/verify",
        },
        "contact": contact_email,
        "their_production": False,
    }


def one_pager(public_url: str, contact_email: str) -> str:
    base = (public_url or "").rstrip("/")
    return f"""FIN-2016-A003 SCENARIO 3 CHECK — Nisaba LLC
═══════════════════════════════════════════

Primary
  FinCEN {FINCEN}
  {SCENARIO}
  https://www.fincen.gov/resources/advisories/fincen-advisory-fin-2016-a003

Typology (verbatim shape)
  Criminal emails Company C as a supplier: send future invoices to a new
  account number. Company C updates vendor payment master. Wires go to
  the criminal. That is Scenario 3.

Offer
  Free 72h REVIEW of one vendor bank-change / pay path: where Scenario 3
  can still complete without sealed out-of-band callback + dual approve.

Ask
  Reply REVIEW — no charge, no invoice, no obligation.
  Or deposit path: {base}/diligence

Links
  {base}/scenario-3
  {base}/scenario-3/one-pager.txt
  {base}/scenario-3/offer.json
  Stranger verify: https://velaru.xyz/verify

Contact
  {contact_email}

their_production: false
"""


def page_copy() -> dict[str, str]:
    return {
        "headline": "FIN-2016-A003 Scenario 3 Check",
        "sub": (
            "FinCEN already named the fraud: criminal impersonates a supplier, "
            "emails a new account number, you update the vendor master, the wire "
            "leaves. This REVIEW maps where that write can still complete without "
            "a stranger-verifiable Seal."
        ),
    }
