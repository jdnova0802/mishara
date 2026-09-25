"""CDP x402 facilitator client — JWT auth, verify, settle.

Fails closed. Header presence is never payment. A paid route unlocks only when
POST /verify returns isValid and POST /settle returns success.
"""
from __future__ import annotations

import base64
import json
import os
import secrets
import time
from typing import Any
from urllib.parse import urlparse

import requests

DEFAULT_FACILITATOR_BASE = "https://api.cdp.coinbase.com/platform/v2/x402"
DEFAULT_TIMEOUT_SECONDS = 20


def facilitator_base_url() -> str:
    raw = (os.getenv("GATE_X402_FACILITATOR_URL") or "").strip().rstrip("/")
    if raw:
        return raw
    return DEFAULT_FACILITATOR_BASE


def cdp_credentials() -> tuple[str | None, str | None]:
    key_id = (os.getenv("CDP_API_KEY_ID") or os.getenv("GATE_CDP_API_KEY_ID") or "").strip()
    secret = (
        os.getenv("CDP_API_KEY_SECRET") or os.getenv("GATE_CDP_API_KEY_SECRET") or ""
    ).strip()
    return (key_id or None, secret or None)


def facilitator_ready() -> bool:
    """True when verify/settle can be attempted (URL + CDP credentials)."""
    key_id, secret = cdp_credentials()
    return bool(key_id and secret)


def facilitator_debug() -> dict[str, Any]:
    key_id, secret = cdp_credentials()
    return {
        "ready": bool(key_id and secret),
        "url": facilitator_base_url(),
        "cdp_key_configured": bool(key_id),
        "cdp_secret_configured": bool(secret),
    }


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _parse_cdp_private_key(key_data: str):
    """Parse CDP API key secret: PEM EC (ES256) or base64 Ed25519 (EdDSA)."""
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec, ed25519

    if "\\n" in key_data:
        key_data = key_data.replace("\\n", "\n")

    try:
        key = serialization.load_pem_private_key(key_data.encode("utf-8"), password=None)
        if isinstance(key, ec.EllipticCurvePrivateKey):
            return key, "ES256"
    except Exception:
        pass

    try:
        decoded = base64.b64decode(key_data)
        if len(decoded) == 64:
            seed = decoded[:32]
            return ed25519.Ed25519PrivateKey.from_private_bytes(seed), "EdDSA"
    except Exception:
        pass

    raise ValueError("CDP key secret must be PEM EC or base64 Ed25519 (64 bytes)")


