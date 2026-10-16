"""x402 v2 payment challenge builder for Gate paid routes."""
from __future__ import annotations

import base64
import hashlib
import json
import os
import uuid
from typing import Any

SPEC = "gate-x402-challenge-v1"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
NETWORK_BASE = "eip155:8453"
DEFAULT_AMOUNT_ATOMIC = "2000"  # $0.002 USDC (6 decimals)


# Settlement address only. GATE_X402_DEMO_PAYTO is ignored: production used it
# to keep a 402 alive against the null address 0x…00aa, which sends USDC nowhere.
_PAYTO_ENVS = (
    "GATE_X402_PAYTO",
    "GATE_X402_PAY_TO",
)


def settlement_address(raw: str | None) -> str | None:
    """EVM address that can receive a settlement. Null and short demo addresses are not one."""
    s = (raw or "").strip().strip('"').strip("'")
    if not (s.startswith("0x") and len(s) == 42):
        return None
    try:
        n = int(s[2:], 16)
    except ValueError:
        return None
    # 0x0, 0x…00aa, 0x…0001 and the other fixture burns sit under 2^16.
    if n < 0x10000:
        return None
    return s


def payto() -> str | None:
    for key in _PAYTO_ENVS:
        parsed = settlement_address(os.getenv(key))
        if parsed:
            return parsed
    return None


def payto_debug() -> dict:
    pt = payto()
    raw = ""
    source = None
    rejected = None
    for key in _PAYTO_ENVS:
        candidate = (os.getenv(key) or "").strip()
        if not candidate:
            continue
        raw = candidate
        source = key
        if settlement_address(candidate) is None:
            rejected = key
        break
    demo = (os.getenv("GATE_X402_DEMO_PAYTO") or "").strip()
    return {
        "configured": pt is not None,
        "env_set": bool(raw),
        "env_len": len(raw),
        "env_key": source,
        "valid_len": settlement_address(raw) is not None if raw else False,
        "placeholder_rejected": rejected is not None,
        "demo_env_ignored": bool(demo),
    }


def amount_atomic() -> str:
    raw = (os.getenv("GATE_X402_AMOUNT_ATOMIC") or DEFAULT_AMOUNT_ATOMIC).strip()
    return raw or DEFAULT_AMOUNT_ATOMIC


def payto_configured() -> bool:
    return payto() is not None


_PAYMENT_HEADER_KEYS = (
    "Payment-Signature",
    "PAYMENT-SIGNATURE",
    "X-Payment",
    "X-PAYMENT",
    "payment-signature",
    "x-payment",
)


def payment_header_value(headers) -> str | None:
    """First non-empty payment header value, or None."""
    if not headers:
        return None
    for key in _PAYMENT_HEADER_KEYS:
        raw = headers.get(key)
        if raw:
            return raw if isinstance(raw, str) else str(raw)
    # Werkzeug / CI may expose only lowercase keys via .get — scan items.
    try:
        for key, val in headers.items():
            if key and key.lower().replace("_", "-") in (
                "payment-signature",
                "x-payment",
            ):
                if val:
                    return val if isinstance(val, str) else str(val)
    except Exception:
        pass
    return None


def payment_header_present(headers) -> bool:
    """True if a payment header is present. Presence is NOT payment."""
    return payment_header_value(headers) is not None


def _addr_eq(a: str | None, b: str | None) -> bool:
    if not a or not b:
        return False
    return a.strip().lower() == b.strip().lower()


def _dev_unverified_escape() -> bool:
    accept_unverified = (os.getenv("GATE_X402_ACCEPT_UNVERIFIED") or "").strip() in (
        "1",
        "true",
        "TRUE",
        "yes",
    )
    dev = (os.getenv("GATE_DEV_MODE") or "").strip() in ("1", "true", "TRUE", "yes")
    return accept_unverified and dev


