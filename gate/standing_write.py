"""Standing write — monthly lease on write-stop remaining true.

Reply-path only after Bind yes. Not cold. Not book/desk/Operator/Conformant.
Same officer pack + stranger-openable receipt, kept current.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-standing-write-v1"
PRICE_LABEL = "$4,500/mo"
PRICE_CENTS = 450_000
PAYEE = "Nisaba LLC"
CONTACT = "hello@velaru.xyz"

# Objection: "why not just re-buy Bind next year"
REBUY_BIND_OBJECTION = (
    "Bind is the first proof. Standing is the same pack kept current for the "
    "renewal ask — a receipt from last March does not answer this March's question."
)

WHY_MONTHLY = (
    "A credit that recurs annually needs evidence that recurs annually."
)

WHY_MONTHLY_BODY = [
    "Carriers credit documented controls (MFA, stacked controls) at renewal — not once forever.",
    "Self-attestation is giving way to exports and third-party verification.",
    "SOC 2 / ISO rarely buy a fixed rate credit; they show up as better terms, lower retentions, fewer conditions.",
    "Mid-market retentions often run near $100k. Evidence that shifts conditions on that is worth more than the lease.",
]

ASK = "reply STANDING and I'll send the monthly invoice."
HALT = "we will not sell may. We will not implement the rail on this SKU."

WHAT_IT_IS = (
    "Monthly lease on write-stop remaining true. Same officer pack and "
    "stranger-openable receipt as Bind Room — kept current. Not implementation. "
    "Not a retainer for work. Not a new product."
)

WHEN_OFFERED = (
    "In-thread, after a Bind yes, only when the underwriter will ask again at renewal. "
    "Never cold. Never a second sermon."
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
        "why_monthly": WHY_MONTHLY,
        "why_monthly_body": WHY_MONTHLY_BODY,
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
    """Paste-ready reply after Bind yes."""
    subject = f"Re: {prior_subject} — Standing write"
    body = f"""Underwriters re-ask at renewal. Credits and conditions are re-earned, not granted once.

Bind Room is the first stranger-openable receipt. Standing write keeps that evidence current — same officer pack, same verify, every month — {PRICE_LABEL}.

{WHY_MONTHLY}

{REBUY_BIND_OBJECTION}

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
