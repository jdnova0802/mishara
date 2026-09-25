"""x402 v2 payment challenge builder for Gate paid routes."""
from __future__ import annotations

import base64
import json
import os
import uuid
from typing import Any

SPEC = "gate-x402-challenge-v1"
USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
NETWORK_BASE = "eip155:8453"
DEFAULT_AMOUNT_ATOMIC = "2000"  # $0.002 USDC (6 decimals)


_PAYTO_ENVS = (
    "GATE_X402_PAYTO",
    "GATE_X402_PAY_TO",
    "GATE_X402_DEMO_PAYTO",  # production currently has this name; crawlers still need a 402
)


def payto() -> str | None:
    for key in _PAYTO_ENVS:
        raw = (os.getenv(key) or "").strip().strip('"').strip("'")
        if raw.startswith("0x") and len(raw) == 42:
            return raw
    return None


def payto_debug() -> dict:
    pt = payto()
    raw = ""
    source = None
    for key in _PAYTO_ENVS:
        candidate = (os.getenv(key) or "").strip()
        if candidate:
            raw = candidate
            source = key
            break
    return {
        "configured": pt is not None,
        "env_set": bool(raw),
        "env_len": len(raw),
        "env_key": source,
        "valid_len": len(raw.strip('"').strip("'")) == 42 if raw else False,
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


def payment_verified(headers, *, amount_atomic_override: str | None = None) -> dict:
    """Fail closed: a payment header alone never unlocks a paid route.

    Requires CDP facilitator verify + settle (CDP_API_KEY_ID/SECRET).
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
        accept_unverified = (os.getenv("GATE_X402_ACCEPT_UNVERIFIED") or "").strip() in (
            "1",
            "true",
            "TRUE",
            "yes",
        )
        dev = (os.getenv("GATE_DEV_MODE") or "").strip() in ("1", "true", "TRUE", "yes")
        if accept_unverified and dev:
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
        accept_unverified = (os.getenv("GATE_X402_ACCEPT_UNVERIFIED") or "").strip() in (
            "1",
            "true",
            "TRUE",
            "yes",
        )
        dev = (os.getenv("GATE_DEV_MODE") or "").strip() in ("1", "true", "TRUE", "yes")
        if accept_unverified and dev:
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
    reqs = fac.payment_requirements_from_payload(payload)
    if not reqs:
        # Reconstruct from Gate challenge defaults when buyer omitted accepted.
        if not our_payto:
            return {
                "ok": False,
                "reason": "payto_unconfigured",
                "paid": False,
            }
        amt = (amount_atomic_override or amount_atomic()).strip()
        reqs = fac.local_requirements(
            pay_to=our_payto,
            amount=amt,
            asset=USDC_BASE,
            network=NETWORK_BASE,
        )

    # Merchant-side fail-closed: only settle payments aimed at our payTo.
    if our_payto and not _addr_eq(str(reqs.get("payTo") or ""), our_payto):
        return {
            "ok": False,
            "reason": "payto_mismatch",
            "paid": False,
            "note": "paymentRequirements.payTo does not match GATE_X402_PAYTO.",
        }

    result = fac.verify_and_settle(payment_payload=payload, payment_requirements=reqs)
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
