"""R3 — key transparency for the signer, not the subject.

CONIKS-shaped directory of *which* Ed25519 fingerprint is current for
receipt signing. Two different fingerprints in the same epoch are
equivocation evidence. Does not rotate 142. Does not claim an HSM.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import evidence_log as evidence_log_mod
except ImportError:
    import evidence_log as evidence_log_mod

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-key-transparency-v1"


def _iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_KEYDIR_PATH") or Path(__file__).resolve().parent / "data" / "key_transparency.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "entries": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "entries": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "entries": []}
    data.setdefault("entries", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def _leaf(entry: dict[str, Any]) -> str:
    blob = json.dumps(
        {
            "epoch": entry.get("epoch"),
            "fingerprint": entry.get("fingerprint"),
            "purpose": entry.get("purpose"),
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode()).hexdigest()


def catalog() -> dict[str, Any]:
    store = _load()
    leaves = [_leaf(e) for e in store["entries"]]
    return {
        "spec": SPEC,
        "hsm": False,
        "quorum": False,
        "single_admin": True,
        "current": current(),
        "entries": store["entries"],
        "directory_root": evidence_log_mod.merkle_root(leaves) if leaves else evidence_log_mod.EMPTY_LEAF.hex(),
        "plain": "Directory of signing fingerprints in a Merkle tree. Equivocation is two fingerprints for one epoch.",
    }


def publish(*, epoch: str, fingerprint: str | None = None, purpose: str = "receipt_signing") -> dict[str, Any]:
    ep = sanitize_mod.strip_agent(epoch, limit=80)
    fp = (fingerprint or receipt_mod.receipt_public_key_fingerprint() or "").strip()
    if not ep:
        return {"spec": SPEC, "ok": False, "error": "epoch_required"}
    if not fp:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "no_signing_fingerprint",
            "plain": "Nothing to publish. GATE_RECEIPT_PRIVATE_KEY is still the 142 gap.",
        }
    rec = {
        "spec": SPEC,
        "ok": True,
        "epoch": ep,
        "fingerprint": fp,
        "purpose": (purpose or "receipt_signing").strip(),
        "published_at": _iso(),
        "leaf_hash": "",
    }
    rec["leaf_hash"] = _leaf(rec)
    store = _load()
    store["entries"].append(rec)
    _save(store)
    return rec


def current() -> dict[str, Any] | None:
    rows = _load()["entries"]
    if not rows:
        live = receipt_mod.receipt_public_key_fingerprint()
        if not live:
            return None
        return {"fingerprint": live, "epoch": None, "unpublished": True}
    return dict(rows[-1])


def equivocation() -> dict[str, Any]:
    by_epoch: dict[str, set[str]] = {}
    for e in _load()["entries"]:
        by_epoch.setdefault(str(e.get("epoch")), set()).add(str(e.get("fingerprint")))
    clashes = {ep: sorted(fps) for ep, fps in by_epoch.items() if len(fps) > 1}
    return {
        "spec": SPEC,
        "ok": True,
        "equivocation": bool(clashes),
        "clashes": clashes,
        "plain": (
            "Two fingerprints for one epoch. That is split-view on the signer, not on a receipt."
            if clashes
            else "No equivocation in this directory. A missing second watcher still cannot catch a split-view of the log."
        ),
    }


def prove_inclusion(*, fingerprint: str) -> dict[str, Any]:
    fp = (fingerprint or "").strip()
    store = _load()
    leaves = [_leaf(e) for e in store["entries"]]
    idx = next((i for i, e in enumerate(store["entries"]) if e.get("fingerprint") == fp), None)
    if idx is None:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "fingerprint_not_in_directory",
            "plain": "No leaf for this fingerprint. Absence of a leaf is not proof of a different signer.",
        }
    proof = evidence_log_mod.inclusion_proof(leaves, idx)
    root = evidence_log_mod.merkle_root(leaves)
    return {
        "spec": SPEC,
        "ok": True,
        "fingerprint": fp,
        "entry": store["entries"][idx],
        "proof": proof,
        "directory_root": root,
        "verified": evidence_log_mod.verify_inclusion(leaf_hash=leaves[idx], root_hash=root, proof=proof),
        "hsm": False,
        "plain": "This fingerprint is in the directory tree. It is not an HSM attestation.",
    }


def prove_absence(*, epoch: str, fingerprint: str) -> dict[str, Any]:
    ep = (epoch or "").strip()
    fp = (fingerprint or "").strip()
    in_epoch = [e for e in _load()["entries"] if str(e.get("epoch")) == ep]
    present = any(e.get("fingerprint") == fp for e in in_epoch)
    return {
        "spec": SPEC,
        "ok": True,
        "absent": not present,
        "epoch": ep,
        "fingerprint": fp,
        "epoch_entry_count": len(in_epoch),
        "plain": (
            "This fingerprint was not published in that epoch. Re-scan the directory."
            if not present
            else "This fingerprint sits in that epoch. Absence fails."
        ),
    }
