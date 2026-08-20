"""DvP Mouth — PFMI P12: permission leg and spend leg settle together or not at all.

Delivery versus payment: one leg cannot finalise alone. Gate maps permission
(LIVE parent · ticket · exclusive door) to delivery (bind/payout act) and
refuses split settlement — ALLOW without fuse LIVE is payment without delivery;
PAS 200 without mouth is delivery without payment.

Not cliche token DvP. Operational DvP on the welded write.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-dvp-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def link(
    *,
    permission_live: bool | None = None,
    spend_acted: bool | None = None,
    decision: str | None = None,
) -> dict[str, Any]:
    live = bool(permission_live)
    acted = bool(spend_acted)
    d = (decision or "").upper()
    if acted and not live:
        posture = "payment_without_delivery"
        claim = "spend_without_permission_live"
    elif live and not acted and d == "ALLOW":
        posture = "delivery_without_payment"
        claim = "permission_without_mouth_act_yet"
    elif acted and live and d == "ALLOW":
        posture = "dvp_linked"
        claim = "both_legs_finalised_together"
    elif d in ("HALT", "BLOCK"):
        posture = "dvp_aborted"
        claim = "neither_leg_settles"
    else:
        posture = "unevaluated"
        claim = "insufficient_leg_data"
    return {
        "spec": SPEC,
        "name": "DvP Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": ["PFMI Principle 12 — DvP eliminates principal risk", "Gate married write — one door"],
        "permission_live": live,
        "spend_acted": acted,
        "decision": d or None,
        "posture": posture,
        "claim": claim,
        "thesis": "Split settlement is how principal risk returns. The mouth links the legs.",
        "gatekeep": "Proprietary DvP mouth. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "DvP Mouth",
        "inventor": INVENTOR,
        "example_linked": link(permission_live=True, spend_acted=True, decision="ALLOW"),
        "example_split": link(permission_live=False, spend_acted=True, decision="ALLOW"),
        "live": f"{base}/.well-known/dvp-mouth.json",
        "fulfillment": f"{base}/.well-known/fulfillment.json",
        "their_production": False,
    }
