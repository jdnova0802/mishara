"""Append-only Merkle evidence log over receipt hashes (CT-style).

Strangers verify:
1. receipt_hash is included in published tree head (inclusion proof)
2. tree only grew (consistency proof vs prior head — optional client cache)

RFC 9162 algorithms simplified for Gate's flat receipt list.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

SPEC = "gate-evidence-log-v1"
EMPTY_LEAF = hashlib.sha256(b"gate-evidence-empty").digest()


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


def consistency_proof(old_size: int, new_size: int, leaf_hashes_hex: list[str]) -> dict:
    """Minimal consistency: same prefix leaves hash to same subtree root."""
    if old_size > new_size:
        return {"valid": False, "reason": "old_size > new_size"}
    if old_size == 0:
        return {"valid": True, "old_root": merkle_root([]), "new_root": merkle_root(leaf_hashes_hex)}
    old_root = merkle_root(leaf_hashes_hex[:old_size])
    new_root = merkle_root(leaf_hashes_hex)
    return {
        "valid": True,
        "old_size": old_size,
        "new_size": new_size,
        "old_root": old_root,
        "new_root": new_root,
        "append_only": old_size <= new_size,
    }


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
    sig = receipt_mod.sign_receipt_hash(hashlib.sha256(canonical.encode()).hexdigest())
    head["head_signature"] = sig
    head["signed_over"] = "sha256(canonical_head_json)"
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