def build_cdp_jwt(*, method: str, host: str, path: str) -> str:
    """EdDSA/ES256 JWT for CDP REST — matches Coinbase CDP auth shape (uris claim)."""
    key_id, secret = cdp_credentials()
    if not key_id or not secret:
        raise RuntimeError("CDP_API_KEY_ID and CDP_API_KEY_SECRET required")

    private_key, algorithm = _parse_cdp_private_key(secret)
    now = int(time.time())
    header = {
        "alg": algorithm,
        "typ": "JWT",
        "kid": key_id,
        "nonce": "".join(secrets.choice("0123456789") for _ in range(16)),
    }
    # CDP SDK urlparse quirk: host+path without scheme → netloc empty, path holds both.
    parsed = urlparse(f"{host}{path}")
    uri = f"{method.upper()} {parsed.netloc}{parsed.path}"
    claims = {
        "sub": key_id,
        "iss": "cdp",
        "aud": ["cdp_service"],
        "nbf": now,
        "exp": now + 120,
        "uris": [uri],
    }
    header_b64 = _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url(json.dumps(claims, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")

    if algorithm == "EdDSA":
        sig = private_key.sign(signing_input)
    else:
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

        der = private_key.sign(signing_input, ec.ECDSA(hashes.SHA256()))
        r, s = decode_dss_signature(der)
        sig = r.to_bytes(32, "big") + s.to_bytes(32, "big")

    return f"{header_b64}.{payload_b64}.{_b64url(sig)}"


def _facilitator_parts() -> tuple[str, str, str]:
    """(origin_base, host, api_base_path) e.g. (.../x402, api.cdp.coinbase.com, /platform/v2/x402)."""
    raw = facilitator_base_url().rstrip("/")
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    host = parsed.netloc or "api.cdp.coinbase.com"
    base_path = (parsed.path or "").rstrip("/") or "/platform/v2/x402"
    if not base_path.startswith("/"):
        base_path = "/" + base_path
    origin = f"{parsed.scheme or 'https'}://{host}{base_path}"
    return origin, host, base_path


def _auth_headers(method: str, operation: str) -> dict[str, str]:
    """operation is verify|settle — JWT uri path is {base_path}/{operation}."""
    _origin, host, base_path = _facilitator_parts()
    full_path = f"{base_path}/{operation.lstrip('/')}"
    token = build_cdp_jwt(method=method, host=host, path=full_path)
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def decode_payment_header(raw: str) -> dict[str, Any] | None:
    """Decode PAYMENT-SIGNATURE / X-Payment value → paymentPayload dict."""
    if not raw or not isinstance(raw, str):
        return None
    text = raw.strip()
    if not text:
        return None
    # Prefer base64 (x402 wire), fall back to raw JSON.
    for candidate in (text,):
        try:
            pad = "=" * (-len(candidate) % 4)
            decoded = base64.b64decode(candidate + pad)
            obj = json.loads(decoded.decode("utf-8"))
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
        try:
            obj = json.loads(candidate)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
    return None


def payment_requirements_from_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    """Derive facilitator paymentRequirements from a v1/v2 paymentPayload."""
    if not isinstance(payload, dict):
        return None
    accepted = payload.get("accepted")
    if isinstance(accepted, dict) and accepted.get("scheme") and accepted.get("network"):
        # V2: accepted is the requirements object (no resource metadata).
        reqs = {
            k: accepted[k]
            for k in (
                "scheme",
                "network",
                "amount",
                "asset",
                "payTo",
                "maxTimeoutSeconds",
                "extra",
            )
            if k in accepted
        }
        # Some buyers still send maxAmountRequired on accepted — map to amount.
        if "amount" not in reqs and accepted.get("maxAmountRequired"):
            reqs["amount"] = accepted["maxAmountRequired"]
        return reqs if reqs.get("payTo") and reqs.get("amount") and reqs.get("asset") else None

    # V1 payload: scheme/network top-level; requirements rebuilt by caller often.
    if payload.get("x402Version") == 1 or (
        payload.get("scheme") and payload.get("network") and "accepted" not in payload
    ):
        # Incomplete without amount/asset/payTo — caller should supply local challenge.
        return None
    return None


def local_requirements(
    *,
    pay_to: str,
    amount: str,
    asset: str,
    network: str,
    scheme: str = "exact",
    max_timeout_seconds: int = 300,
    extra: dict | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "scheme": scheme,
        "network": network,
        "amount": amount,
        "asset": asset,
        "payTo": pay_to,
        "maxTimeoutSeconds": max_timeout_seconds,
    }
    if extra is not None:
        out["extra"] = extra
    else:
        out["extra"] = {"name": "USD Coin", "version": "2"}
    return out


def _post(
    operation: str, body: dict[str, Any], *, timeout: float = DEFAULT_TIMEOUT_SECONDS
) -> tuple[int, dict[str, Any]]:
    origin, _host, _base_path = _facilitator_parts()
    url = f"{origin.rstrip('/')}/{operation.lstrip('/')}"
    headers = _auth_headers("POST", operation)
    try:
        resp = requests.post(url, headers=headers, json=body, timeout=timeout)
    except requests.Timeout:
        return 0, {"error": "facilitator_timeout"}
    except requests.RequestException as exc:
        return 0, {"error": "facilitator_unreachable", "detail": str(exc)[:200]}
    try:
        data = resp.json()
    except Exception:
        data = {"error": "facilitator_non_json", "body": (resp.text or "")[:300]}
    if not isinstance(data, dict):
        data = {"error": "facilitator_bad_body", "body": data}
    return resp.status_code, data


def verify_and_settle(
    *,
    payment_payload: dict[str, Any],
    payment_requirements: dict[str, Any],
    timeout: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """POST verify then settle. Returns {ok, reason, ...} — never raises for HTTP failures."""
    if not facilitator_ready():
        return {
            "ok": False,
            "reason": "facilitator_credentials_missing",
            "paid": False,
            "note": "Set CDP_API_KEY_ID and CDP_API_KEY_SECRET to unlock paid x402 routes.",
        }

    version = payment_payload.get("x402Version") or payment_requirements.get("x402Version") or 2
    try:
        version = int(version)
    except (TypeError, ValueError):
        version = 2

    body = {
        "x402Version": version,
        "paymentPayload": payment_payload,
        "paymentRequirements": payment_requirements,
    }

    v_status, v_data = _post("verify", body, timeout=timeout)
    if v_status == 0:
        return {
            "ok": False,
            "reason": v_data.get("error") or "facilitator_unreachable",
            "paid": False,
            "verify": v_data,
        }
    if v_status >= 400 or not v_data.get("isValid"):
        return {
            "ok": False,
            "reason": v_data.get("invalidReason")
            or v_data.get("errorType")
            or "facilitator_verify_rejected",
            "paid": False,
            "verify_status": v_status,
            "verify": {
                k: v_data.get(k)
                for k in ("isValid", "invalidReason", "invalidMessage", "payer", "errorType", "errorMessage")
                if k in v_data
            },
        }

    s_status, s_data = _post("settle", body, timeout=timeout)
    if s_status == 0:
        return {
            "ok": False,
            "reason": s_data.get("error") or "facilitator_settle_unreachable",
            "paid": False,
            "verify": {"isValid": True, "payer": v_data.get("payer")},
            "settle": s_data,
        }
    if s_status >= 400 or not s_data.get("success"):
        return {
            "ok": False,
            "reason": s_data.get("errorReason")
            or s_data.get("errorType")
            or "facilitator_settle_rejected",
            "paid": False,
            "settle_status": s_status,
            "verify": {"isValid": True, "payer": v_data.get("payer")},
            "settle": {
                k: s_data.get(k)
                for k in (
                    "success",
                    "errorReason",
                    "errorMessage",
                    "payer",
                    "transaction",
                    "network",
                    "amount",
                )
                if k in s_data
            },
        }

    return {
        "ok": True,
        "reason": "facilitator_settled",
        "paid": True,
        "payer": s_data.get("payer") or v_data.get("payer"),
        "transaction": s_data.get("transaction"),
        "network": s_data.get("network") or payment_requirements.get("network"),
        "amount": s_data.get("amount") or payment_requirements.get("amount"),
        "note": "Payment verified and settled via CDP facilitator.",
    }
