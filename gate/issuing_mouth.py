"""Stripe Issuing auth mouth — Gate Clear on every agent card authorization.

Vault stays at Stripe. Gate only AUTHORIZE / DECLINE + stranger-verifiable receipt.
Realtime webhook must answer in <2s (Stripe issuing_authorization.request timeout).
"""
from __future__ import annotations

import os
import time
from typing import Any, Callable

SPEC = "gate-issuing-mouth-v1"
RAIL = "issuing"


def issuing_enabled() -> bool:
    return os.getenv("GATE_ISSUING_ENABLED", "").strip().lower() in ("1", "true", "yes", "on")


def webhook_secret() -> str:
    return (
        os.getenv("STRIPE_ISSUING_WEBHOOK_SECRET")
        or os.getenv("STRIPE_WEBHOOK_SECRET")
        or ""
    ).strip()


def config() -> dict[str, Any]:
    secret_key = bool((os.getenv("STRIPE_SECRET_KEY") or "").strip())
    enabled = issuing_enabled()
    wh = bool(webhook_secret())
    return {
        "spec": SPEC,
        "rail": RAIL,
        "issuing_enabled": enabled,
        "stripe_secret_configured": secret_key,
        "webhook_secret_configured": wh,
        "money_real": bool(enabled and secret_key),
        "gate_holds_funds": False,
        "auth_timeout_seconds": 2,
        "plain": (
            "Apply Issuing for agents (own business) in Stripe Dashboard, "
            "set GATE_ISSUING_ENABLED=1, point issuing_authorization.request "
            "at POST /v1/issuing/authorization. Dogfood works without approval."
        ),
    }


def _cents_to_amount(cents: Any) -> str:
    try:
        n = int(cents)
    except (TypeError, ValueError):
        return "0"
    return f"{n / 100:.2f}"


def authorization_to_evaluate_body(auth: dict) -> dict[str, Any]:
    """Map Stripe Issuing Authorization object → prefinality evaluate body."""
    auth = auth if isinstance(auth, dict) else {}
    merchant = auth.get("merchant_data") if isinstance(auth.get("merchant_data"), dict) else {}
    card = auth.get("card") if isinstance(auth.get("card"), dict) else {}
    meta = card.get("metadata") if isinstance(card.get("metadata"), dict) else {}

    merchant_name = (merchant.get("name") or "").strip()
    network_id = (merchant.get("network_id") or merchant.get("category_code") or "").strip()
    counterparty = merchant_name or network_id or "unknown_merchant"

    agent_id = (
        (meta.get("agent_id") or meta.get("gate_agent_id") or auth.get("agent_id") or "")
        .strip()
        or None
    )
    max_amount = (meta.get("max_amount") or meta.get("mandate_max") or "").strip() or None
    expected = (meta.get("expected_merchant") or meta.get("allowed_merchant") or "").strip() or None
    daily_cap = (meta.get("daily_cap") or "").strip() or None
    review_ceiling = (meta.get("review_ceiling") or "").strip() or None

    mandate: dict[str, Any] = {}
    if agent_id:
        mandate["agent_id"] = agent_id
    if max_amount:
        mandate["max_amount"] = max_amount
    if expected:
        mandate["expected_counterparty"] = expected
    if daily_cap:
        mandate["daily_cap"] = daily_cap
    if review_ceiling:
        mandate["review_ceiling"] = review_ceiling

    currency = (auth.get("currency") or "usd").strip().upper()
    if currency == "USD":
        currency = "USD"

    return {
        "rail": RAIL,
        "transfer": {
            "amount": _cents_to_amount(auth.get("amount")),
            "currency": currency or "USD",
            "counterparty": counterparty,
            "merchant_category": (merchant.get("category") or merchant.get("category_code") or ""),
            "authorization_id": auth.get("id"),
        },
        "mandate": mandate,
        "context": {
            "stripe_authorization_id": auth.get("id"),
            "card_id": card.get("id"),
            "merchant_city": merchant.get("city"),
            "merchant_country": merchant.get("country"),
            "network_risk_score": auth.get("network_risk_score"),
        },
        "ttl_seconds": 120,
    }


