"""UAPA classification Seal — post-send RTP fraudulently-induced reporting receipt.

Distinct from pre-push FedNow/RTP Never. Mouth: was this transfer reportable
under TCH UAPA — and can a stranger verify the classification Seal?

Surfaces:
  GET  /uapa-seal
  GET  /uapa-seal/one-pager.txt
  GET  /uapa-seal/offer.json
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-uapa-seal-offer-v1"
DEPOSIT_LABEL = "$2,500"
REVIEW_BAND = "$5,000–$8,000"
DELIVERY = "72h"
TCH_PRIMARY = (
    "The Clearing House RTP Rules Interpretation — Fraud Reporting and Acting on Alerts "
    "(issued Oct 29, 2025; Operating Rule II.G)"
)
UAPA = "UAPA"
UAPA_EFF = "March 31, 2026"


def offer(public_url: str, contact_email: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "UAPA classification Seal",
        "firm": "Nisaba LLC",
        "primary": {
            "body": "The Clearing House",
            "instrument": TCH_PRIMARY,
            "code": UAPA,
            "effective": UAPA_EFF,
            "meaning": (
                "Fraudulently induced RTP-native payment — Sender induced under false "
                "pretenses (impersonation, social engineering, other deceptive tactics)"
            ),
        },
        "offer": (
            "Was this RTP-native transfer already reportable under TCH’s UAPA code — "
            "and can a stranger verify the classification receipt?"
        ),
        "direction": "post_send_classification",
        "not": [
            "Not pre-push Go/Never (that is the FedNow/RTP halt SKU — sibling)",
            "Not a TCH participant product or camt.056 gateway",
            "Not implementing network messaging on this SKU",
        ],
        "distinct_from": {
            "pre_push": f"{base}/diligence",
            "note": "FPC gap + pre-push Never ≠ UAPA post-send reporting Seal",
        },
        "price": {
            "deposit": DEPOSIT_LABEL,
            "review": REVIEW_BAND,
            "delivery": DELIVERY,
            "free_review": "Reply REVIEW — one RTP/FedNow path, 72h",
        },
        "deliverable": (
            "72h memo on one instant-pay path: where a fraudulently induced send "
            "can leave without a stranger-verifiable UAPA-class Seal (who decided "
            "FRAD vs UAPA vs neither, when, bound to which payment fingerprint)."
        ),
        "ask": "Reply REVIEW — no charge, no invoice, no obligation.",
        "urls": {
            "page": f"{base}/uapa-seal",
            "one_pager": f"{base}/uapa-seal/one-pager.txt",
            "offer": f"{base}/uapa-seal/offer.json",
            "diligence": f"{base}/diligence",
            "scenario_3": f"{base}/scenario-3",
            "verify": "https://velaru.xyz/verify",
        },
        "contact": contact_email,
        "their_production": False,
    }


def one_pager(public_url: str, contact_email: str) -> str:
    base = (public_url or "").rstrip("/")
    return f"""UAPA CLASSIFICATION SEAL — Nisaba LLC
════════════════════════════════════

Primary
  {TCH_PRIMARY}
  Reason code {UAPA} effective {UAPA_EFF}
  = fraudulently induced RTP-native payment (impersonation / social engineering)

Mouth
  Was this transfer already reportable under UAPA — and can a stranger
  verify the classification receipt?

Distinct from
  Pre-push FedNow/RTP Never (may the irrevocable send proceed?).
  UAPA is post-send taxonomy. This SKU Seals the classification, not the push.

Offer
  Free 72h REVIEW of one RTP/FedNow path: FRAD vs UAPA vs unclassified —
  who decided, when, bound to which payment fingerprint.

Ask
  Reply REVIEW — no charge, no invoice, no obligation.
  Or deposit: {base}/diligence

Links
  {base}/uapa-seal
  {base}/uapa-seal/one-pager.txt
  {base}/uapa-seal/offer.json
  Stranger verify: https://velaru.xyz/verify

Contact
  {contact_email}

their_production: false
"""


def page_copy() -> dict[str, str]:
    return {
        "headline": "Was this transfer already UAPA — and can a stranger Seal it?",
        "sub": (
            "TCH reason code UAPA (eff. Mar 31, 2026) labels fraudulently induced "
            "RTP-native payments after the send. This REVIEW maps where that "
            "classification can still go missing as a stranger-verifiable receipt — "
            "not the pre-push halt."
        ),
    }
