"""RTP / FedNow adapter — gate before PSP payment_order create.

Modern Treasury and similar PSPs expose instant credit as `type: rtp`; the bank
routes FedNow vs RTP internally. This adapter verifies a Gate pre-finality receipt
matches the outbound payment instruction before you call the PSP API.

GO receipts are redeemed (jti consumed) here. Network failure after allow means
the caller must re-evaluate for a new jti — replay of the same receipt is rejected.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import prefinality as prefinality_mod
except ImportError:
    import prefinality as prefinality_mod

SPEC = "gate-rtp-adapter-v1"


def payment_order_fingerprint(order: dict) -> str:
    """Build fingerprint from a Modern-Treasury-shaped payment order."""
    transfer: dict[str, Any] = {
        "amount": _cents_to_decimal(order.get("amount")),
        "currency": (order.get("currency") or "USD").upper(),
    }
    # Accept both nested receiving_account and flat MT-style fields used in tests.
    recv = order.get("receiving_account") if isinstance(order.get("receiving_account"), dict) else {}
    if recv.get("id"):
        transfer["external_account_id"] = str(recv["id"])
    rd = recv.get("routing_details") if isinstance(recv.get("routing_details"), list) else []
    if rd and isinstance(rd[0], dict):
        transfer["routing_number"] = rd[0].get("routing_number")
        transfer["account_number"] = rd[0].get("account_number")
    elif order.get("routing_number") and order.get("account_number"):
        transfer["routing_number"] = order.get("routing_number")
        transfer["account_number"] = order.get("account_number")
    return prefinality_mod.transfer_fingerprint(rail="rtp", transfer=transfer)


def _cents_to_decimal(amount) -> str | None:
    if amount is None:
        return None
    try:
        cents = int(amount)
    except (TypeError, ValueError):
        return str(amount)
    return f"{cents / 100:.2f}"


def gate_payment_order(*, receipt_jwt: str, payment_order: dict) -> dict:
    """Return allow/deny for an outbound RTP-shaped payment order.

    Consumes the GO jti on first successful allow. Replay → allow=False.
    """
    order = payment_order if isinstance(payment_order, dict) else {}
    fp = payment_order_fingerprint(order)
    # Commit path: always consume. Retries after success need a fresh evaluate.
    verified = prefinality_mod.redeem_receipt_jwt(
        receipt_jwt, expected_fingerprint=fp
    )
    decision = verified.get("decision")
    allow = bool(verified.get("valid") and decision == "GO")
    return {
        "spec": SPEC,
        "allow": allow,
        "halt": not allow,
        "decision": decision,
        "valid_receipt": bool(verified.get("valid")),
        "redeemed": bool(verified.get("redeemed")),
        "reason": verified.get("reason"),
        "fingerprint": fp,
        "payment_type_expected": "rtp",
        "receipt_one_shot": True,
        "message": (
            "Receipt valid, GO, and jti redeemed — safe to create payment_order with type=rtp."
            if allow
            else (
                "Do not create payment_order — receipt missing, invalid, not GO, "
                "or already redeemed (re-evaluate for a new jti)."
            )
        ),
    }


def spec(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "hook": "before_payment_order_create",
        "psp_examples": ["Modern Treasury", "Column"],
        "payment_type": "rtp",
        "fednow_note": "PSP selects FedNow vs RTP; Gate fingerprints the instruction, not the network.",
        "receipt_one_shot": True,
        "evaluate": f"{base}/v1/prefinality/evaluate",
        "verify": f"{base}/v1/prefinality/verify",
        "manifest": f"{base}/.well-known/prefinality.json",
    }
