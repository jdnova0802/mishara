"""Public audit of the live receipt signature, and the hybrid signer beside it.

The published receipt stays SHA-256 + Ed25519 until GATE_RECEIPT_ML_DSA_SEED
and GATE_RECEIPT_CA_PRIVATE_KEY are set on the host. This module does not
call that receipt quantum-safe.
"""
from __future__ import annotations

import base64
import hashlib
import os
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

SPEC = "gate-signature-audit-v1"
DATED = "2026-10-30"
DRAFT_URL = "https://www.ietf.org/archive/id/draft-stone-aivs-01.html"
ML_DSA_CONTEXT = b"gate-receipt-v1"
ML_DSA_ALG = "ML-DSA-65"


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode("ascii")


def ml_dsa_backend() -> bool:
    try:
        from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

        return callable(getattr(MLDSA65PrivateKey, "from_seed_bytes", None))
    except Exception:
        return False


def ml_dsa_seed() -> bytes | None:
    raw = receipt_mod._b64decode_raw(os.getenv("GATE_RECEIPT_ML_DSA_SEED"))
    if not raw or len(raw) != 32:
        return None
    return raw


def ml_dsa_configured() -> bool:
    return ml_dsa_seed() is not None and ml_dsa_backend()


def _ml_dsa_private():
    seed = ml_dsa_seed()
    if not seed or not ml_dsa_backend():
        return None
    from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

    return MLDSA65PrivateKey.from_seed_bytes(seed)


def ml_dsa_public_b64() -> str | None:
    key = _ml_dsa_private()
    if key is None:
        return None
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    pub = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    return _b64(pub)


def sign_ml_dsa(message: bytes) -> str | None:
    """ML-DSA-65 over the same bytes Ed25519 signs. Absent when no seed is set."""
    key = _ml_dsa_private()
    if key is None or not message:
        return None
    return _b64(key.sign(message, ML_DSA_CONTEXT))


def verify_ml_dsa(message: bytes, signature_b64: str | None) -> bool:
    if not message or not signature_b64:
        return False
    key = _ml_dsa_private()
    sig = receipt_mod._b64decode_raw(signature_b64)
    if key is None or not sig:
        return False
    try:
        key.public_key().verify(sig, message, ML_DSA_CONTEXT)
        return True
    except Exception:
        return False


def verify_receipt_signatures(
    *, receipt_hash: str, signature_b64: str | None, ml_dsa_b64: str | None = None
) -> bool:
    """Ed25519 remains sufficient. A present ML-DSA signature must also verify."""
    if not receipt_mod.verify_receipt_signature(
        receipt_hash=receipt_hash, signature_b64=signature_b64
    ):
        return False
    if not ml_dsa_b64:
        return True
    return verify_ml_dsa(receipt_hash.encode("utf-8"), ml_dsa_b64)


def _ca_private():
    raw = receipt_mod._b64decode_raw(os.getenv("GATE_RECEIPT_CA_PRIVATE_KEY"))
    if not raw:
        return None
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    try:
        return Ed25519PrivateKey.from_private_bytes(raw)
    except Exception:
        return None


def identity_key_configured() -> bool:
    return _ca_private() is not None and receipt_mod._ed25519_public_key_bytes() is not None


def certificate_chain_der() -> list[bytes] | None:
    """Leaf (receipt key) then identity cert. None until the identity key is set."""
    ca_key = _ca_private()
    receipt_pub = receipt_mod._ed25519_public_key_bytes()
    if ca_key is None or not receipt_pub:
        return None
    from cryptography import x509
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    from cryptography.x509.oid import NameOID

    leaf_key = Ed25519PublicKey.from_public_bytes(receipt_pub)
    not_before = datetime(2026, 10, 30, tzinfo=timezone.utc)
    not_after = not_before + timedelta(days=3650)
    identity_name = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "Nisaba LLC")]
    )
    leaf_name = x509.Name(
        [x509.NameAttribute(NameOID.COMMON_NAME, "gate.velaru.xyz")]
    )

    def _serial(material: bytes) -> int:
        return int.from_bytes(hashlib.sha256(material).digest()[:16], "big") | 1

    identity = (
        x509.CertificateBuilder()
        .subject_name(identity_name)
        .issuer_name(identity_name)
        .public_key(ca_key.public_key())
        .serial_number(_serial(b"identity"))
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .sign(ca_key, None)
    )
    leaf = (
        x509.CertificateBuilder()
        .subject_name(leaf_name)
        .issuer_name(identity_name)
        .public_key(leaf_key)
        .serial_number(_serial(receipt_pub))
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(ca_key, None)
    )
    return [leaf.public_bytes(serialization_encoding()), identity.public_bytes(serialization_encoding())]


def serialization_encoding():
    from cryptography.hazmat.primitives.serialization import Encoding

    return Encoding.DER


def x5c() -> list[str] | None:
    chain = certificate_chain_der()
    if not chain:
        return None
    return [_b64(cert) for cert in chain]


def publish() -> dict[str, Any]:
    chain = x5c()
    ml_pub = ml_dsa_public_b64()
    return {
        "spec": SPEC,
        "dated": DATED,
        "subject": "The live receipt signature is Ed25519",
        "finding": (
            "Gate audited its own receipt against draft-stone-aivs-01. "
            "Both sign a SHA-256 hash with Ed25519 only. Gate publishes the raw "
            "public key itself, at /.well-known/prefinality-jwks.json. "
            "There is no certificate chain on that key. "
            "The live receipt is not quantum-safe."
        ),
        "compared_to": DRAFT_URL,
        "live": {
            "hash": "SHA-256",
            "signature": "Ed25519",
            "jwt_alg": "EdDSA",
            "key_publication": "/.well-known/prefinality-jwks.json",
            "certificate_chain": bool(chain),
            "ml_dsa": bool(ml_pub),
            "quantum_safe": False,
        },
        "scheduled": {
            "hybrid": "Ed25519 and ML-DSA-65 over the same receipt-hash bytes",
            "context": ML_DSA_CONTEXT.decode("ascii"),
            "ed25519_verification": "stays valid for receipts that have no second signature",
            "certificate": (
                "An Ed25519 certificate for gate.velaru.xyz, signed by a Nisaba identity key, "
                "published as x5c on the receipt JWK"
            ),
            "turns_on_when": [
                "GATE_RECEIPT_ML_DSA_SEED",
                "GATE_RECEIPT_CA_PRIVATE_KEY",
            ],
        },
        "signer_ready": {
            "ml_dsa_backend": ml_dsa_backend(),
            "ml_dsa_seed_configured": ml_dsa_configured(),
            "identity_key_configured": identity_key_configured(),
            "ml_dsa_public_key": ml_pub,
            "x5c": chain,
        },
        "not": [
            "Not a claim that the published receipts are quantum-safe.",
            "Not a claim that every attestation draft has this gap. The comparison is draft-stone-aivs-01.",
            "Not a new product. The halt receipt is the same object.",
        ],
    }