def _amount_asset_network_mismatch(buyer: dict, ours: dict) -> dict | None:
    """Compare a buyer-echoed requirements object against the server's own.

    payTo is checked by the caller (distinct reason). Here: the buyer must pay the
    exact required amount in the exact required asset on the exact required network."""
    out: dict[str, Any] = {}
    try:
        if int(str(buyer.get("amount"))) != int(str(ours.get("amount"))):
            out["amount"] = {"buyer": buyer.get("amount"), "required": ours.get("amount")}
    except (TypeError, ValueError):
        out["amount"] = {"buyer": buyer.get("amount"), "required": ours.get("amount")}
    if str(buyer.get("asset") or "").lower() != str(ours.get("asset") or "").lower():
        out["asset"] = {"buyer": buyer.get("asset"), "required": ours.get("asset")}
    if str(buyer.get("network") or "").lower() != str(ours.get("network") or "").lower():
        out["network"] = {"buyer": buyer.get("network"), "required": ours.get("network")}
    return out or None


def _payment_nonce(payload: dict) -> str | None:
    """Stable id for a payment authorization — basis for replay rejection.

    Keyed on the signed authorization (signature + authorization fields) so two
    different payments never collide, but a resubmission of the same one does."""
    try:
        inner = payload.get("payload") if isinstance(payload.get("payload"), dict) else {}
        signature = inner.get("signature") or payload.get("signature")
        authorization = (
            inner.get("authorization")
            if isinstance(inner.get("authorization"), dict)
            else payload.get("authorization")
        )
        basis: Any
        if signature or authorization:
            basis = {"signature": signature, "authorization": authorization}
        else:
            basis = payload
        canonical = json.dumps(basis, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    except Exception:
        return None


def payment_verified(
    headers,
    *,
    amount_atomic_override: str | None = None,
    asset: str | None = None,
    network: str | None = None,
    resource: str | None = None,
) -> dict:
    """Fail closed: a payment header alone never unlocks a paid route.

    Requires CDP facilitator verify + settle (CDP_API_KEY_ID/SECRET). The payment
    requirements (amount, asset, network, payTo) are built server-side from the
    route's own price — never taken from the buyer's payload — so a buyer cannot
    name their own price. A buyer-echoed `accepted` object is only checked for an
    exact match. Each payment payload is single-use (replay rejected).
    Dev-only escape: GATE_X402_ACCEPT_UNVERIFIED=1 AND GATE_DEV_MODE=1.
    """
    try:
        from gate import x402_facilitator as fac
    except ImportError:
        import x402_facilitator as fac

    raw = payment_header_value(headers)
    if not raw:
        return {
            "ok": False,
            "reason": "payment_header_missing",
            "paid": False,
        }

    payload = fac.decode_payment_header(raw)
    if not payload:
        # Forged / garbage header — still fail closed (never treat as paid).
        if _dev_unverified_escape():
            return {
                "ok": True,
                "reason": "dev_unverified_accepted",
                "paid": True,
                "note": "DEV ONLY — header accepted without facilitator verify.",
            }
        return {
            "ok": False,
            "reason": "payment_payload_invalid",
            "paid": False,
            "note": "PAYMENT-SIGNATURE did not decode to a JSON paymentPayload.",
        }

    if not fac.facilitator_ready():
        if _dev_unverified_escape():
            return {
                "ok": True,
                "reason": "dev_unverified_accepted",
                "paid": True,
                "note": "DEV ONLY — header accepted without facilitator verify.",
            }
        return {
            "ok": False,
            "reason": "facilitator_verify_required",
            "paid": False,
            "facilitator": fac.facilitator_debug(),
            "note": (
                "Payment header present but CDP facilitator credentials are not set. "
                "Set CDP_API_KEY_ID and CDP_API_KEY_SECRET (optional GATE_X402_FACILITATOR_URL)."
            ),
        }

    our_payto = payto()
    if not our_payto:
        return {
            "ok": False,
            "reason": "payto_unconfigured",
            "paid": False,
            "note": "GATE_X402_PAYTO not configured — cannot settle safely.",
        }

    # Server-authoritative requirements. The buyer never names the price.
    expected_amount = (amount_atomic_override or amount_atomic()).strip()
    reqs = fac.local_requirements(
        pay_to=our_payto,
        amount=expected_amount,
        asset=(asset or USDC_BASE),
        network=(network or NETWORK_BASE),
    )

    # If the buyer echoed a requirements object, it must match ours exactly.
    buyer_reqs = fac.payment_requirements_from_payload(payload)
    if buyer_reqs:
        if not _addr_eq(str(buyer_reqs.get("payTo") or ""), our_payto):
            return {
                "ok": False,
                "reason": "payto_mismatch",
                "paid": False,
                "note": "paymentRequirements.payTo does not match GATE_X402_PAYTO.",
            }
        mismatch = _amount_asset_network_mismatch(buyer_reqs, reqs)
        if mismatch:
            return {
                "ok": False,
                "reason": "requirements_mismatch",
                "paid": False,
                "mismatch": mismatch,
                "note": "Buyer-supplied amount/asset/network does not match the route price.",
            }

    # Replay: claim the payment-payload nonce before settling. Release on failure.
    nonce = _payment_nonce(payload)
    if nonce:
        try:
            from gate import db
        except ImportError:
            import db
        if not db.reserve_x402_payment(nonce=nonce, resource=resource or "", amount=expected_amount):
            return {
                "ok": False,
                "reason": "payment_replayed",
                "paid": False,
                "note": "This payment payload was already used.",
            }

    result = fac.verify_and_settle(payment_payload=payload, payment_requirements=reqs)
    if nonce:
        try:
            from gate import db
        except ImportError:
            import db
        if result.get("ok"):
            db.mark_x402_settled(nonce)
        else:
            db.release_x402_payment(nonce)
    result["facilitator"] = fac.facilitator_debug()
    return result


def _bazaar_info(*, method: str = "POST") -> dict:  # noqa: ARG001 — method reserved for GET wire routes
    return {
        "input": {
            "type": "http",
            "method": method,
            "bodyType": "json",
            "body": {
                "rail": "x402",
                "transfer": {
                    "amount": "0.002",
                    "currency": "USDC",
                    "counterparty": "0x0000000000000000000000000000000000000001",
                },
                "mandate": {"agent_id": "researcher-01", "max_amount": "1.00"},
            },
        },
        "schema": {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "rail": {"type": "string", "enum": ["x402", "rtp"]},
                "transfer": {"type": "object"},
                "mandate": {"type": "object"},
                "context": {"type": "object"},
            },
            "required": ["rail", "transfer"],
        },
    }


