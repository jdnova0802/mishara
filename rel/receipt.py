"""Ed25519 receipt for release MAY. Separate keys from Gate. No cosign weld."""
from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any

SPEC = "rel-v1"
DEFAULT_TTL_SECONDS = 300

_PRIV_ENV = "REL_RECEIPT_PRIVATE_KEY"
_PUB_ENV = "REL_RECEIPT_PUBLIC_KEY"


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(text: str) -> bytes:
    pad = "=" * ((4 - len(text) % 4) % 4)
    return base64.urlsafe_b64decode(text + pad)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _key_bytes(env: str) -> bytes | None:
    raw = (os.environ.get(env) or "").strip()
    if not raw:
        return None
    try:
        return base64.b64decode(raw)
    except Exception:
        return None


def _signing_key():
    raw = _key_bytes(_PRIV_ENV)
    if not raw or len(raw) != 32:
        return None
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    return Ed25519PrivateKey.from_private_bytes(raw)


def _public_key_bytes() -> bytes | None:
    raw = _key_bytes(_PUB_ENV)
    if raw and len(raw) == 32:
        return raw
    key = _signing_key()
    if not key:
        return None
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    return key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)


def key_id() -> str:
    pub = _public_key_bytes() or b""
    return hashlib.sha256(pub).hexdigest()[:16] if pub else "unconfigured"


def mint_receipt_jwt(
    *,
    evaluation_id: str,
    decision: str,
    reason: str | None,
    instrument_hash: str | None,
    authority_hash: str | None,
    control_platform: str | None,
    instrument_state: str | None,
    signals: list[str],
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
) -> str | None:
    key = _signing_key()
    if not key:
        return None
    if decision != "EXIST":
        exists = False
    else:
        exists = True
    now = _utc_now()
    exp = now + timedelta(seconds=max(30, min(int(ttl_seconds or DEFAULT_TTL_SECONDS), 3600)))
    payload = {
        "spec": SPEC,
        "jti": evaluation_id,
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
        "dec": decision,
        "rel": decision,
        "rsn": reason,
        "inh": instrument_hash,
        "ah": authority_hash,
        "ctr": control_platform,
        "ins": instrument_state,
        "sig": list(signals or []),
        "exists": exists,
        "halt": decision in {"HOLD", "NONEXIST"},
    }
    header = {"alg": "EdDSA", "typ": "JWT", "kid": key_id()}
    header_b64 = _b64url(_canonical_json(header).encode("utf-8"))
    payload_b64 = _b64url(_canonical_json(payload).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig = key.sign(signing_input)
    return f"{header_b64}.{payload_b64}.{_b64url(sig)}"


def verify_receipt_jwt(token: str) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "spec": SPEC,
        "valid": False,
        "decision": None,
        "reason": None,
        "payload": None,
    }
    if not token or not isinstance(token, str):
        meta["reason"] = "missing_token"
        return meta
    parts = token.split(".")
    if len(parts) != 3:
        meta["reason"] = "malformed_jwt"
        return meta
    try:
        header = json.loads(_b64url_decode(parts[0]))
        payload = json.loads(_b64url_decode(parts[1]))
        sig = _b64url_decode(parts[2])
    except Exception:
        meta["reason"] = "decode_error"
        return meta
    pub = _public_key_bytes()
    if not pub:
        meta["reason"] = "verify_unconfigured"
        return meta
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        Ed25519PublicKey.from_public_bytes(pub).verify(
            sig, f"{parts[0]}.{parts[1]}".encode("utf-8")
        )
    except Exception:
        meta["reason"] = "bad_signature"
        return meta
    if header.get("alg") != "EdDSA":
        meta["reason"] = "unsupported_alg"
        return meta
    exp = payload.get("exp")
    if exp is not None and int(exp) < int(_utc_now().timestamp()):
        meta["reason"] = "expired"
        meta["payload"] = payload
        return meta
    decision = str(payload.get("dec") or "")
    if payload.get("exists") is True and decision != "EXIST":
        meta["reason"] = "exists_without_exist"
        meta["payload"] = payload
        return meta
    meta["valid"] = True
    meta["decision"] = decision
    meta["payload"] = payload
    return meta
