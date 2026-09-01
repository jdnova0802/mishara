"""Named may — permission is not bearer cash.

Satoshi: anyone who holds the key may spend. The secret is the owner.
Gate tickets minted as bearer inherit that shape — token = spend.

Named may: the secret is not enough. A public holder must stand on the
redeem, matching the holder named at issue. Bearer may is the bug on
irreversible civic writes (bind, payout, force). Cash can be bearer.
Permission cannot.

Default remains bearer so existing drills do not break.
A ticket becomes named when holder_id is present at issue,
or when GATE_NAMED_MAY=1 (every print must name a holder).
"""
from __future__ import annotations

import os
from typing import Any

SPEC = "gate-named-may-v1"
REASON_REQUIRED = "named_may_holder_required"
REASON_MISMATCH = "named_may_holder_mismatch"
REASON_BEARER_FORBIDDEN = "named_may_bearer_forbidden"

INVENTION = (
    "Named digital permission — consume-once may bound to a public holder, "
    "not a bearer secret. Satoshi inverse of UTXO."
)


def required() -> bool:
    return os.getenv("GATE_NAMED_MAY", "").strip().lower() in ("1", "true", "yes", "on")


def normalize_holder(raw) -> str | None:
    if raw is None:
        return None
    s = str(raw).strip()[:128]
    return s or None


def classify(*, holder_id: str | None) -> dict[str, Any]:
    hid = normalize_holder(holder_id)
    named = bool(hid)
    law_on = required()
    if law_on and not named:
        return {
            "ok": False,
            "named": False,
            "bearer": True,
            "reason": REASON_BEARER_FORBIDDEN,
            "holder_id": None,
        }
    return {
        "ok": True,
        "named": named,
        "bearer": not named,
        "reason": None,
        "holder_id": hid,
    }


def check(*, issued_holder: str | None, presented_holder: str | None) -> dict[str, Any]:
    """Fail closed if the ticket was named and redeem does not stand the same name."""
    issued = normalize_holder(issued_holder)
    presented = normalize_holder(presented_holder)
    if not issued:
        if required():
            return {
                "ok": False,
                "reason": REASON_BEARER_FORBIDDEN,
                "named": False,
            }
        return {"ok": True, "reason": None, "named": False, "bearer": True}
    if not presented:
        return {
            "ok": False,
            "reason": REASON_REQUIRED,
            "named": True,
            "bearer": False,
        }
    if issued != presented:
        return {
            "ok": False,
            "reason": REASON_MISMATCH,
            "named": True,
            "bearer": False,
        }
    return {
        "ok": True,
        "reason": None,
        "named": True,
        "bearer": False,
        "holder_id": issued,
    }


def spec(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Named may",
        "invention": INVENTION,
        "satoshi": "Bearer UTXO — the secret is the owner.",
        "heavier": (
            "Irreversible permission cannot be ownerless. Token without a "
            "standing name is Satoshi-shaped cash, not a throat."
        ),
        "required": required(),
        "missing": REASON_REQUIRED,
        "mismatch": REASON_MISMATCH,
        "bearer_forbidden": REASON_BEARER_FORBIDDEN,
        "default_bearer_until_named": True,
        "law": "GATE_NAMED_MAY=1 forbids bearer prints. Else named only when holder_id is issued.",
        "never_sell_may": True,
        "page": f"{base}/inventions",
        "their_production": False,
    }
