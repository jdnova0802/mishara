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
            "claim_scope": result.get("claim_scope"),
            "signed_claim": result.get("signed_claim"),
        },
        "claim_scope": result.get("claim_scope"),
        "signed_claim": result.get("signed_claim"),
        "write_state": result.get("write_state")
        or {
            "spec": "gate-write-state-v1",
            "phase": "CLEARANCE",
            "cancellable": True if approved else None,
            "never_during_this_phase": (
                "NO_GO here is clearance refusal before Stripe auth. "
                "APPROVED from this mouth is not capture/settlement — Stripe auth stays "
                "pending until capture; Gate does not collapse that into final."
            ),
            "plain": (
                "Issuing mouth is clearance only. Stripe authorization after approve is "
                "IN_FLIGHT on the card network until capture/expiry — Gate write_executed=false."
            ),
            "detail": {
                "write_executed": False,
                "stripe_auth_after_approve": "PENDING_CAPTURE_OR_EXPIRY",
                "already_handled_clearance": True,
                "gap_closed": "explicit_pending_vs_settled",
            },
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


def readiness(*, stripe_mod: Any | None = None) -> dict[str, Any]:
    """Ops checklist: mouth on + float available + card exists → spendable.

    Does not expose PAN/CVC. Gate never holds funds — reads Stripe Issuing balance only.
    """
    cfg = config()
    steps: dict[str, Any] = {
        "mouth_enabled": bool(cfg["issuing_enabled"]),
        "webhook_secret": bool(cfg["webhook_secret_configured"]),
        "stripe_secret": bool(cfg["stripe_secret_configured"]),
        "issuing_available_cents": None,
        "issuing_currency": None,
        "cardholders": None,
        "cards": None,
        "cards_active": None,
        "pending_issuing_topups": None,
        "stripe_error": None,
    }
    next_steps: list[str] = []

    if not steps["mouth_enabled"]:
        next_steps.append("set GATE_ISSUING_ENABLED=1 on Render")
    if not steps["webhook_secret"]:
        next_steps.append("set STRIPE_ISSUING_WEBHOOK_SECRET (issuing_authorization.request)")
    if not steps["stripe_secret"]:
        next_steps.append("set STRIPE_SECRET_KEY")
        return {
            "spec": "gate-issuing-readiness-v1",
            "rail": RAIL,
            "config": cfg,
            "steps": steps,
            "spendable": False,
            "next": next_steps,
            "gate_holds_funds": False,
        }

    try:
        import stripe as _stripe

        stripe_lib = stripe_mod or _stripe
        bal = stripe_lib.Balance.retrieve()
        issuing = bal.get("issuing") if isinstance(bal, dict) else getattr(bal, "issuing", None)
        available = []
        if isinstance(issuing, dict):
            available = issuing.get("available") or []
        elif issuing is not None:
            available = getattr(issuing, "available", None) or []
        cents = 0
        currency = "usd"
        if available:
            row = available[0]
            if isinstance(row, dict):
                cents = int(row.get("amount") or 0)
                currency = (row.get("currency") or "usd").lower()
            else:
                cents = int(getattr(row, "amount", 0) or 0)
                currency = (getattr(row, "currency", None) or "usd").lower()
        steps["issuing_available_cents"] = cents
        steps["issuing_currency"] = currency

        ch = stripe_lib.issuing.Cardholder.list(limit=100)
        cards = stripe_lib.issuing.Card.list(limit=100)
        ch_data = ch.get("data") if isinstance(ch, dict) else getattr(ch, "data", []) or []
        card_data = cards.get("data") if isinstance(cards, dict) else getattr(cards, "data", []) or []
        steps["cardholders"] = len(ch_data)
        steps["cards"] = len(card_data)
        active = 0
        for c in card_data:
            status = c.get("status") if isinstance(c, dict) else getattr(c, "status", None)
            if status == "active":
                active += 1
        steps["cards_active"] = active

        try:
            tops = stripe_lib.Topup.list(limit=20)
            top_data = tops.get("data") if isinstance(tops, dict) else getattr(tops, "data", []) or []
            pending = 0
            for t in top_data:
                status = t.get("status") if isinstance(t, dict) else getattr(t, "status", None)
                dest = (
                    t.get("destination_balance")
                    if isinstance(t, dict)
                    else getattr(t, "destination_balance", None)
                )
                if status == "pending" and (dest == "issuing" or dest is None):
                    # destination_balance may be absent on older topups; count pending anyway if amount>0
                    pending += 1
            steps["pending_issuing_topups"] = pending
        except Exception:
            steps["pending_issuing_topups"] = None
    except Exception as exc:
        steps["stripe_error"] = type(exc).__name__
        next_steps.append(f"Stripe read failed: {type(exc).__name__}")

    if steps["issuing_available_cents"] is not None and steps["issuing_available_cents"] <= 0:
        next_steps.append("Add funds to Issuing balance (Dashboard → Issuing → Add funds)")
    if steps["cardholders"] == 0:
        next_steps.append("Create a cardholder")
    if (steps["cards_active"] or 0) == 0:
        next_steps.append("Create an active virtual card")

    spendable = bool(
        steps["mouth_enabled"]
        and steps["webhook_secret"]
        and steps["stripe_secret"]
        and (steps["issuing_available_cents"] or 0) > 0
        and (steps["cards_active"] or 0) > 0
        and not steps["stripe_error"]
    )
    if spendable:
        next_steps = ["One tiny real auth — Gate mouth should AUTHORIZE/DECLINE <2s"]

    return {
        "spec": "gate-issuing-readiness-v1",
        "rail": RAIL,
        "config": cfg,
        "steps": steps,
        "spendable": spendable,
        "next": next_steps,
        "gate_holds_funds": False,
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
        "ops_readiness": f"{base}/ops/issuing-status",
        "evaluate_rail": RAIL,
        "primary_docs": "https://docs.stripe.com/issuing/agents",
        "apply": "Stripe Dashboard → Issuing for agents → Cards for your own business",
        "their_production": False,
    }
