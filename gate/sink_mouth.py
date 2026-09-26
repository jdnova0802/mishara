"""OCT / Fast Funds sink mouth — Gate Clear before money lands on the card.

World: Visa pays the *receiving* issuer when funds are pushed TO the card
(Original Credit $0.29 · Fast Funds $0.60 — Visa USA IRF PDF).
Gate never moves money. Gate only GO / NEVER + stranger-verifiable receipt
before the program accepts an inbound push as intentional.

Dogfood works without a live Visa Direct BIN. Real money needs sponsor
OCT Fast Funds receive enrollment (Column / bank — typically 90–120 days).
"""
from __future__ import annotations

import os
from typing import Any, Callable

SPEC = "gate-sink-mouth-v1"
RAIL = "oct"

# Verbatim from Visa USA Interchange Reimbursement Fees (public PDF).
# https://usa.visa.com/dam/VCOM/download/merchants/visa-usa-interchange-reimbursement-fees.pdf
VISA_PRIMARY = (
    "https://usa.visa.com/dam/VCOM/download/merchants/visa-usa-interchange-reimbursement-fees.pdf"
)
RECEIVE_FEES_USD = {
    "original_credit": 0.29,
    "fast_funds": 0.60,
    "money_transfer_oct": 0.10,
    "money_transfer_deferred": 0.015,
}
# CPS/Account Funding, Debit — issuer of card being drained (exempt-style rows).
AFT_EXEMPT_DEBIT = {"ad_valorem": 0.0175, "fixed": 0.20, "label": "1.75% + $0.20"}


def sink_enabled() -> bool:
    return os.getenv("GATE_SINK_ENABLED", "").strip().lower() in ("1", "true", "yes", "on")


def config() -> dict[str, Any]:
    enabled = sink_enabled()
    return {
        "spec": SPEC,
        "rail": RAIL,
        "sink_enabled": enabled,
        "money_real": False,  # real OCT receive requires bank Fast Funds — not Stripe self-serve tonight
        "gate_holds_funds": False,
        "visa_primary": VISA_PRIMARY,
        "receive_fees_usd": RECEIVE_FEES_USD,
        "aft_exempt_debit": AFT_EXEMPT_DEBIT,
        "plain": (
            "Dogfood inbound OCT Clear now. Real receive fees need a BIN with "
            "Visa Money Transfer Fast Funds enrolled — RFQ Column/sponsor "
            "(typically 90–120 days). Stripe Issuing auth mouth stays separate."
        ),
    }


def _cents_to_amount(cents: Any) -> str:
    try:
        n = int(cents)
    except (TypeError, ValueError):
        return "0"
    return f"{n / 100:.2f}"


def push_to_evaluate_body(push: dict) -> dict[str, Any]:
    """Map inbound OCT / Fast Funds push → prefinality evaluate body."""
    push = push if isinstance(push, dict) else {}
    meta = push.get("metadata") if isinstance(push.get("metadata"), dict) else {}

    sender = (
        (push.get("sender_name") or push.get("originator") or push.get("bai") or "")
        .strip()
        or "unknown_sender"
    )
    agent_id = (meta.get("agent_id") or push.get("agent_id") or "").strip() or None
    max_amount = (meta.get("max_amount") or meta.get("mandate_max") or "").strip() or None
    expected = (
        meta.get("expected_sender") or meta.get("allowed_sender") or meta.get("expected_counterparty") or ""
    ).strip() or None
    review_ceiling = (meta.get("review_ceiling") or "").strip() or None
    daily_cap = (meta.get("daily_cap") or "").strip() or None

    program = (push.get("program") or push.get("fee_program") or "fast_funds").strip().lower()
    if program not in RECEIVE_FEES_USD:
        program = "fast_funds"
    receive_fee = RECEIVE_FEES_USD[program]

    mandate: dict[str, Any] = {"intent": "accept_inbound_oct"}
    if agent_id:
        mandate["agent_id"] = agent_id
    if max_amount:
        mandate["max_amount"] = max_amount
    if expected:
        mandate["expected_counterparty"] = expected
    if review_ceiling:
        mandate["review_ceiling"] = review_ceiling
    if daily_cap:
        mandate["daily_cap"] = daily_cap

    currency = (push.get("currency") or "usd").strip().upper()
    if currency == "USD":
        currency = "USD"

    amount = push.get("amount")
    if amount is None and push.get("amount_cents") is not None:
        amount = _cents_to_amount(push.get("amount_cents"))
    elif isinstance(amount, (int, float)) and amount >= 100 and push.get("amount_cents") is None:
        # treat large ints without decimal as cents only when amount_cents key used; else dollars as string
        amount = str(amount)

    return {
        "rail": RAIL,
        "transfer": {
            "amount": str(amount) if amount is not None else "0",
            "currency": currency or "USD",
            "counterparty": sender,
            "authorization_id": push.get("id") or push.get("transaction_id"),
            "fee_program": program,
            "receive_fee_usd": receive_fee,
        },
        "mandate": mandate,
        "context": {
            "direction": "inbound_oct",
            "bai": push.get("bai"),
            "card_id": push.get("card_id"),
            "program": program,
            "receive_fee_usd": receive_fee,
            "visa_primary": VISA_PRIMARY,
        },
        "ttl_seconds": 120,
    }


