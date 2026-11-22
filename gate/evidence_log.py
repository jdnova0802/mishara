"""Append-only Merkle evidence log over receipt hashes (CT-style).

Strangers verify:
1. receipt_hash is included in published tree head (inclusion proof)
2. tree only grew (consistency proof vs prior head — optional client cache)
3. optional independent witness co-signs the tree head (not Gate's primary key)

RFC 9162-style domain separation (prefixes only):
  leaf node  = SHA-256(0x00 || data)
    inner node = SHA-256(0x01 || left || right)

Tree shape is still Gate pairwise with odd-leaf duplication, not RFC 9162's
unbalanced k = 2^n split. Prefixes close the second-preimage class; do not
claim the tree itself is RFC 9162.
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
MERKLE_ALG = "rfc9162-sha256-domain-separated"
LEGACY_MERKLE_ALG = "gate-sha256-pairwise-v0"
LEAF_PREFIX = b"\x00"
NODE_PREFIX = b"\x01"
EMPTY_LEAF = hashlib.sha256(b"gate-evidence-empty").digest()
PROOF_SCHEME_PLAIN = (
    "RFC 9162-style domain separation (0x00 leaf / 0x01 node prefixes) on a "
    "pairwise odd-leaf tree — not RFC 9162 unbalanced k=2^n"
)
LEGACY_PROOF_SCHEME_PLAIN = (
    "pre-2026-11-22 pairwise SHA-256(left||right) with odd-leaf duplication "
    "and no domain-separation prefixes"
)


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


def witness_separate_operator() -> bool:
    """Human-attested air-gap. Keys in this process are not 'separate' by default."""
    return os.getenv("GATE_WITNESS_SEPARATE_OPERATOR", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def witness_required() -> bool:
    """LIVE on Issuing receipts requires cosign only when a distinct off-box key exists."""
    if not witness_configured() or not witness_separate_operator():
        return False
    w_fp = witness_public_key_fingerprint()
    gate_fp = receipt_mod.receipt_public_key_fingerprint()
    return bool(w_fp and gate_fp and w_fp != gate_fp)


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


def rfc9162_leaf_hash(data: bytes) -> bytes:
    """RFC 9162-style leaf: HASH(0x00 || data). Tree shape is not RFC 9162."""
    return _d(LEAF_PREFIX + data)


def node_hash(left: bytes, right: bytes) -> bytes:
    """RFC 9162-style inner node: HASH(0x01 || left || right)."""
    return _d(NODE_PREFIX + left + right)


def legacy_leaf_hash(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def legacy_node_hash(left: bytes, right: bytes) -> bytes:
    return hashlib.sha256(left + right).digest()


def merkle_root(leaf_hashes_hex: list[str]) -> str:
    if not leaf_hashes_hex:
        return EMPTY_LEAF.hex()
    level = [rfc9162_leaf_hash(_leaf_bytes(h)) for h in leaf_hashes_hex]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            nxt.append(node_hash(left, right))
        level = nxt
    return level[0].hex()


def _tree_levels(leaf_hashes_hex: list[str]) -> list[list[bytes]]:
    if not leaf_hashes_hex:
        return [[EMPTY_LEAF]]
    levels = [[rfc9162_leaf_hash(_leaf_bytes(h)) for h in leaf_hashes_hex]]
    level = levels[0]
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1] if i + 1 < len(level) else left
            nxt.append(node_hash(left, right))
        levels.append(nxt)
        level = nxt
    return levels


def inclusion_proofs(leaf_hashes_hex: list[str]) -> list[dict]:
    """Inclusion proof for every leaf. One tree build, then a sibling path per index."""
    if not leaf_hashes_hex:
        return []
    levels = _tree_levels(leaf_hashes_hex)
    root = levels[-1][0].hex()
    out = []
    for index in range(len(leaf_hashes_hex)):
        siblings = []
        idx = index
        for level in levels[:-1]:
            sib = idx ^ 1
            if sib < len(level):
                siblings.append(level[sib].hex())
            else:
                siblings.append(level[idx].hex())
            idx //= 2
        out.append(
            {
                "index": index,
                "tree_size": len(leaf_hashes_hex),
                "leaf_hash": leaf_hashes_hex[index],
                "siblings": siblings,
                "root_hash": root,
                "merkle_alg": MERKLE_ALG,
            }
        )
    return out


def inclusion_proof(leaf_hashes_hex: list[str], index: int) -> dict:
    """Merkle inclusion proof for leaf at index (0-based)."""
    if not leaf_hashes_hex:
        return {
            "index": 0,
            "tree_size": 0,
            "siblings": [],
            "leaf_hash": EMPTY_LEAF.hex(),
            "merkle_alg": MERKLE_ALG,
        }
    if index < 0 or index >= len(leaf_hashes_hex):
        raise IndexError("leaf index out of range")
    return inclusion_proofs(leaf_hashes_hex)[index]


def _fold_inclusion(leaf_node: bytes, proof: dict, node_fn) -> bytes | None:
    idx = proof.get("index", 0)
    h = leaf_node
    for sib_hex in proof.get("siblings") or []:
        try:
            sib = bytes.fromhex(sib_hex)
        except ValueError:
            return None
        if idx % 2 == 0:
            h = node_fn(h, sib)
        else:
            h = node_fn(sib, h)
        idx //= 2
    return h


def verify_inclusion(*, leaf_hash: str, root_hash: str, proof: dict) -> bool:
    """Accept current RFC 9162-style proofs, or pre-change pairwise proofs.

    leaf_hash is the receipt data hex (preimage), not the 0x00-prefixed node.
    """
    return verify_inclusion_report(
        leaf_hash=leaf_hash, root_hash=root_hash, proof=proof
    )["ok"]


def verify_inclusion_report(*, leaf_hash: str, root_hash: str, proof: dict) -> dict:
    """Same check as verify_inclusion, with a stranger-readable scheme note."""
    try:
        data = _leaf_bytes(leaf_hash)
    except ValueError:
        return {
            "ok": False,
            "scheme": None,
            "predates_current_proof_scheme": False,
            "reason": "leaf_hash_not_hex",
            "proof_scheme_plain": "leaf hash is not hex",
        }
    current = _fold_inclusion(rfc9162_leaf_hash(data), proof, node_hash)
    if current is not None and current.hex() == root_hash:
        return {
            "ok": True,
            "scheme": MERKLE_ALG,
            "predates_current_proof_scheme": False,
            "reason": None,
            "proof_scheme_plain": PROOF_SCHEME_PLAIN,
        }
    legacy = _fold_inclusion(legacy_leaf_hash(data), proof, legacy_node_hash)
    if legacy is not None and legacy.hex() == root_hash:
        return {
            "ok": True,
            "scheme": LEGACY_MERKLE_ALG,
            "predates_current_proof_scheme": True,
            "reason": None,
            "proof_scheme_plain": LEGACY_PROOF_SCHEME_PLAIN,
        }
    return {
        "ok": False,
        "scheme": None,
        "predates_current_proof_scheme": True,
        "reason": "inclusion_mismatch_current_and_legacy",
        "proof_scheme_plain": (
            "this receipt predates the current proof scheme, or the inclusion "
            "path does not match either the RFC 9162-style domain-separated "
            "tree or the pre-2026-11-22 pairwise tree"
        ),
    }


def consistency_proof(old_size: int, leaf_hashes_hex: list[str]) -> dict:
    """Append-only check: old tree is the prefix of the new tree."""
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
        "merkle_alg": MERKLE_ALG,
        "proof_scheme_plain": PROOF_SCHEME_PLAIN,
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
        "required": witness_required(),
        "separate_operator": witness_separate_operator(),
        "plain": (
            "Cosign capacity on GATE_WITNESS_*. required=true only when "
            "GATE_WITNESS_SEPARATE_OPERATOR=1 and the witness fingerprint is "
            "distinct from GATE_RECEIPT_*. Same-process keys are not independent. "
            "Do not treat this block as an independent witness until required is true."
        ),
    }
    try:
        from gate import tlog_witness as tlog_witness_mod
    except ImportError:
        import tlog_witness as tlog_witness_mod
    return tlog_witness_mod.attach(head)


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
        "merkle_alg": MERKLE_ALG,
        "proof_scheme_plain": PROOF_SCHEME_PLAIN,
        "predates_current_proof_scheme": False,
        "inclusion": proof,
        "tree_head": head,
        "verify_inclusion": (
            "Recompute root from leaf_hash + siblings under the current "
            "RFC 9162-style prefixes, or the pre-2026-11-22 pairwise fallback; "
            "compare to tree_head.root_hash"
        ),
    }
