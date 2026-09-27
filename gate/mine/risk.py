"""HF / liquidation-candidate risk passport — empty Bazaar niche Gate owns.

Agents pay for the passport. YOUR liquidator mine uses the same scoring.
Double print: meter revenue + liquidation bonuses.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-mine-risk-passport-v1"
PRICE_USD = "0.05"
AMOUNT_ATOMIC = "50000"  # $0.05 USDC


def price_label() -> str:
    return f"${PRICE_USD}"


def amount_atomic() -> str:
    return AMOUNT_ATOMIC


def passport(
    *,
    collateral_usd: float,
    debt_usd: float,
    liquidation_threshold: float = 0.825,
) -> dict[str, Any]:
    """Deterministic HF passport from provided balances (no chain RPC required)."""
    coll = max(0.0, float(collateral_usd))
    debt = max(0.0, float(debt_usd))
    lt = float(liquidation_threshold)
    if debt <= 0:
        hf = 999.0
        status = "NO_DEBT"
    else:
        hf = (coll * lt) / debt
        if hf < 1.0:
            status = "LIQUIDATABLE"
        elif hf < 1.05:
            status = "CRITICAL"
        elif hf < 1.25:
            status = "ELEVATED"
        else:
            status = "HEALTHY"

    bonus_est = max(0.0, debt * 0.05) if status == "LIQUIDATABLE" else 0.0

    return {
        "spec": SPEC,
        "paid_sku": "hf_risk_passport",
        "price_usd": PRICE_USD,
        "collateral_usd": round(coll, 2),
        "debt_usd": round(debt, 2),
        "liquidation_threshold": lt,
        "health_factor": round(hf, 6),
        "status": status,
        "liquidatable": status == "LIQUIDATABLE",
        "est_liquidation_bonus_usd": round(bonus_est, 2),
        "mine_hook": (
            "If LIQUIDATABLE: run liquidation mine with Gate Clear on seize notional. "
            "Protocol pays the bonus — this passport is the ore detector."
        ),
    }