def decide(
    push: dict,
    *,
    evaluate_fn: Callable[[dict], dict],
) -> dict[str, Any]:
    """Run Gate Clear on an inbound OCT. Fail closed on HOLD/NO_GO/errors."""
    body = push_to_evaluate_body(push)
    try:
        result = evaluate_fn(body)
    except Exception as exc:  # noqa: BLE001
        result = {
            "spec": "gate-prefinality-v1",
            "decision": "NO_GO",
            "halt": True,
            "signals": ["mouth_exception"],
            "reason": type(exc).__name__,
            "message": "Sink mouth failed closed.",
        }

    decision = (result.get("decision") or "NO_GO").upper()
    accepted = decision == "GO"
    program = body["transfer"].get("fee_program") or "fast_funds"
    receive_fee = RECEIVE_FEES_USD.get(program, RECEIVE_FEES_USD["fast_funds"])

    return {
        "spec": SPEC,
        "accepted": accepted,
        "decision": decision,
        "halt": not accepted,
        "receive": {
            "fee_program": program,
            "receive_fee_usd": receive_fee if accepted else 0.0,
            "note": (
                "Fee accrues to receiving issuer per Visa IRF only when BIN is "
                "enrolled and money actually settles — Gate does not collect it."
            ),
        },
        "gate": {
            "evaluation_id": result.get("evaluation_id") or result.get("restraint_id"),
            "verify_url": result.get("verify_url"),
            "receipt": result.get("receipt"),
            "signals": result.get("signals") or [],
            "fingerprint": result.get("fingerprint"),
            "message": result.get("message"),
        },
        "rail": RAIL,
        "push_id": (push.get("id") if isinstance(push, dict) else None),
        "agent_id": body.get("mandate", {}).get("agent_id"),
        "money_real": False,
        "gate_holds_funds": False,
        "visa_primary": VISA_PRIMARY,
    }


def dogfood_push(
    *,
    amount: str = "125.00",
    sender: str = "ADP Wisely Now",
    agent_id: str = "dogfood_sink",
    max_amount: str = "500.00",
    expected_sender: str | None = None,
    program: str = "fast_funds",
    force_breach: bool = False,
) -> dict[str, Any]:
    """Synthetic inbound OCT for live dogfood without Visa Direct."""
    if force_breach:
        amount = "9999.00"
        sender = "Rogue Disburser LLC"
    meta = {
        "agent_id": agent_id,
        "max_amount": max_amount,
    }
    if expected_sender:
        meta["expected_sender"] = expected_sender
    elif not force_breach:
        meta["expected_sender"] = sender
    return {
        "id": "oct_dogfood_sim",
        "object": "original_credit",
        "amount": amount,
        "currency": "usd",
        "sender_name": sender,
        "bai": "PD",
        "program": program if program in RECEIVE_FEES_USD else "fast_funds",
        "card_id": "ic_sink_dogfood",
        "metadata": meta,
    }


def aft_illustration(*, load_amount: float = 100.0) -> dict[str, Any]:
    """Issuer-side AFT Ix when *this* card funds an external wallet (illustration)."""
    ix = load_amount * AFT_EXEMPT_DEBIT["ad_valorem"] + AFT_EXEMPT_DEBIT["fixed"]
    return {
        "direction": "outbound_aft_from_our_card",
        "load_amount_usd": load_amount,
        "schedule": AFT_EXEMPT_DEBIT["label"],
        "issuer_interchange_usd": round(ix, 4),
        "visa_primary": VISA_PRIMARY,
        "note": (
            "Issuer of the card being drained receives CPS/Account Funding rates. "
            "If YOU are the wallet loading via AFT, you are on the cost side."
        ),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    cfg = config()
    return {
        "spec": SPEC,
        "name": "Gate OCT sink mouth",
        "description": (
            "Clearance before accepting inbound Visa Original Credit / Fast Funds "
            "onto an agent card. Receiving issuer fee schedule cited from Visa IRF PDF. "
            "Gate never holds float; Gate never collects network fees."
        ),
        "config": cfg,
        "economics": {
            "receive_fees_usd": RECEIVE_FEES_USD,
            "aft_exempt_debit": AFT_EXEMPT_DEBIT,
            "visa_primary": VISA_PRIMARY,
            "massive_context": (
                "Visa Direct processed >12.5B transactions FY2025 (Visa). "
                "You only earn receive fees on pushes that land on YOUR BIN."
            ),
        },
        "webhook": {
            "url": f"{base}/v1/sink/oct",
            "events": ["original_credit.inbound", "fast_funds.inbound"],
            "response": {"accepted": "boolean — true only on Gate GO"},
            "note": "Sponsor/processor wires inbound OCT here; dogfood uses POST /demo/sink/mouth",
        },
        "dogfood": f"{base}/demo/sink/mouth",
        "aft_demo": f"{base}/demo/sink/aft",
        "page": f"{base}/sink-mouth",
        "evaluate_rail": RAIL,
        "near_term": "Stripe Issuing auth mouth (spend Clear/Never) stays separate and live-dogfoodable.",
        "long_term": "RFQ Column/sponsor for OCT Fast Funds receive — typically 90–120 days.",
        "their_production": False,
    }
