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


def receipt_public_key_b64() -> str | None:
    pub_b = _ed25519_public_key_bytes()
    if not pub_b:
        return None
    return _b64encode_raw(pub_b)


def public_key_staple(*, public_url: str | None = None) -> dict:
    """Published Ed25519 staple — strangers fetch this once, verify forever offline."""
    pub_b64 = receipt_public_key_b64()
    fp = receipt_public_key_fingerprint()
    base = (public_url or "").rstrip("/")
    return {
        "spec": "gate-receipt-key-v1",
        "alg": "Ed25519",
        "public_key_b64": pub_b64,
        "fingerprint": fp,
        "signed_over": "utf-8 hex string of receipt_hash (sha256 of canonical receipt JSON)",
        "signing_required_outside_dev": True,
        "verify": (
            "1) recompute receipt_hash = sha256(canonical_receipt_json) "
            "2) Ed25519.verify(public_key, receipt_hash.encode('utf-8'), signature) "
            "3) fingerprint must match sha256(public_key)[:16] "
            "4) walk prev_receipt_hash; check Merkle inclusion vs evidence-head"
        ),
        "urls": {
            "staple": f"{base}/.well-known/receipt-key.json" if base else None,
            "evidence_head": f"{base}/.well-known/evidence-head.json" if base else None,
            "stranger_verify": f"{base}/receipt/{{event_id}}" if base else None,
            "audit": f"{base}/.well-known/receipt/{{event_id}}/verify.json" if base else None,
        },
        "their_production": False,
        "key_present": bool(pub_b64),
    }


def sign_receipt_hash(receipt_hash_hex: str) -> str | None:
    key = _ed25519_signing_key()
    if not key:
        return None
    # Sign bytes of the receipt hash (hex string).
    sig = key.sign(receipt_hash_hex.encode("utf-8"))
    return _b64encode_raw(sig)


def verify_receipt_signature(
    *,
    receipt_hash: str,
    signature_b64: str | None,
    public_key_b64: str | None = None,
) -> bool:
    """Cold verify: Ed25519 over utf-8 receipt_hash hex string."""
    if not receipt_hash or not signature_b64:
        return False
    pub_b = _b64decode_raw(public_key_b64) if public_key_b64 else _ed25519_public_key_bytes()
    sig_b = _b64decode_raw(signature_b64)
    if not pub_b or not sig_b:
        return False
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        Ed25519PublicKey.from_public_bytes(pub_b).verify(
            sig_b, receipt_hash.encode("utf-8")
        )
        return True
    except Exception:
        return False


def verify_canonical_hash(*, canonical_receipt: dict | None, receipt_hash: str | None) -> bool:
    if not isinstance(canonical_receipt, dict) or not receipt_hash:
        return False
    recomputed = compute_receipt_hash(_canonical_json(canonical_receipt))
    return recomputed == receipt_hash


