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


def payto() -> str | None:
    raw = (os.getenv("GATE_X402_PAYTO") or os.getenv("GATE_X402_PAY_TO") or "").strip()
    if raw.startswith("0x") and len(raw) == 42:
        return raw
    return None


def amount_atomic() -> str:
    raw = (os.getenv("GATE_X402_AMOUNT_ATOMIC") or DEFAULT_AMOUNT_ATOMIC).strip()
    return raw or DEFAULT_AMOUNT_ATOMIC


def payto_configured() -> bool:
    return payto() is not None


def payment_header_present(headers) -> bool:
    if not headers:
        return False
    for key in (
        "Payment-Signature",
        "PAYMENT-SIGNATURE",
        "X-Payment",
        "X-PAYMENT",
        "payment-signature",
    ):
        if headers.get(key):
            return True
    return False


def _bazaar_info(*, method: str = "POST") -> dict:
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


def challenge_payload(*, resource_url: str, description: str) -> dict[str, Any]:
    pt = payto()
    if not pt:
        raise RuntimeError("GATE_X402_PAYTO not configured")
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
                "amount": amount_atomic(),
                "asset": USDC_BASE,
                "payTo": pt,
                "maxTimeoutSeconds": 300,
                "extra": {"name": "USD Coin", "version": "2"},
            }
        ],
        "extensions": {"bazaar": {"info": _bazaar_info()}},
    }


def payment_required_response(*, resource_url: str, description: str):
    from flask import jsonify

    payload = challenge_payload(resource_url=resource_url, description=description)
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
        f"{base}/demo/prefinality/evaluate",
        f"{base}/mcp",
    ]
    out: dict[str, Any] = {"version": 1, "resources": resources}
    pt = payto()
    if pt:
        out["ownershipProofs"] = [pt]
    out["instructions"] = (
        "Prefinality clearance before irreversible commit. "
        "Paid evaluate via x402 USDC on Base when GATE_X402_PAYTO is configured; "
        "free demo at /demo/prefinality/evaluate."
    )
    return out
