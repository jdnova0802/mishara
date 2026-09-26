"""Append-only Merkle evidence log over receipt hashes (CT-style).

Strangers verify:
1. receipt_hash is included in published tree head (inclusion proof)
2. tree only grew (consistency proof vs prior head — optional client cache)
3. optional independent witness co-signs the tree head (not Gate's primary key)

RFC 9162 algorithms simplified for Gate's flat receipt list.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

SPEC = "gate-evidence-log-v1"
WITNESS_SPEC = "gate-evidence-witness-v1"
EMPTY_LEAF = hashlib.sha256(b"gate-evidence-empty").digest()


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


def _witness_private_key():
    """Independent witness key — air-gapped from GATE_RECEIPT_PRIVATE_KEY.

    Env:
      GATE_WITNESS_PRIVATE_KEY — base64(raw 32-byte Ed25519 private key)
      GATE_WITNESS_PUBLIC_KEY  — base64(raw 32-byte Ed25519 public key)
    """
    priv_b = _b64decode_raw(os.getenv("GATE_WITNESS_PRIVATE_KEY"))
    if not priv_b:
        return None
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

        return Ed25519PrivateKey.from_private_bytes(priv_b)
    except Exception:
        return None


def witness_public_key_bytes() -> bytes | None:
    pub_b = _b64decode_raw(os.getenv("GATE_WITNESS_PUBLIC_KEY"))
    if pub_b:
        return pub_b
    key = _witness_private_key()
    if not key:
        return None
    try:
        from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

        return key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    except Exception:
        return None


def witness_public_key_fingerprint() -> str | None:
    pub_b = witness_public_key_bytes()
    if not pub_b:
        return None
    return hashlib.sha256(pub_b).hexdigest()[:16]


def witness_public_key_b64() -> str | None:
    pub_b = witness_public_key_bytes()
    if not pub_b:
        return None
    return _b64encode_raw(pub_b)


def witness_configured() -> bool:
    return bool(witness_public_key_bytes())


def _sign_witness(head_hash_hex: str) -> str | None:
    key = _witness_private_key()
    if not key:
        return None
    try:
        return _b64encode_raw(key.sign(head_hash_hex.encode("utf-8")))
    except Exception:
        return None


def verify_witness_signature(*, head_hash: str, signature_b64: str | None) -> bool:
    if not head_hash or not signature_b64:
        return False
    pub_b = witness_public_key_bytes()
    sig_b = _b64decode_raw(signature_b64)
    if not pub_b or not sig_b:
        return False
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        Ed25519PublicKey.from_public_bytes(pub_b).verify(sig_b, head_hash.encode("utf-8"))
        return True
    except Exception:
        return False


def _d(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def _leaf_bytes(receipt_hash_hex: str) -> bytes:
    return bytes.fromhex(receipt_hash_hex)


def merkle_root(leaf_hashes_hex: list[str]) -> str:
    if not leaf_hashes_hex:
        return EMPTY_LEAF.hex()
    level = [_leaf_bytes(h) for h in leaf_hashes_hex]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            nxt.append(_d(left + right))
        level = nxt
    return level[0].hex()


def _tree_levels(leaf_hashes_hex: list[str]) -> list[list[bytes]]:
    if not leaf_hashes_hex:
        return [[EMPTY_LEAF]]
    levels = [[_leaf_bytes(h) for h in leaf_hashes_hex]]
    level = levels[0]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            nxt.append(_d(left + right))
        levels.append(nxt)
        level = nxt
    return levels


def inclusion_proof(leaf_hashes_hex: list[str], index: int) -> dict:
    """Merkle inclusion proof for leaf at index (0-based)."""
    if not leaf_hashes_hex:
        return {"index": 0, "tree_size": 0, "siblings": [], "leaf_hash": EMPTY_LEAF.hex()}
    if index < 0 or index >= len(leaf_hashes_hex):
        raise IndexError("leaf index out of range")
    levels = _tree_levels(leaf_hashes_hex)
    siblings = []
    idx = index
    for level in levels[:-1]:
        sib = idx ^ 1
        if sib < len(level):
            siblings.append(level[sib].hex())
        else:
            siblings.append(level[idx].hex())
        idx //= 2
    return {
        "index": index,
        "tree_size": len(leaf_hashes_hex),
        "leaf_hash": leaf_hashes_hex[index],
        "siblings": siblings,
        "root_hash": levels[-1][0].hex(),
    }


def verify_inclusion(*, leaf_hash: str, root_hash: str, proof: dict) -> bool:
    h = bytes.fromhex(leaf_hash)
    idx = proof.get("index", 0)
    for sib_hex in proof.get("siblings") or []:
        sib = bytes.fromhex(sib_hex)
        if idx % 2 == 0:
            h = _d(h + sib)
        else:
            h = _d(sib + h)
        idx //= 2
    return h.hex() == root_hash


def consistency_proof(old_size: int, leaf_hashes_hex: list[str]) -> dict:
    """RFC 9162-shaped append-only check: old tree is the prefix of the new tree."""
    n = len(leaf_hashes_hex)
    if old_size < 0 or old_size > n:
        return {
            "spec": "gate-evidence-consistency-v1",
            "valid": False,
            "reason": "old_size_out_of_range",
            "old_size": old_size,
            "new_size": n,
        }
    old_root = merkle_root(leaf_hashes_hex[:old_size])
    new_root = merkle_root(leaf_hashes_hex)
    return {
        "spec": "gate-evidence-consistency-v1",
        "valid": True,
        "old_size": old_size,
        "new_size": n,
        "old_root": old_root,
        "new_root": new_root,
        "append_only": True,
        "verify": "old_root == merkle(leaves[:old_size]) AND new_root == merkle(leaves)",
    }


def verify_consistency(*, old_size: int, old_root: str, new_root: str, leaf_hashes_hex: list[str]) -> bool:
    proof = consistency_proof(old_size, leaf_hashes_hex)
    return (
        proof.get("valid") is True
        and proof.get("old_root") == old_root
        and proof.get("new_root") == new_root
    )


def signed_tree_head(leaf_hashes_hex: list[str]) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    root = merkle_root(leaf_hashes_hex)
    head = {
        "spec": SPEC,
        "tree_size": len(leaf_hashes_hex),
        "root_hash": root,
        "timestamp": now,
        "public_key_fingerprint": receipt_mod.receipt_public_key_fingerprint(),
    }
    canonical = json.dumps(head, sort_keys=True, separators=(",", ":"))
    head_hash = hashlib.sha256(canonical.encode()).hexdigest()
    sig = receipt_mod.sign_receipt_hash(head_hash)
    head["head_signature"] = sig
    head["signed_over"] = "sha256(canonical_head_json)"
    head["head_hash"] = head_hash

    # Witness co-sign capacity: second independent key over the same head_hash.
    # Capability exists even when the witness key is not yet configured — strangers
    # see witness.configured false rather than an implied single-party forever.
    w_fp = witness_public_key_fingerprint()
    w_sig = _sign_witness(head_hash) if w_fp else None
    gate_fp = receipt_mod.receipt_public_key_fingerprint()
    distinct = bool(w_fp and gate_fp and w_fp != gate_fp)
    head["witness"] = {
        "spec": WITNESS_SPEC,
        "configured": witness_configured(),
        "signed": bool(w_sig),
        "distinct_from_gate_key": distinct if w_fp else None,
        "public_key_fingerprint": w_fp,
        "public_key_b64": witness_public_key_b64(),
        "signature": w_sig,
        "signed_over": "same head_hash as head_signature",
        "required": False,
        "plain": (
            "Independent co-sign of the periodic tree head — not Gate's primary "
            "receipt key. Air-gap GATE_WITNESS_* from GATE_RECEIPT_*. "
            "Consortium partner optional; capacity is infrastructure now."
        ),
    }
    return head


def log_from_rows(rows: list[dict]) -> list[str]:
    """Ordered receipt hashes for Merkle tree (created_at ascending)."""
    ordered = sorted(
        [r for r in rows if r.get("receipt_hash")],
        key=lambda r: (r.get("created_at") or "", r.get("id") or ""),
    )
    return [r["receipt_hash"] for r in ordered]


def proof_bundle(rows: list[dict], event_id: str) -> dict | None:
    by_id = {r["id"]: r for r in rows if r.get("id")}
    row = by_id.get(event_id)
    if not row or not row.get("receipt_hash"):
        return None
    leaves = log_from_rows(rows)
    try:
        idx = next(i for i, h in enumerate(leaves) if h == row["receipt_hash"])
    except StopIteration:
        return None
    proof = inclusion_proof(leaves, idx)
    head = signed_tree_head(leaves)
    return {
        "spec": "gate-evidence-proof-v1",
        "event_id": event_id,
        "receipt_hash": row["receipt_hash"],
        "inclusion": proof,
        "tree_head": head,
        "verify_inclusion": "Recompute root from leaf_hash + siblings; compare to tree_head.root_hash",
    }