def stranger_audit(
    *,
    receipt_row: dict,
    prev_row: dict | None,
    inclusion_bundle: dict | None,
    public_url: str | None = None,
) -> dict:
    """
    God-mode stranger check — one object, no login:
    hash_ok · signature_ok · fingerprint_ok · chain_ok · inclusion_ok · all_pass
    """
    payload = receipt_to_public_payload(receipt_row=receipt_row, public_url=public_url)
    staple = public_key_staple(public_url=public_url)
    pub_b64 = staple.get("public_key_b64")
    receipt_hash = payload.get("receipt_hash")
    canonical = payload.get("canonical_receipt")

    hash_ok = verify_canonical_hash(
        canonical_receipt=canonical if isinstance(canonical, dict) else None,
        receipt_hash=receipt_hash,
    )
    signature_ok = verify_receipt_signature(
        receipt_hash=receipt_hash or "",
        signature_b64=payload.get("receipt_signature"),
        public_key_b64=pub_b64,
    )
    row_fp = payload.get("receipt_public_key_fingerprint")
    staple_fp = staple.get("fingerprint")
    fingerprint_ok = bool(row_fp and staple_fp and row_fp == staple_fp)

    prev_hash = payload.get("prev_receipt_hash")
    if not prev_hash:
        chain_ok = True
        chain_reason = "genesis"
    elif not prev_row:
        chain_ok = False
        chain_reason = "prev_missing"
    else:
        chain_ok = prev_row.get("receipt_hash") == prev_hash
        chain_reason = "linked" if chain_ok else "prev_hash_mismatch"

    inclusion_ok = False
    inclusion_reason = "no_proof"
    if inclusion_bundle and isinstance(inclusion_bundle, dict):
        try:
            from gate import evidence_log as evidence_log_mod
        except ImportError:
            import evidence_log as evidence_log_mod

        inc = inclusion_bundle.get("inclusion") or {}
        head = inclusion_bundle.get("tree_head") or {}
        root = head.get("root_hash") or inc.get("root_hash")
        leaf = inclusion_bundle.get("receipt_hash") or receipt_hash
        if leaf and root:
            inclusion_ok = evidence_log_mod.verify_inclusion(
                leaf_hash=leaf, root_hash=root, proof=inc
            )
            inclusion_reason = "merkle_ok" if inclusion_ok else "merkle_fail"
        else:
            inclusion_reason = "incomplete_proof"

    checks = {
        "hash_ok": hash_ok,
        "signature_ok": signature_ok,
        "fingerprint_ok": fingerprint_ok,
        "chain_ok": chain_ok,
        "inclusion_ok": inclusion_ok,
    }
    all_pass = all(checks.values())
    event_id = payload.get("event_id") or receipt_row.get("id")
    base = (public_url or "").rstrip("/")
    return {
        "spec": "gate-receipt-verify-v1",
        "event_id": event_id,
        "all_pass": all_pass,
        "checks": checks,
        "chain_reason": chain_reason,
        "inclusion_reason": inclusion_reason,
        "decision": payload.get("decision"),
        "state": payload.get("state"),
        "halt": payload.get("halt"),
        "verdict": payload.get("verdict"),
        "receipt_hash": receipt_hash,
        "prev_receipt_hash": prev_hash,
        "receipt_public_key_fingerprint": row_fp,
        "staple_fingerprint": staple_fp,
        "key_present": staple.get("key_present"),
        "their_production": False,
        "receipt_is_not_the_product": True,
        "urls": {
            "receipt": f"{base}/.well-known/receipt/{event_id}.json" if base and event_id else None,
            "proof": f"{base}/.well-known/receipt/{event_id}/proof.json" if base and event_id else None,
            "packet": f"{base}/.well-known/evidence-packet/{event_id}.json" if base and event_id else None,
            "staple": f"{base}/.well-known/receipt-key.json" if base else None,
            "page": f"{base}/receipt/{event_id}" if base and event_id else None,
        },
        "staple": staple,
        "receipt": payload,
    }


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


def signing_required() -> bool:
    """Outside GATE_DEV_MODE, unsigned receipts are a halt — not evidence custody."""
    return os.getenv("GATE_DEV_MODE", "").strip().lower() not in ("1", "true", "yes", "on")


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
        "canonical_receipt_json": <string>,
        "unsigned_halt": True  # when signing required and keys missing
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
    out = {
        "receipt_hash": receipt_hash,
        "receipt_signature": sig,
        "receipt_public_key_fingerprint": receipt_public_key_fingerprint(),
        "prev_receipt_hash": prev_receipt_hash,
        "canonical_receipt_json": canonical_json,
    }
    if signing_required() and not sig:
        out["unsigned_halt"] = True
    return out



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
        # Publish the verifying key on every receipt so one fetch is enough offline.
        "receipt_public_key_b64": receipt_public_key_b64(),
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

    payload = counterfactual_mod.attach_to_receipt_payload(payload, receipt_row)
    if public_url:
        try:
            from gate import inhabitant as inhabitant_mod
        except ImportError:
            import inhabitant as inhabitant_mod
        payload = inhabitant_mod.attach_to_receipt_payload(payload, receipt_row, public_url)
    return payload