def challenge_payload(
    *,
    resource_url: str,
    description: str,
    amount_atomic_override: str | None = None,
    bazaar_method: str = "POST",
) -> dict[str, Any]:
    pt = payto()
    if not pt:
        raise RuntimeError("GATE_X402_PAYTO not configured")
    amt = (amount_atomic_override or amount_atomic()).strip()
    return {
        "x402Version": 2,
        "error": "Payment required",
        "resource": {
            "url": resource_url,
            "description": description,
            "mimeType": "application/json",
        },
        "accepts": [
            {
                "scheme": "exact",
                "network": NETWORK_BASE,
                "amount": amt,
                "asset": USDC_BASE,
                "payTo": pt,
                "maxTimeoutSeconds": 300,
                "extra": {"name": "USD Coin", "version": "2"},
            }
        ],
        "extensions": {"bazaar": {"info": _bazaar_info(method=bazaar_method)}},
    }


def payment_required_response(
    *,
    resource_url: str,
    description: str,
    amount_atomic_override: str | None = None,
    bazaar_method: str = "POST",
):
    from flask import jsonify

    payload = challenge_payload(
        resource_url=resource_url,
        description=description,
        amount_atomic_override=amount_atomic_override,
        bazaar_method=bazaar_method,
    )
    encoded = base64.b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8")).decode("ascii")
    return (
        jsonify(payload),
        402,
        {
            "Payment-Required": encoded,
            "X-Gate-X402": SPEC,
            "X-Request-Id": f"req_{uuid.uuid4().hex[:16]}",
        },
    )


def well_known_fanout(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    resources = [
        f"{base}/v1/prefinality/evaluate",
        f"{base}/api/x402/wire",
    ]
    out: dict[str, Any] = {"version": 1, "resources": resources}
    pt = payto()
    if pt:
        out["ownershipProofs"] = [pt]
    out["free_resources"] = [f"{base}/audit", f"{base}/api/x402/audit"]
    out["instructions"] = (
        "Free: GET /audit?url=... or /api/x402/audit?url=... — probe any x402 endpoint. "
        "Paid: GET /api/x402/wire?domain=...&email=... — $497 USDC deploy bundle. "
        "Prefinality: POST /v1/prefinality/evaluate or free demo /demo/prefinality/evaluate."
    )
    return out
