"""
Evidence custody — signed, content-addressed receipts.

Goal (smallest useful version):
- Each bind event gets a canonical receipt JSON.
- receipt_hash = sha256(canonical_receipt_json)
- receipt_signature = Ed25519 signature over receipt_hash
- Bind events are chained via prev_receipt_hash (simple append-only chain).

Third-party verification:
- fetch receipt by event_id
- verify signature using public key (Gate publishes key via the receipt payload)
- verify chaining by following prev_receipt_hash to older receipts

No PII is included: only fuse_id, job_id, decision, acted, verify_url,
and receipt timestamp + upstream hop state if present.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any


def _b64decode_raw(s: str | None) -> bytes | None:
    if not s:
        return None
    s = s.strip()
    if not s:
        return None
    # Accept both standard and URL-safe base64.
    s = s.replace("-", "+").replace("_", "/")
    pad = "=" * (-len(s) % 4)
    try:
        return base64.b64decode(s + pad, validate=False)
    except Exception:
        return None


def _b64encode_raw(b: bytes) -> str:
    return base64.b64encode(b).decode("utf-8")


def _canonical_json(obj: Any) -> str:
    # JSON canonicalization: stable key order + no whitespace.
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_receipt_hash(canonical_receipt_json: str) -> str:
    return hashlib.sha256(canonical_receipt_json.encode("utf-8")).hexdigest()


def _ed25519_signing_key():
    # Env vars:
    #   - GATE_RECEIPT_PRIVATE_KEY: base64(raw 32-byte Ed25519 private key)
    #   - GATE_RECEIPT_PUBLIC_KEY:  base64(raw 32-byte Ed25519 public key)
    #
    # If keys are missing, signing is disabled (hashes still work).
    priv_b = _b64decode_raw(os.getenv("GATE_RECEIPT_PRIVATE_KEY"))
    if not priv_b:
        return None
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    try:
        return Ed25519PrivateKey.from_private_bytes(priv_b)
    except Exception:
        return None


def _ed25519_public_key_bytes() -> bytes | None:
    # Prefer env public key; fall back to deriving it from private if possible.
    pub_b = _b64decode_raw(os.getenv("GATE_RECEIPT_PUBLIC_KEY"))
    if pub_b:
        return pub_b
    key = _ed25519_signing_key()
    if not key:
        return None
    try:
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

        return key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    except Exception:
        return None


def receipt_public_key_fingerprint() -> str | None:
    pub_b = _ed25519_public_key_bytes()
    if not pub_b:
        return None
    return hashlib.sha256(pub_b).hexdigest()[:16]


def sign_receipt_hash(receipt_hash_hex: str) -> str | None:
    key = _ed25519_signing_key()
    if not key:
        return None
    # Sign bytes of the receipt hash (hex string).
    sig = key.sign(receipt_hash_hex.encode("utf-8"))
    return _b64encode_raw(sig)


def build_canonical_receipt(
    *,
    event_id: str,
    fuse_id: str,
    job_id: str | None,
    decision: str,
    acted: bool | None,
    verify_url: str | None,
    created_at: str,
    hop: dict | None = None,
    prev_receipt_hash: str | None = None,
) -> dict:
    hop = hop if isinstance(hop, dict) else {}
    return {
        "spec": "gate-receipt-v1",
        "id": event_id,
        "prev_receipt_hash": prev_receipt_hash,
        "fuse_id": fuse_id,
        "job_id": job_id,
        "decision": decision,
        "acted": acted,
        "verify_url": verify_url,
        "state": hop.get("state"),
        "halt": hop.get("halt"),
        "verdict": hop.get("verdict"),
        "created_at": created_at,
        "time_is_utc": True,
        "created_at_format": "iso-8601",
        "gate": "Nisaba LLC",
    }


def issue_receipt(
    *,
    event_id: str,
    fuse_id: str,
    job_id: str | None,
    decision: str,
    acted: bool | None,
    verify_url: str | None,
    created_at: str,
    hop: dict | None,
    prev_receipt_hash: str | None,
) -> dict:
    """
    Returns:
      {
        "receipt_hash": <sha256 hex>,
        "receipt_signature": <base64> | None,
        "receipt_public_key_fingerprint": <hex str> | None,
        "prev_receipt_hash": ...
        "canonical_receipt_json": <string>,   (optional; omit for DB)
      }
    """
    canonical = build_canonical_receipt(
        event_id=event_id,
        fuse_id=fuse_id,
        job_id=job_id,
        decision=decision,
        acted=acted,
        verify_url=verify_url,
        created_at=created_at,
        hop=hop,
        prev_receipt_hash=prev_receipt_hash,
    )
    canonical_json = _canonical_json(canonical)
    receipt_hash = compute_receipt_hash(canonical_json)
    sig = sign_receipt_hash(receipt_hash)
    return {
        "receipt_hash": receipt_hash,
        "receipt_signature": sig,
        "receipt_public_key_fingerprint": receipt_public_key_fingerprint(),
        "prev_receipt_hash": prev_receipt_hash,
        "canonical_receipt_json": canonical_json,
    }


def receipt_to_public_payload(
    *, receipt_row: dict, canonical_receipt_json: str | None = None, public_url: str | None = None
) -> dict:
    # Gate does not publish full hop; only the canonical receipt fields are used.
    # canonical_receipt_json may be supplied if you want the client to recompute the hash.
    payload = {
        "spec": "gate-receipt-payload-v1",
        "event_id": receipt_row.get("id"),
        "receipt_hash": receipt_row.get("receipt_hash"),
        "prev_receipt_hash": receipt_row.get("prev_receipt_hash"),
        "receipt_signature": receipt_row.get("receipt_signature"),
        "receipt_public_key_fingerprint": receipt_row.get("receipt_public_key_fingerprint"),
        "created_at": receipt_row.get("created_at"),
        "fuse_id": receipt_row.get("fuse_id"),
        "job_id": receipt_row.get("job_id"),
        "decision": receipt_row.get("decision"),
        "acted": bool(receipt_row["acted"]) if receipt_row.get("acted") is not None else None,
        "verify_url": receipt_row.get("verify_url"),
        # Include state hints without PII.
        "state": None,
        "halt": None,
        "verdict": None,
    }
    try:
        hop = receipt_row.get("hop") if isinstance(receipt_row.get("hop"), dict) else None
        if hop is None:
            hop_json = receipt_row.get("hop_json")
            if hop_json:
                hop = json.loads(hop_json)
        if hop:
            payload["state"] = hop.get("state")
            payload["halt"] = hop.get("halt")
            payload["verdict"] = hop.get("verdict")
            # Rebuild canonical receipt object for client-side recompute.
            canonical_obj = build_canonical_receipt(
                event_id=receipt_row.get("id"),
                fuse_id=receipt_row.get("fuse_id"),
                job_id=receipt_row.get("job_id"),
                decision=receipt_row.get("decision"),
                acted=receipt_row.get("acted"),
                verify_url=receipt_row.get("verify_url"),
                created_at=receipt_row.get("created_at"),
                hop=hop,
                prev_receipt_hash=receipt_row.get("prev_receipt_hash"),
            )
            payload["canonical_receipt"] = canonical_obj
    except Exception:
        pass

    # If we couldn't parse hop_json (or it was missing), still include a
    # canonical receipt object derived from the already-stored fields.
    if "canonical_receipt" not in payload:
        try:
            canonical_obj = build_canonical_receipt(
                event_id=receipt_row.get("id"),
                fuse_id=receipt_row.get("fuse_id"),
                job_id=receipt_row.get("job_id"),
                decision=receipt_row.get("decision"),
                acted=receipt_row.get("acted"),
                verify_url=receipt_row.get("verify_url"),
                created_at=receipt_row.get("created_at"),
                hop={},
                prev_receipt_hash=receipt_row.get("prev_receipt_hash"),
            )
            payload["canonical_receipt"] = canonical_obj
        except Exception:
            pass

    if canonical_receipt_json:
        payload["canonical_receipt_json"] = canonical_receipt_json

    try:
        from gate import counterfactual as counterfactual_mod
    except ImportError:
        import counterfactual as counterfactual_mod

    payload = counterfactual_mod.attach_to_receipt_payload(payload, receipt_row, public_url)
    if public_url:
        try:
            from gate import inhabitant as inhabitant_mod
        except ImportError:
            import inhabitant as inhabitant_mod
        payload = inhabitant_mod.attach_to_receipt_payload(payload, receipt_row, public_url)
    return payload

