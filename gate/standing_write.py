"""Standing write — monthly lease on write-stop remaining true.

Reply-path only after Bind yes. Not cold. Not book/desk/Operator/Conformant.
Same officer pack + stranger-openable receipt, reissued current each month.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-standing-write-v1"
PRICE_LABEL = "$4,500/mo"
PRICE_CENTS = 450_000
PAYEE = "Nisaba LLC"
CONTACT = "hello@velaru.xyz"

# Objection only — deploy if asked "why not just re-buy Bind next year"
REBUY_BIND_OBJECTION = (
    "Bind is the first proof. Standing is the same pack kept current for the "
    "renewal ask — a receipt from last March does not answer this March's question."
)

WHY_MONTHLY = (
    "A credit that recurs annually needs evidence that recurs annually."
)

WHY_MONTHLY_BODY = [
    "Underwriters re-ask at renewal; credits and conditions are re-earned, not granted once.",
    "Carriers stopped taking self-attestation in 2026 — they want dated evidence, and dated evidence goes stale.",
    "SOC 2 / ISO rarely buy a fixed rate credit; they show up as better terms, lower retentions, fewer conditions.",
    "Mid-market retentions often run near $100k. Evidence that shifts conditions on that is worth more than the lease.",
]

WHAT_ARRIVES_MONTHLY = (
    "The receipt is reissued current each month. If nothing changed, you still get "
    "a dated current receipt for this month's ask — not a silent 'trust us.'"
)

ASK = "reply STANDING and I'll send the monthly invoice."
HALT = "we will not sell may. We will not implement the rail on this SKU."

WHAT_IT_IS = (
    "Monthly lease on write-stop remaining true. Same officer pack and "
    "stranger-openable receipt as Bind Room — reissued current each month. "
    "Not implementation. Not a retainer for work. Not a new product."
)

WHEN_OFFERED = (
    "In-thread, after a Bind yes, only when the underwriter will ask again at renewal. "
    "Never cold outbound. A forwarded page must still read clean to a GC who was not on the thread."
)

THEIR_PROBLEM = (
    "Carriers stopped taking self-attestation in 2026 — they want dated evidence, "
    "and dated evidence goes stale."
)


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Standing write",
        "price": PRICE_LABEL,
        "cents": PRICE_CENTS,
        "interval": "month",
        "payee": PAYEE,
        "contact": CONTACT,
        "what": WHAT_IT_IS,
        "their_problem": THEIR_PROBLEM,
        "why_monthly": WHY_MONTHLY,
        "why_monthly_body": WHY_MONTHLY_BODY,
        "what_arrives_monthly": WHAT_ARRIVES_MONTHLY,
        "rebuy_bind_objection": REBUY_BIND_OBJECTION,
        "when_offered": WHEN_OFFERED,
        "ask": ASK,
        "halt": HALT,
        "not": [
            "not may",
            "not rail implementation on this SKU",
            "not Standing book / desk",
            "not Operator",
            "not Conformant",
            "not cold outbound",
        ],
        "links": {
            "page": f"{base}/standing",
            "bind_room": f"{base}/bind-room",
            "officer_pack": f"{base}/bind-room/officer-pack.json",
            "verify": "https://velaru.xyz/verify",
        },
    }


def reply_email(*, prior_subject: str = "Bind Room") -> dict[str, str]:
    """Paste-ready reply after Bind yes. Objection line lives in §2 only."""
    subject = f"Re: {prior_subject} — Standing write"
    body = f"""Underwriters re-ask at renewal, and credits and conditions are re-earned rather than granted once. Carriers stopped taking self-attestation in 2026 — they want dated evidence, and dated evidence goes stale.

Standing write keeps the receipt current for that ask. Same officer pack, same verify, reissued monthly — {PRICE_LABEL}.

{WHY_MONTHLY}

https://gate.velaru.xyz/standing
https://gate.velaru.xyz/bind-room/officer-pack.json
https://velaru.xyz/verify

Ask: {ASK}
Halt: {HALT}

Demond Davis
Nisaba LLC
{CONTACT}
"""
    return {"subject": subject, "body": body.strip() + "\n"}