def decide(
    auth: dict,
    *,
    evaluate_fn: Callable[[dict], dict],
) -> dict[str, Any]:
    """Run Gate Clear on an Issuing authorization. Fail closed on HOLD/NO_GO/errors."""
    t0 = time.perf_counter()
    body = authorization_to_evaluate_body(auth)
    try:
        result = evaluate_fn(body)
    except Exception as exc:  # noqa: BLE001 — mouth must never throw into Stripe timeout
        result = {
            "spec": "gate-prefinality-v1",
            "decision": "NO_GO",
            "halt": True,
            "signals": ["mouth_exception"],
            "reason": type(exc).__name__,
            "message": "Issuing mouth failed closed.",
        }

    decision = (result.get("decision") or "NO_GO").upper()
    approved = decision == "GO"
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    return {
        "spec": SPEC,
        "approved": approved,
        "stripe_response": {"approved": approved},
        "decision": decision,
        "halt": not approved,
        "gate": {
            "evaluation_id": result.get("evaluation_id") or result.get("restraint_id"),
            "verify_url": result.get("verify_url"),
            "receipt": result.get("receipt"),
            "signals": result.get("signals") or [],
            "fingerprint": result.get("fingerprint"),
            "message": result.get("message"),
        },
        "rail": RAIL,
        "authorization_id": (auth.get("id") if isinstance(auth, dict) else None),
        "agent_id": body.get("mandate", {}).get("agent_id"),
        "elapsed_ms": elapsed_ms,
        "within_stripe_timeout": elapsed_ms < 2000,
        "money_real": config()["money_real"],
        "gate_holds_funds": False,
        "write_executed": False,
    }


def dogfood_authorization(
    *,
    amount_cents: int = 2500,
    merchant: str = "Acme Supplies",
    agent_id: str = "dogfood_agent",
    max_amount: str = "50.00",
    expected_merchant: str | None = None,
    force_breach: bool = False,
) -> dict[str, Any]:
    """Synthetic Issuing Authorization for live dogfood without Stripe Issuing approval."""
    if force_breach:
        amount_cents = 9_999_00  # exceeds default max
    meta = {
        "agent_id": agent_id,
        "max_amount": max_amount,
    }
    if expected_merchant:
        meta["expected_merchant"] = expected_merchant
    return {
        "id": "iauth_dogfood_sim",
        "object": "issuing.authorization",
        "amount": int(amount_cents),
        "currency": "usd",
        "merchant_data": {
            "name": merchant if not force_breach else "Rogue Merchant LLC",
            "category_code": "5045",
            "city": "San Francisco",
            "country": "US",
            "network_id": "1234567890",
        },
        "card": {
            "id": "ic_dogfood",
            "metadata": meta,
        },
        "network_risk_score": 12,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    cfg = config()
    return {
        "spec": SPEC,
        "name": "Gate Issuing auth mouth",
        "description": (
            "Real-time AUTHORIZE/DECLINE for Stripe Issuing agent cards. "
            "Every auth hits Gate Clear; declines mint stranger-verifiable receipts. "
            "Gate never holds card float."
        ),
        "config": cfg,
        "webhook": {
            "url": f"{base}/v1/issuing/authorization",
            "events": ["issuing_authorization.request"],
            "response": {"approved": "boolean — true only on Gate GO"},
            "timeout_note": "Stripe waits ~2 seconds; mouth fail-closes on HOLD/NO_GO/error",
        },
        "dogfood": f"{base}/demo/issuing/mouth",
        "page": f"{base}/issuing-mouth",
        "evaluate_rail": RAIL,
        "primary_docs": "https://docs.stripe.com/issuing/agents",
        "apply": "Stripe Dashboard → Issuing for agents → Cards for your own business",
        "their_production": False,
    }
