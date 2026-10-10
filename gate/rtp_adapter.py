"""RTP / FedNow adapter — gate before PSP payment_order create.

Modern Treasury and similar PSPs expose instant credit as `type: rtp`; the bank
routes FedNow vs RTP internally. This adapter verifies a Gate pre-finality receipt
matches the outbound payment instruction before you call the PSP API.
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

    Fail closed. A live money rail refuses:
      - any receipt that does not verify or is not GO,
      - demo/dogfood receipts (signed, but never actionable),
      - a receipt whose jti was already used (single-use; replay rejected)."""
    fp = payment_order_fingerprint(payment_order if isinstance(payment_order, dict) else {})
    verified = prefinality_mod.verify_receipt_jwt(receipt_jwt, expected_fingerprint=fp)
    decision = verified.get("decision")
    valid = bool(verified.get("valid"))
    is_demo = bool(verified.get("demo"))
    reason = verified.get("reason")

    allow = valid and decision == "GO" and not is_demo
    if valid and is_demo:
        reason = "demo_receipt_refused"

    if allow:
        jti = verified.get("jti")
        try:
            from gate import db
        except ImportError:
            import db
        if not db.consume_receipt(jti=jti, rail="rtp", fingerprint=fp):
            allow = False
            reason = "receipt_already_used"

    if allow:
        message = "Receipt valid and GO — safe to create payment_order with type=rtp."
    elif is_demo:
        message = "Do not create payment_order — this is a demo receipt and cannot action a live rail."
    elif reason == "receipt_already_used":
        message = "Do not create payment_order — this receipt was already used (single-use)."
    else:
        message = "Do not create payment_order — receipt missing, invalid, or not GO."

    return {
        "spec": SPEC,
        "allow": allow,
        "halt": not allow,
        "decision": decision,
        "valid_receipt": valid,
        "demo": is_demo,
        "reason": reason,
        "fingerprint": fp,
        "payment_type_expected": "rtp",
        "message": message,
    }


def spec(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "hook": "before_payment_order_create",
        "psp_examples": ["Modern Treasury", "Column"],
        "payment_type": "rtp",
        "fednow_note": "PSP selects FedNow vs RTP; Gate fingerprints the instruction, not the network.",
        "evaluate": f"{base}/v1/prefinality/evaluate",
        "verify": f"{base}/v1/prefinality/verify",
        "manifest": f"{base}/.well-known/prefinality.json",
    }
