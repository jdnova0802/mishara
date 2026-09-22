"""Receipt signing custody — keys out of app logic.

Backends (GATE_RECEIPT_CUSTODY):
  env  — GATE_RECEIPT_PRIVATE_KEY / GATE_RECEIPT_PUBLIC_KEY (default)
  file — sealed raw Ed25519 key material on disk (GATE_RECEIPT_KEY_FILE)
  kms  — AWS KMS asymmetric Ed25519 (GATE_RECEIPT_KMS_KEY_ID); optional boto3

Institutional tell: signing is a custody concern, not scattered crypto in routes.
Outside GATE_DEV_MODE, missing/unavailable custody → unsigned_halt (fail closed).
"""

from __future__ import annotations

import base64
import hashlib
import os
from dataclasses import dataclass
from typing import Protocol


def _b64decode_raw(s: str | None) -> bytes | None:
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    s = s.replace("-", "+").replace("_", "/")
    pad = "=" * (-len(s) % 4)
    try:
        return base64.b64decode(s + pad, validate=False)
    except Exception:
        return None


def _b64encode_raw(b: bytes) -> str:
    return base64.b64encode(b).decode("utf-8")


def _fingerprint(pub: bytes | None) -> str | None:
    if not pub:
        return None
    return hashlib.sha256(pub).hexdigest()[:16]


class CustodyBackend(Protocol):
    name: str

    def public_key_bytes(self) -> bytes | None: ...

    def sign(self, receipt_hash_hex: str) -> bytes | None: ...

    def available(self) -> bool: ...


@dataclass
class EnvCustody:
    name: str = "env"

    def _priv(self):
        priv_b = _b64decode_raw(os.getenv("GATE_RECEIPT_PRIVATE_KEY"))
        if not priv_b:
            return None
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        try:
            return Ed25519PrivateKey.from_private_bytes(priv_b)
        except Exception:
            return None

    def public_key_bytes(self) -> bytes | None:
        pub_b = _b64decode_raw(os.getenv("GATE_RECEIPT_PUBLIC_KEY"))
        if pub_b:
            return pub_b
        key = self._priv()
        if not key:
            return None
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

        return key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)

    def sign(self, receipt_hash_hex: str) -> bytes | None:
        key = self._priv()
        if not key:
            return None
        try:
            return key.sign(receipt_hash_hex.encode("utf-8"))
        except Exception:
            return None

    def available(self) -> bool:
        return self._priv() is not None and self.public_key_bytes() is not None


@dataclass
class FileCustody:
    """Sealed key file: base64(raw 32-byte Ed25519 private) on one line.

    Optional second line: base64(raw 32-byte public). If omitted, derived.
    Path: GATE_RECEIPT_KEY_FILE (default /var/data/receipt_ed25519.key).
    """

    name: str = "file"

    def _path(self) -> str:
        return (
            os.getenv("GATE_RECEIPT_KEY_FILE", "").strip()
            or "/var/data/receipt_ed25519.key"
        )

    def _load_priv_pub(self) -> tuple[bytes | None, bytes | None]:
        path = self._path()
        if not os.path.isfile(path):
            return None, None
        try:
            with open(path, "r", encoding="utf-8") as fh:
                raw = fh.read().strip().splitlines()
        except OSError:
            return None, None
        if not raw:
            return None, None
        priv_b = _b64decode_raw(raw[0].strip())
        pub_b = _b64decode_raw(raw[1].strip()) if len(raw) > 1 else None
        return priv_b, pub_b

    def _priv(self):
        priv_b, _ = self._load_priv_pub()
        if not priv_b:
            return None
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        try:
            return Ed25519PrivateKey.from_private_bytes(priv_b)
        except Exception:
            return None

    def public_key_bytes(self) -> bytes | None:
        _, pub_b = self._load_priv_pub()
        if pub_b:
            return pub_b
        key = self._priv()
        if not key:
            return None
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

        return key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)

    def sign(self, receipt_hash_hex: str) -> bytes | None:
        key = self._priv()
        if not key:
            return None
        try:
            return key.sign(receipt_hash_hex.encode("utf-8"))
        except Exception:
            return None

    def available(self) -> bool:
        return self._priv() is not None and self.public_key_bytes() is not None


