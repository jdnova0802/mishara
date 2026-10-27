"""C2SP tlog-witness subset on Gate's evidence head.

The log emits a checkpoint (origin, tree size, base64 root). A witness key
distinct from GATE_RECEIPT_* cosigns it only after the tree is consistent with
the last checkpoint this process stored. That is the C2SP add-checkpoint job:
https://c2sp.org/tlog-witness@v1.1.0

Not a dashboard. Not required for the tree to exist. Independent watchers can
still cache evidence-head.json; this is the signed, offline-checkable form.
"""
from __future__ import annotations

import base64
import json
import os
import time
from typing import Any

try:
    from gate import evidence_log as evidence_log_mod
except ImportError:
    import evidence_log as evidence_log_mod

SPEC = "c2sp.org/tlog-witness@v1.1.0"
DEFAULT_ORIGIN = "gate.velaru.xyz/evidence"


def origin() -> str:
    raw = (os.getenv("GATE_TLOG_ORIGIN") or DEFAULT_ORIGIN).strip()
    return raw or DEFAULT_ORIGIN


def checkpoint_body(*, tree_size: int, root_hash: str, origin_line: str | None = None) -> str:
    origin_line = origin_line or origin()
    root_b64 = base64.b64encode(bytes.fromhex(root_hash)).decode("ascii")
    return f"{origin_line}\n{int(tree_size)}\n{root_b64}\n"


def _state_path() -> str:
    base = os.getenv("GATE_DB_PATH", "").strip()
    if base:
        if base.endswith(".db"):
            return base[:-3] + ".tlog-witness.json"
        return base + ".tlog-witness.json"
    return os.path.join("/tmp", "gate-tlog-witness.json")


def _load_state() -> dict[str, Any]:
    path = _state_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(state: dict[str, Any]) -> None:
    path = _state_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def last_checkpoint(origin_line: str | None = None) -> dict[str, Any] | None:
    row = _load_state().get(origin_line or origin())
    return row if isinstance(row, dict) else None


def sign_checkpoint(checkpoint: str) -> dict[str, Any] | None:
    key = evidence_log_mod._witness_private_key()
    if not key:
        return None
    ts = int(time.time())
    msg = f"{ts}\n{checkpoint}".encode("utf-8")
    sig = base64.b64encode(key.sign(msg)).decode("ascii")
    return {
        "timestamp": ts,
        "signature": sig,
        "signed_over": "ascii timestamp newline + checkpoint body",
        "public_key_b64": evidence_log_mod.witness_public_key_b64(),
        "public_key_fingerprint": evidence_log_mod.witness_public_key_fingerprint(),
    }


def verify_cosignature(*, checkpoint: str, timestamp: int, signature_b64: str) -> bool:
    pub_b = evidence_log_mod.witness_public_key_bytes()
    sig_b = evidence_log_mod._b64decode_raw(signature_b64)
    if not pub_b or not sig_b:
        return False
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        Ed25519PublicKey.from_public_bytes(pub_b).verify(
            sig_b, f"{int(timestamp)}\n{checkpoint}".encode("utf-8")
        )
        return True
    except Exception:
        return False


def attach(head: dict[str, Any]) -> dict[str, Any]:
    """Add a C2SP checkpoint. Cosignature is last add-checkpoint only, not a free sign."""
    tree_size = int(head.get("tree_size") or 0)
    root = (head.get("root_hash") or "").strip()
    body = checkpoint_body(tree_size=tree_size, root_hash=root) if root else ""
    last = last_checkpoint()
    cosig = None
    if (
        last
        and body
        and int(last.get("tree_size") or -1) == tree_size
        and (last.get("root_hash") or "") == root
    ):
        cosig = last.get("cosignature")
        body = last.get("checkpoint") or body
    head["c2sp"] = {
        "spec": SPEC,
        "origin": origin(),
        "checkpoint": body,
        "add_checkpoint": "/v1/evidence-witness/add-checkpoint",
        "cosignature": cosig,
        "note": (
            "Witness cosigns this checkpoint only after add-checkpoint sees a "
            "consistency proof against the last stored size. Distinct from "
            "GATE_RECEIPT_*. Not required for the Merkle tree to exist."
        ),
    }
    return head


def add_checkpoint(
    *,
    leaves: list[str],
    old_size: int,
    old_root: str | None = None,
    origin_line: str | None = None,
) -> dict[str, Any]:
    origin_line = origin_line or origin()
    if not evidence_log_mod.witness_configured():
        return {
            "ok": False,
            "error": "witness_not_configured",
            "spec": SPEC,
            "configured": False,
        }
    proof = evidence_log_mod.consistency_proof(old_size, leaves)
    if proof.get("valid") is not True:
        return {"ok": False, "error": proof.get("reason") or "inconsistent", "spec": SPEC, "proof": proof}
    if old_root and proof.get("old_root") != old_root.lower() and proof.get("old_root") != old_root:
        return {
            "ok": False,
            "error": "old_root_mismatch",
            "spec": SPEC,
            "proof": proof,
        }
    prior = last_checkpoint(origin_line)
    if prior:
        if int(prior.get("tree_size") or 0) != int(old_size):
            return {
                "ok": False,
                "error": "old_size_must_equal_last_checkpoint",
                "last_tree_size": prior.get("tree_size"),
                "old_size": old_size,
                "spec": SPEC,
            }
        if (prior.get("root_hash") or "") != proof.get("old_root"):
            return {
                "ok": False,
                "error": "last_checkpoint_root_mismatch",
                "spec": SPEC,
            }
    new_root = proof["new_root"]
    new_size = proof["new_size"]
    body = checkpoint_body(tree_size=new_size, root_hash=new_root, origin_line=origin_line)
    cosig = sign_checkpoint(body)
    if not cosig:
        return {"ok": False, "error": "witness_sign_failed", "spec": SPEC}
    row = {
        "origin": origin_line,
        "tree_size": new_size,
        "root_hash": new_root,
        "checkpoint": body,
        "cosignature": cosig,
    }
    state = _load_state()
    state[origin_line] = row
    _save_state(state)
    return {"ok": True, "spec": SPEC, **row, "proof": proof}


def manifest(public_url: str = "") -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    last = last_checkpoint()
    return {
        "spec": SPEC,
        "origin": origin(),
        "configured": evidence_log_mod.witness_configured(),
        "add_checkpoint": f"{base}/v1/evidence-witness/add-checkpoint" if base else "/v1/evidence-witness/add-checkpoint",
        "head": f"{base}/.well-known/evidence-head.json" if base else "/.well-known/evidence-head.json",
        "last": last,
        "their_production": False,
    }
