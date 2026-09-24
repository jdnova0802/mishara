"""CPPA ADMT decision-notice Seal — CA coming-compliance Diligence (Jan 1, 2027).

Primary: 11 CCR § 7200(b) (Article 11). Unstayed Tier 1 future bet.

Surfaces:
  GET  /admt
  GET  /admt/one-pager.txt
  GET  /admt/offer.json
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-cppa-admt-offer-v1"
DEPOSIT_LABEL = "$2,500"
REVIEW_BAND = "$5,000–$8,000"
DELIVERY = "72h"
CLOCK = "January 1, 2027"
PIN = "11 CCR § 7200(b) (Article 11 — Automated Decisionmaking Technology)"


def offer(public_url: str, contact_email: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "CPPA ADMT decision-notice Seal",
        "firm": "Nisaba LLC",
        "primary": {
            "pin": PIN,
            "clock": CLOCK,
            "package": "https://www.cppa.ca.gov/regulations/ccpa_updates.html",
            "approved_text": (
                "https://www.cppa.ca.gov/regulations/pdf/"
                "ccpa_updates_cyber_risk_admt_appr_text.pdf"
            ),
        },
        "offer": (
            "Before / when ADMT makes a significant decision — can a stranger verify "
            "pre-use notice + access/opt-out path as a Seal? Coming-compliance map "
            f"ahead of {CLOCK}."
        ),
        "tier": "1",
        "not": [
            "Not § 7120 (that is Article 9 cybersecurity audits)",
            "Not Colorado SB 26-189 (stayed / contested — do not conflate)",
            "Not implementing privacy ops software on this SKU",
        ],
        "price": {
            "deposit": DEPOSIT_LABEL,
            "review": REVIEW_BAND,
            "delivery": DELIVERY,
            "free_review": f"Reply REVIEW — one significant-decision path, 72h (ahead of {CLOCK})",
        },
        "deliverable": (
            f"72h memo on one ADMT significant-decision path: where notice / access / "
            f"opt-out can still miss a stranger-verifiable Seal before {CLOCK} compliance."
        ),
        "ask": "Reply REVIEW — no charge, no invoice, no obligation.",
        "urls": {
            "page": f"{base}/admt",
            "one_pager": f"{base}/admt/one-pager.txt",
            "offer": f"{base}/admt/offer.json",
            "diligence": f"{base}/diligence",
            "verify": "https://velaru.xyz/verify",
        },
        "contact": contact_email,
        "their_production": False,
    }


def one_pager(public_url: str, contact_email: str) -> str:
    base = (public_url or "").rstrip("/")
    return f"""CPPA ADMT DECISION-NOTICE SEAL — Nisaba LLC
═══════════════════════════════════════════

Primary
  {PIN}
  Compliance clock: {CLOCK}
  https://www.cppa.ca.gov/regulations/ccpa_updates.html

Mouth
  Before / when ADMT makes a significant decision (lend / house / educate /
  employ / compensate / healthcare) — can a stranger verify pre-use notice
  + access / opt-out as a Seal?

Offer
  Free 72h REVIEW of one significant-decision path — coming-compliance map
  ahead of {CLOCK}. Not legal advice. Public regs only.

Do not conflate
  Not 11 CCR § 7120 (cybersecurity audits).
  Not Colorado SB 26-189 (enforcement stayed — separate).

Ask
  Reply REVIEW — no charge, no invoice, no obligation.
  Or deposit: {base}/diligence

Links
  {base}/admt
  {base}/admt/one-pager.txt
  {base}/admt/offer.json
  Stranger verify: https://velaru.xyz/verify

Contact
  {contact_email}

their_production: false
"""


def page_copy() -> dict[str, str]:
    return {
        "headline": "ADMT significant decision — Seal before Jan 1, 2027",
        "sub": (
            "California 11 CCR § 7200(b) (Article 11). Coming-compliance Diligence: "
            "one significant-decision path where pre-use notice + access/opt-out "
            "can still miss a stranger-verifiable Seal. Unstayed clock."
        ),
    }
