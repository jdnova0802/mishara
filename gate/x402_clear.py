"""Paid agent-spend Clear — high-ticket x402 SKU for Payments & finance.

Agents already concentrate spend in payments/finance (Paddock ~36% share).
Prefinality at dust ($0.002) does not match willingness-to-pay for irreversible
commit clearance. This mouth is the same GO/NO_GO + signed receipt, priced for
machine settlement without a human conversation.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import prefinality as prefinality_mod
except ImportError:
    import prefinality as prefinality_mod

SPEC = "gate-x402-clear-v1"
CLEAR_PRICE_USD = "97.00"
CLEAR_AMOUNT_ATOMIC = "97000000"  # $97 USDC, 6 decimals


def clear_price_label() -> str:
    return f"${CLEAR_PRICE_USD}"


def clear_amount_atomic() -> str:
    return CLEAR_AMOUNT_ATOMIC


def clear_receipt(
    *,
    body: dict,
    public_url: str,
) -> dict[str, Any]:
    """Run prefinality evaluate and stamp as paid Clear SKU."""
    payload = dict(body) if isinstance(body, dict) else {}
    if not (payload.get("rail") or "").strip():
        payload["rail"] = "x402"
    result = prefinality_mod.evaluate(payload, public_url=public_url)
    out: dict[str, Any] = {
        "spec": SPEC,
        "paid": True,
        "price_usd": CLEAR_PRICE_USD,
        "sku": "agent_spend_clear",
        "decision": result.get("decision"),
        "halt": result.get("halt"),
        "receipt": result.get("receipt"),
        "transfer_fingerprint": result.get("transfer_fingerprint")
        or result.get("fingerprint"),
        "rail": result.get("rail") or payload.get("rail"),
        "claim_scope": result.get("claim_scope"),
        "reasons": result.get("reasons") or result.get("reason_codes"),
        "evaluation_id": result.get("evaluation_id"),
        "note": (
            "Machine Clear before irreversible agent spend. Signed receipt bound to "
            "transfer fingerprint. No email, no account — USDC settle unlocks."
        ),
        "verify": f"{public_url.rstrip('/')}/.well-known/prefinality.json",
        "catalog": f"{public_url.rstrip('/')}/.well-known/x402.json",
    }
    for key in ("expires_at", "key_id", "write_state", "policy", "created_at"):
        if key in result:
            out[key] = result[key]
    return out
