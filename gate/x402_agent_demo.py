"""Agent payment demo — autonomous attempt → Gate evaluate → receipt.

Demonstrates the x402 / pre-finality gap close: an agent proposes an irreversible
USDC transfer; Gate fail-closes or clears and issues a stranger-verifiable receipt.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
import uuid
from typing import Any


def agent_intent(
    *,
    agent_id: str,
    amount_usdc: str,
    destination: str,
    memo: str,
) -> dict[str, Any]:
    return {
        "agent_id": agent_id,
        "rail": "x402",
        "transfer": {
            "amount": amount_usdc,
            "currency": "USDC",
            "network": "eip155:8453",
            "destination": destination,
            "memo": memo,
        },
        "mandate": {
            "agent_id": agent_id,
            "max_amount": "1.00",
            "purpose": "autonomous_payment_demo",
        },
    }


def evaluate_intent(intent: dict[str, Any], *, payto_configured: bool) -> dict[str, Any]:
    """Fail-closed evaluation of an agent payment attempt."""
    transfer = intent.get("transfer") or {}
    mandate = intent.get("mandate") or {}
    amount = str(transfer.get("amount") or "0")
    dest = str(transfer.get("destination") or "")
    max_amount = str(mandate.get("max_amount") or "0")
    reasons: list[str] = []
    try:
        amt_f = float(amount)
        max_f = float(max_amount)
    except ValueError:
        amt_f, max_f = 0.0, 0.0
        reasons.append("amount_unparseable")
    if amt_f <= 0:
        reasons.append("amount_nonpositive")
    if max_f > 0 and amt_f > max_f:
        reasons.append("amount_over_mandate_cap")
    if not dest.startswith("0x") or len(dest) != 42:
        reasons.append("destination_not_address")
    if not payto_configured:
        reasons.append("x402_payto_unconfigured")

    decision = "NO_GO" if reasons else "GO"
    fingerprint = hashlib.sha256(
        json.dumps(intent, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    receipt_id = f"rcpt_x402_{uuid.uuid4().hex[:16]}"
    return {
        "decision": decision,
        "reasons": reasons,
        "intent": intent,
        "fingerprint": fingerprint,
        "receipt_id": receipt_id,
        "issued_at": int(time.time()),
        "x402_payto_configured": payto_configured,
        "note": (
            "Cleared — agent may present payment proof against Gate x402 challenge."
            if decision == "GO"
            else "Fail-closed — autonomous payment halted before wallet sign."
        ),
    }


def demo_payto_active() -> bool:
    return (os.getenv("GATE_X402_DEMO") or "").strip() in {"1", "true", "yes"}