@dataclass
class KmsCustody:
    """AWS KMS Ed25519 asymmetric key. Requires boto3 + GATE_RECEIPT_KMS_KEY_ID."""

    name: str = "kms"

    def _key_id(self) -> str:
        return (os.getenv("GATE_RECEIPT_KMS_KEY_ID") or "").strip()

    def _client(self):
        if not self._key_id():
            return None
        try:
            import boto3  # type: ignore
        except ImportError:
            return None
        region = (os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1").strip()
        try:
            return boto3.client("kms", region_name=region)
        except Exception:
            return None

    def public_key_bytes(self) -> bytes | None:
        # Prefer pinned env public for verify without KMS round-trip.
        pinned = _b64decode_raw(os.getenv("GATE_RECEIPT_PUBLIC_KEY"))
        if pinned:
            return pinned
        client = self._client()
        kid = self._key_id()
        if not client or not kid:
            return None
        try:
            out = client.get_public_key(KeyId=kid)
            der = out.get("PublicKey") or b""
            # SPKI DER → raw 32-byte Ed25519 if possible; else return DER for fingerprint only.
            if len(der) >= 32:
                # Ed25519 SPKI is 44 bytes; raw key is last 32.
                if len(der) == 44:
                    return der[-32:]
                return der[-32:] if len(der) > 32 else der
            return None
        except Exception:
            return None

    def sign(self, receipt_hash_hex: str) -> bytes | None:
        client = self._client()
        kid = self._key_id()
        if not client or not kid:
            return None
        try:
            out = client.sign(
                KeyId=kid,
                Message=receipt_hash_hex.encode("utf-8"),
                MessageType="RAW",
                SigningAlgorithm="ED25519_SHA_512",
            )
            sig = out.get("Signature")
            return sig if isinstance(sig, (bytes, bytearray)) else None
        except Exception:
            return None

    def available(self) -> bool:
        return bool(self._key_id()) and self._client() is not None and self.public_key_bytes() is not None


def custody_mode() -> str:
    mode = (os.getenv("GATE_RECEIPT_CUSTODY") or "env").strip().lower()
    if mode not in ("env", "file", "kms"):
        return "env"
    return mode


def get_custody() -> CustodyBackend:
    mode = custody_mode()
    if mode == "file":
        return FileCustody()
    if mode == "kms":
        return KmsCustody()
    return EnvCustody()


def sign_receipt_hash(receipt_hash_hex: str) -> str | None:
    sig = get_custody().sign(receipt_hash_hex)
    if not sig:
        return None
    return _b64encode_raw(sig)


def public_key_bytes() -> bytes | None:
    return get_custody().public_key_bytes()


def public_key_b64() -> str | None:
    pub = public_key_bytes()
    return _b64encode_raw(pub) if pub else None


def public_key_fingerprint() -> str | None:
    return _fingerprint(public_key_bytes())


def custody_status(*, public_url: str | None = None) -> dict:
    """Public custody posture — no private material."""
    backend = get_custody()
    mode = custody_mode()
    avail = False
    try:
        avail = bool(backend.available())
    except Exception:
        avail = False
    fp = public_key_fingerprint()
    base = (public_url or "").rstrip("/")
    return {
        "spec": "gate-receipt-custody-v1",
        "backend": mode,
        "available": avail,
        "fingerprint": fp,
        "alg": "Ed25519",
        "signed_over": "utf-8 hex string of receipt_hash",
        "kms_key_configured": bool((os.getenv("GATE_RECEIPT_KMS_KEY_ID") or "").strip()),
        "key_file": (os.getenv("GATE_RECEIPT_KEY_FILE") or "").strip() or None
        if mode == "file"
        else None,
        "signing_required_outside_dev": True,
        "fail_closed": "unsigned receipt issue → halt outside GATE_DEV_MODE",
        "their_production": False,
        "urls": {
            "custody": f"{base}/.well-known/custody.json" if base else None,
            "receipt_key": f"{base}/.well-known/receipt-key.json" if base else None,
        },
    }


# --- Fail-closed failure matrix (engineering diligence) ---

FAILURE_MATRIX = (
    {
        "id": "custody_unavailable",
        "condition": "signing backend missing or cannot sign",
        "required_behavior": "unsigned_halt outside DEV; no bind_event acting as evidence",
    },
    {
        "id": "public_key_absent",
        "condition": "no verifiable public key bytes",
        "required_behavior": "staple key_present=false; stranger audit cannot all_pass",
    },
    {
        "id": "velaru_unreachable",
        "condition": "upstream fuse timeout / 5xx",
        "required_behavior": "HTTP 503 halt; never treat UNREACHABLE as LIVE",
    },
    {
        "id": "gate_process_down",
        "condition": "Gate host unavailable at weld time",
        "required_behavior": "welded write must fail closed in their runtime (worker/PAS)",
    },
    {
        "id": "chain_break",
        "condition": "prev_receipt_hash does not match prior receipt_hash",
        "required_behavior": "stranger audit chain_ok=false",
    },
    {
        "id": "staple_mismatch",
        "condition": "receipt fingerprint ≠ published custody fingerprint",
        "required_behavior": "fingerprint_ok=false; do not trust signature",
    },
)


def failure_matrix() -> dict:
    return {
        "spec": "gate-fail-closed-matrix-v1",
        "product": "Clearance before irreversible write",
        "default": "DENY under uncertainty",
        "rows": list(FAILURE_MATRIX),
        "their_production": False,
    }
