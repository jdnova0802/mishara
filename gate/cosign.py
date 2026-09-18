"""Operator cosign — the machine key cannot be the operator mouth.

One Render env var can mint every distinctive hop we have.
Durability is a second role, a second key, never living on the box.
Not FROST. Not an air-gap. Two signatures over the same hop bytes.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from typing import Any

SPEC = "gate-cosign-v1"
INVARIANT = "The machine key cannot wear the operator mouth."
STATUSES = ("OK", "GAP", "HOLD", "BAD")


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _b64decode(s: str | None) -> bytes | None:
    if not s or not str(s).strip():
        return None
    raw = str(s).strip().replace("-", "+").replace("_", "/")
    pad = "=" * (-len(raw) % 4)
    try:
        return base64.b64decode(raw + pad, validate=False)
    except Exception:
        return None


def _b64encode(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")


def _pub_from_env() -> bytes | None:
    return _b64decode(os.getenv("GATE_OPERATOR_PUBLIC_KEY"))


def operator_fingerprint(pub: bytes | None = None) -> str | None:
    raw = pub if pub is not None else _pub_from_env()
    if not raw:
        return None
    return hashlib.sha256(raw).hexdigest()[:16]


def preimage(claims: dict[str, Any]) -> bytes:
    body = {
        "spec": SPEC,
        "fp": claims.get("fp") or claims.get("fingerprint"),
        "dec": claims.get("dec") or claims.get("decision"),
        "act": claims.get("act") or claims.get("action"),
        "sink": claims.get("sink"),
        "owh": claims.get("owh") or claims.get("otherwise_hash"),
        "agc": claims.get("agc") or claims.get("agency"),
        "nst": claims.get("nst") or claims.get("nested_stit"),
        "stl": claims.get("stl") or claims.get("settler_id"),
        "mut": claims.get("mut") or claims.get("mutation"),
        "iaa": claims.get("iaa") or claims.get("in_authority"),
        "chn": claims.get("chn") or claims.get("chain_grade"),
        "cma": claims.get("cma") or claims.get("chain_min_agency"),
        "ugp": claims.get("ugp") or claims.get("upstream_gap"),
    }
    return _canonical_json(body).encode("utf-8")


def preimage_hash(claims: dict[str, Any]) -> str:
    return hashlib.sha256(preimage(claims)).hexdigest()


def verify_sig(*, claims: dict[str, Any], signature: str | None, public_key: bytes | None) -> bool:
    if not signature or not public_key:
        return False
    sig = _b64decode(signature)
    if not sig:
        return False
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        Ed25519PublicKey.from_public_bytes(public_key).verify(sig, preimage(claims))
        return True
    except Exception:
        return False


def sign(*, claims: dict[str, Any], private_key: bytes) -> str:
    return sign_preimage(preimage(claims), private_key)


def sign_preimage(raw: bytes, private_key: bytes) -> str:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    key = Ed25519PrivateKey.from_private_bytes(private_key)
    return _b64encode(key.sign(raw))


def witness(
    *,
    machine_fpr: str | None,
    operator_fpr: str | None,
    verified: bool,
    required: bool,
    signature_present: bool,
) -> dict[str, Any]:
    """Role-split cosign. Same fingerprint on both mouths is a substitution."""
    same = bool(machine_fpr and operator_fpr and machine_fpr == operator_fpr)
    if same:
        status = "BAD"
        halt = True
        gap = False
        gap_reason = None
        reason = "role_substitution"
    elif required and not operator_fpr:
        status = "BAD"
        halt = True
        gap = True
        gap_reason = "missing_operator_pin"
        reason = "missing_operator_pin"
    elif required and not signature_present:
        status = "HOLD"
        halt = True
        gap = False
        gap_reason = None
        reason = "operator_unsigned"
    elif required and not verified:
        status = "BAD"
        halt = True
        gap = False
        gap_reason = None
        reason = "operator_bad_sig"
    elif not operator_fpr:
        status = "GAP"
        halt = False
        gap = True
        gap_reason = "missing_operator"
        reason = None
    elif verified:
        status = "OK"
        halt = False
        gap = False
        gap_reason = None
        reason = None
    else:
        status = "GAP"
        halt = False
        gap = True
        gap_reason = "operator_unsigned"
        reason = None
    return {
        "spec": SPEC,
        "status": status,
        "required": required,
        "verified": bool(verified) and not same,
        "halt": halt,
        "gap": gap,
        "gap_reason": gap_reason,
        "reason": reason,
        "machine_fpr": machine_fpr,
        "operator_fpr": operator_fpr,
        "invariant": INVARIANT,
        "not": "FROST, one env var, dual-control as air-gap, or the machine key wearing a human mouth.",
    }


def from_env_and_body(policy: dict | None, body: dict | None) -> tuple[bytes | None, str | None, bool]:
    """Pinned operator pubkey, caller signature, whether cosign is required."""
    pol = policy if isinstance(policy, dict) else {}
    b = body if isinstance(body, dict) else {}
    pub = _pub_from_env()
    sig = b.get("operator_sig") or b.get("cosign_sig") or (b.get("cosign") or {}).get("signature")
    sig_s = str(sig).strip() if sig else None
    required = bool(pub) or bool(pol.get("require_operator") or b.get("require_operator"))
    return pub, sig_s, required
