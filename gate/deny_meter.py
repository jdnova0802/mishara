"""DENY Meter v0 — DENY/Clear as unit of account (Nisaba / Gate invent).

Civilizational gap: markets price seats, tokens, YES-access.
Scarcity that holds civilization together is halt that holds.

NOT a sister company. On-card invent under Action OS / register fees.
Surfaces:
  GET /.well-known/deny-meter.json
  POST /demo/deny/quote
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-deny-meter-v0"
FIRM = "Nisaba LLC"
CARD = (
    "On-card invent. Prices proven DENY/CLEAR — not dashboard seats. "
    "Does not rename the firm. Pairs with register bps + CHARGE-only."
)

# Unit classes — what can be metered as scarce halt
UNITS = (
    "CLEAR_GO",  # proven may at T (still scarce — issued sparingly)
    "DENY_HOLD",  # halt that held — the primary commodity
    "PROTEST",  # formal dishonour instrument (see documentary_protest)
    "STRANGER_VERIFY",  # completed partial diplomatic verify events
)


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "firm": FIRM,
        "name": "DENY Meter",
        "version": "0",
        "card": CARD,
        "job": (
            "Treat proven DENY/CLEAR as the unit of account. "
            "Sell halt that holds — not narrative about governance."
        ),
        "thesis": (
            "SaaS sells YES (seats, tokens, access). "
            "Civilization needs priced NO that is stranger-checkable and irreversible-path-bound."
        ),
        "units": list(UNITS),
        "pricing_shapes": [
            {
                "shape": "per_deny_receipt",
                "meaning": "Fee when a DENY/HOLD receipt is issued and stranger-verifiable",
            },
            {
                "shape": "bps_on_cleared_flow",
                "meaning": "Existing register: 10 bps when Clear allows leave that completes",
            },
            {
                "shape": "protest_instrument",
                "meaning": "Fee for formal PROTEST when leave is dishonoured / Clear refuses",
            },
            {
                "shape": "verify_completion",
                "meaning": "Optional micro-fee or included: stranger completes issuer-incomplete verify",
            },
        ],
        "not_sold": [
            "Seat tiers as the scarcity story",
            "Soft-yes resurrection without CHARGE",
            "Governance PDF without a halt",
        ],
        "pairs_with": [
            "gate-diplomatics-v0",
            "gate-documentary-protest-v0",
            "gate-finality-compiler-v0",
            "gate-oracle-compiler-v0",
        ],
        "urls": {
            "well_known": f"{base}/.well-known/deny-meter.json",
            "demo_quote": f"{base}/demo/deny/quote",
            "register": f"{base}/register",
            "operator": f"{base}/operator",
        },
        "civilizational": True,
        "novelty_honest": (
            "Pricing access is ancient. Pricing stranger-proven DENY on irreversible "
            "leave as the primary commodity — underbuilt as product law."
        ),
    }


def quote(
    *,
    unit: str | None = None,
    notional_cents: int | None = None,
    bps: float = 10.0,
) -> dict[str, Any]:
    u = (unit or "DENY_HOLD").strip().upper()
    if u not in UNITS:
        u = "DENY_HOLD"
    notional = max(0, int(notional_cents or 0))
    bps_fee = int(round(notional * (bps / 10_000.0))) if notional else None
    flat = {
        "CLEAR_GO": 2500_00,  # aligns with diligence deposit scale (cents) as floor signal
        "DENY_HOLD": 1750_00,  # bind-room scale — halt pack
        "PROTEST": 7500_00,  # refusal SKU adjacency
        "STRANGER_VERIFY": 0,
    }
    return {
        "spec": SPEC,
        "firm": FIRM,
        "unit": u,
        "flat_cents_indicative": flat.get(u),
        "bps": bps,
        "notional_cents": notional or None,
        "bps_fee_cents": bps_fee,
        "note": (
            "Indicative invent quote — production fees live on /register and hustle SKUs. "
            "DENY Meter names the unit; commerce SSOT still owns checkout."
        ),
        "card_note": "Not a sister co. Halt is the commodity.",
    }
