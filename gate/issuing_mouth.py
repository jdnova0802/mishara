"""Stripe Issuing auth mouth — Gate Clear on every agent card authorization.

Vault stays at Stripe. Gate only AUTHORIZE / DECLINE + stranger-verifiable receipt.
Realtime webhook must answer in <2s (Stripe issuing_authorization.request timeout).

Two layers (card workflow-lock hunt):
  1. Platform MCC floor — Stripe spending_controls.allowed_categories / blocked_*
     (do not rebuild; Stripe may decline before this webhook fires).
  2. Gate workflow lock — card metadata allowed_categories / job_id / expected_merchant
     checked here with claim_scope. MCC ≠ cart contents (IIAS/Fleet lesson).
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Callable

SPEC = "gate-issuing-mouth-v1"
RAIL = "issuing"
WORKFLOW_SPEC = "gate-issuing-workflow-lock-v1"


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
        "layers": {
            "platform_mcc_floor": (
                "Stripe Issuing spending_controls.allowed_categories / "
                "blocked_categories — hard MCC at Stripe; do not rebuild in Gate."
            ),
            "gate_workflow_lock": (
                "Card metadata allowed_categories + mandate fields enforced here "
                "with claim_scope. Narrower than (or equal to) the Stripe floor."
            ),
            "not_sku_grade": (
                "MCC/category lock is not cart/SKU proof. FSA IIAS / Visa Fleet "
                "product codes are deeper; Gate cannot invent merchant line-items."
            ),
        },
        "plain": (
            "Apply Issuing for agents (own business) in Stripe Dashboard, "
            "set GATE_ISSUING_ENABLED=1, point issuing_authorization.request "
            "at POST /v1/issuing/authorization. Set Stripe spending_controls as MCC "
            "floor; set card metadata allowed_categories for Gate workflow lock. "
            "Dogfood works without approval."
        ),
    }


def _cents_to_amount(cents: Any) -> str:
    try:
        n = int(cents)
    except (TypeError, ValueError):
        return "0"
    return f"{n / 100:.2f}"


def _parse_category_list(raw: Any) -> list[str]:
    """Normalize metadata / spending_controls category lists to lowercase strings."""
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(x).strip().lower() for x in raw if str(x).strip()]
    if isinstance(raw, str):
        s = raw.strip()
        if not s:
            return []
        if s.startswith("["):
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(x).strip().lower() for x in parsed if str(x).strip()]
            except json.JSONDecodeError:
                pass
        return [p.strip().lower() for p in s.split(",") if p.strip()]
    return []


def card_meta(auth: dict) -> dict[str, Any]:
    auth = auth if isinstance(auth, dict) else {}
    card = auth.get("card") if isinstance(auth.get("card"), dict) else {}
    meta = card.get("metadata") if isinstance(card.get("metadata"), dict) else {}
    return meta


def platform_allowed_categories(auth: dict) -> list[str]:
    """Stripe spending_controls on the card object (floor — informational for Gate)."""
    auth = auth if isinstance(auth, dict) else {}
    card = auth.get("card") if isinstance(auth.get("card"), dict) else {}
    sc = card.get("spending_controls") if isinstance(card.get("spending_controls"), dict) else {}
    return _parse_category_list(sc.get("allowed_categories"))


def workflow_allowed_categories(auth: dict) -> list[str]:
    """Gate workflow allowlist from card metadata (enforced in this mouth)."""
    meta = card_meta(auth)
    for key in ("allowed_categories", "gate_allowed_categories", "workflow_categories"):
        got = _parse_category_list(meta.get(key))
        if got:
            return got
    return []


def observed_merchant_category(auth: dict) -> str:
    auth = auth if isinstance(auth, dict) else {}
    merchant = auth.get("merchant_data") if isinstance(auth.get("merchant_data"), dict) else {}
    return (
        (merchant.get("category") or merchant.get("category_code") or "")
        .strip()
        .lower()
    )


def workflow_category_check(auth: dict) -> dict[str, Any]:
    """Fail closed when metadata allowlist is set and auth category is outside it.

    If no Gate allowlist is configured, returns configured=False (Clear still runs).
    Stripe spending_controls are reported but not re-enforced here.
    """
    allowed = workflow_allowed_categories(auth)
    observed = observed_merchant_category(auth)
    platform = platform_allowed_categories(auth)
    out: dict[str, Any] = {
        "spec": WORKFLOW_SPEC,
        "configured": bool(allowed),
        "allowed_categories": allowed,
        "observed_category": observed or None,
        "platform_allowed_categories": platform,
        "ok": True,
        "signal": None,
        "plain": (
            "No Gate workflow category allowlist on card metadata — "
            "Clear runs without category workflow lock."
            if not allowed
            else "Auth merchant category is inside Gate workflow allowlist."
        ),
    }
    if not allowed:
        return out
    if not observed:
        out["ok"] = False
        out["signal"] = "workflow_category_missing"
        out["plain"] = (
            "Card has allowed_categories but auth has no merchant category — fail closed."
        )
        return out
    if observed not in allowed:
        out["ok"] = False
        out["signal"] = "workflow_category_denied"
        out["plain"] = (
            f"Merchant category '{observed}' not in Gate workflow allowlist "
            f"{allowed}. MCC floor may also exist on Stripe spending_controls; "
            "this refusal is the workflow layer (claim_scope), not a rebuilt MCC engine."
        )
        return out
    return out


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
    job_id = (meta.get("job_id") or meta.get("gate_job_id") or "").strip() or None
    allowed_cats = workflow_allowed_categories(auth)

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
    if job_id:
        mandate["job_id"] = job_id
    if allowed_cats:
        mandate["allowed_categories"] = allowed_cats

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
            "workflow_lock": WORKFLOW_SPEC,
            "platform_allowed_categories": platform_allowed_categories(auth),
        },
        "ttl_seconds": 120,
    }


def _workflow_denied_result(check: dict[str, Any], body: dict[str, Any]) -> dict[str, Any]:
    """Prefinality-shaped NO_GO for workflow category miss — with claim_scope."""
    try:
        try:
            from gate import claim_scope as claim_scope_mod
        except ImportError:
            import claim_scope as claim_scope_mod

        counterparty = (body.get("transfer") or {}).get("counterparty") or "unknown_merchant"
        scope = claim_scope_mod.build(
            boundary="gate_issuing_workflow_category_lock",
            logs=[
                "issuing.card.metadata.allowed_categories",
                "issuing.authorization.merchant_data.category",
            ],
            plain=(
                "NO_GO checked only against this card's Gate workflow category allowlist "
                "vs the auth merchant category — not Stripe spending_controls MCC floor, "
                "not cart/SKU contents (MCC ≠ cart; IIAS/Fleet deeper)."
            ),
            time_window={
                "kind": "authorization_request",
                "from": None,
                "to": None,
            },
            counterparties=[counterparty],
            keys_checked={
                "allowed_categories": check.get("allowed_categories"),
                "observed_category": check.get("observed_category"),
                "signal": check.get("signal"),
            },
            extra={
                "platform_allowed_categories": check.get("platform_allowed_categories"),
                "mcc_is_not_cart": True,
                "cite": (
                    "IRS Notice 2006-69 IIAS / Visa Fleet product codes — MCC alone is weak"
                ),
            },
        )
        return claim_scope_mod.attach(
            {
                "spec": "gate-prefinality-v1",
                "decision": "NO_GO",
                "halt": True,
                "signals": [check.get("signal") or "workflow_category_denied"],
                "reason": check.get("signal") or "workflow_category_denied",
                "message": check.get("plain"),
                "workflow_lock": check,
                "rail": RAIL,
            },
            scope=scope,
            force=True,
        )
    except Exception:
        return {
            "spec": "gate-prefinality-v1",
            "decision": "NO_GO",
            "halt": True,
            "signals": [check.get("signal") or "workflow_category_denied"],
            "reason": check.get("signal") or "workflow_category_denied",
            "message": check.get("plain"),
            "workflow_lock": check,
        }


def decide(
    auth: dict,
    *,
    evaluate_fn: Callable[[dict], dict],
) -> dict[str, Any]:
    """Run workflow category lock then Gate Clear. Fail closed on HOLD/NO_GO/errors."""
    t0 = time.perf_counter()
    body = authorization_to_evaluate_body(auth)
    check = workflow_category_check(auth)

    if check.get("configured") and not check.get("ok"):
        result = _workflow_denied_result(check, body)
    else:
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
        if isinstance(result, dict) and check.get("configured"):
            result = dict(result)
            result["workflow_lock"] = check

    decision = (result.get("decision") or "NO_GO").upper()
    approved = decision == "GO"
    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    return {
        "spec": SPEC,
        "approved": approved,
        "stripe_response": {"approved": approved},
        "decision": decision,
        "halt": not approved,
        "workflow_lock": check,
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
                "workflow_lock": check.get("signal") if check.get("configured") else None,
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
    merchant_category: str = "computer_software_stores",
    category_code: str = "5734",
    allowed_categories: list[str] | str | None = None,
    platform_allowed_categories: list[str] | None = None,
    job_id: str | None = None,
    force_breach: bool = False,
) -> dict[str, Any]:
    """Synthetic Issuing Authorization for live dogfood without Stripe Issuing approval."""
    if force_breach:
        amount_cents = 9_999_00  # exceeds default max
    meta: dict[str, Any] = {
        "agent_id": agent_id,
        "max_amount": max_amount,
    }
    if expected_merchant:
        meta["expected_merchant"] = expected_merchant
    if job_id:
        meta["job_id"] = job_id
    if allowed_categories is not None:
        if isinstance(allowed_categories, list):
            meta["allowed_categories"] = ",".join(allowed_categories)
        else:
            meta["allowed_categories"] = str(allowed_categories)
    card: dict[str, Any] = {
        "id": "ic_dogfood",
        "metadata": meta,
    }
    if platform_allowed_categories is not None:
        card["spending_controls"] = {
            "allowed_categories": list(platform_allowed_categories),
            "blocked_categories": None,
        }
    return {
        "id": "iauth_dogfood_sim",
        "object": "issuing.authorization",
        "amount": int(amount_cents),
        "currency": "usd",
        "merchant_data": {
            "name": merchant if not force_breach else "Rogue Merchant LLC",
            "category": merchant_category,
            "category_code": category_code,
            "city": "San Francisco",
            "country": "US",
            "network_id": "1234567890",
        },
        "card": card,
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
        next_steps = [
            "One tiny real auth — Gate mouth should AUTHORIZE/DECLINE <2s",
            "Optional: Stripe spending_controls = MCC floor; metadata allowed_categories = Gate workflow lock",
        ]

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
            "Stripe spending_controls = MCC floor; Gate metadata allowed_categories = "
            "workflow lock with claim_scope. Every auth hits Gate Clear; declines mint "
            "stranger-verifiable receipts. Gate never holds card float."
        ),
        "config": cfg,
        "workflow_lock": {
            "spec": WORKFLOW_SPEC,
            "metadata_keys": [
                "allowed_categories",
                "gate_allowed_categories",
                "workflow_categories",
                "job_id",
                "expected_merchant",
            ],
            "how": (
                "Set card metadata allowed_categories to a comma-list of Stripe "
                "merchant category strings (e.g. automated_fuel_dispensers). "
                "Auth outside that list → NO_GO with claim_scope before Clear."
            ),
            "platform_floor_docs": "https://docs.stripe.com/issuing/controls/spending-controls",
            "why_not_mcc_only": (
                "MCC ≠ cart. Cite: IRS Notice 2006-69 (IIAS); Visa Fleet 2.0 product codes."
            ),
        },
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
