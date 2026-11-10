"""Item 150 — RFC 9162-shaped transparency log over receipt hashes.

Wraps the existing Merkle evidence log. Inclusion and consistency do not
close split-view; that needs gossip from an outside party, not Nisaba.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import evidence_log as evidence_log_mod
except ImportError:
    import evidence_log as evidence_log_mod

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-transparency-log-v1"
RFC = "9162"
SELF_OPERATORS = ("nisaba", "gate", "velaru", "self", "internal", "localhost")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_TLOG_PATH") or Path(__file__).resolve().parent / "data" / "tlog.json")


def _load() -> dict[str, Any]:
    path = _path()
    empty = {"spec": SPEC, "trees": [], "inclusions": [], "consistencies": [], "gossip": []}
    if not path.exists():
        return empty
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return empty
    if not isinstance(data, dict):
        return empty
    for key in ("trees", "inclusions", "consistencies", "gossip"):
        data.setdefault(key, [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def _hashes(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    out: list[str] = []
    for x in raw:
        s = str(x).strip().lower()
        if s and s not in out:
            out.append(s)
    return out


def list_trees() -> list[dict[str, Any]]:
    return list(_load().get("trees") or [])


def list_gossip() -> list[dict[str, Any]]:
    return list(_load().get("gossip") or [])


def _tree(tree_id: str) -> dict[str, Any] | None:
    tid = (tree_id or "").strip()
    return next((t for t in list_trees() if t.get("tree_id") == tid), None)


def snapshot(*, receipt_hashes: Any) -> dict[str, Any]:
    leaves = _hashes(receipt_hashes)
    if not leaves:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "leaves_required",
            "plain": "A tree with no receipt hashes is not a ledger. Pass the hashes that already exist.",
        }
    root = evidence_log_mod.merkle_root(leaves)
    rec = {
        "spec": SPEC,
        "ok": True,
        "rfc": RFC,
        "tree_id": "tlog_" + uuid.uuid4().hex[:12],
        "root_hash": root,
        "tree_size": len(leaves),
        "leaves": leaves,
        "signed_at": _iso(),
        "signature": None,
        "signing_key_note": "Item 142: GATE_RECEIPT_PRIVATE_KEY is still single_admin / online. This snapshot does not rotate it.",
        "plain": "Signed tree head shape. Inclusion/consistency do not prove two verifiers saw the same history.",
    }
    store = _load()
    store["trees"].append(rec)
    _save(store)
    return rec


def prove_inclusion(*, tree_id: str, receipt_id: str) -> dict[str, Any]:
    tree = _tree(tree_id)
    if not tree:
        return {"spec": SPEC, "ok": False, "error": "tree_not_found", "plain": "Unknown tree_id."}
    rid = (receipt_id or "").strip().lower()
    leaves = list(tree.get("leaves") or [])
    try:
        idx = leaves.index(rid)
    except ValueError:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "leaf_not_in_tree",
            "plain": "That receipt hash is not a leaf of this tree. Deletion would fail this check.",
        }
    proof = evidence_log_mod.inclusion_proof(leaves, idx)
    rec = {
        "spec": SPEC,
        "ok": True,
        "proof_id": "inc_" + uuid.uuid4().hex[:12],
        "receipt_id": rid,
        "tree_id": tree["tree_id"],
        "audit_path": proof.get("siblings") or [],
        "index": proof.get("index"),
        "verified": evidence_log_mod.verify_inclusion(
            leaf_hash=rid, root_hash=tree["root_hash"], proof=proof
        ),
        "verified_at": _iso(),
        "plain": "Inclusion against this root. Split-view is outside RFC 9162 inclusion.",
    }
    store = _load()
    store["inclusions"].append(rec)
    _save(store)
    return rec


def prove_consistency(*, old_tree_id: str, new_tree_id: str) -> dict[str, Any]:
    old = _tree(old_tree_id)
    new = _tree(new_tree_id)
    if not old or not new:
        return {"spec": SPEC, "ok": False, "error": "tree_not_found", "plain": "Need two real tree ids."}
    old_leaves = list(old.get("leaves") or [])
    new_leaves = list(new.get("leaves") or [])
    prefix = new_leaves[: len(old_leaves)] == old_leaves
    proof = evidence_log_mod.consistency_proof(len(old_leaves), new_leaves)
    rec = {
        "spec": SPEC,
        "ok": True,
        "proof_id": "con_" + uuid.uuid4().hex[:12],
        "old_tree_id": old["tree_id"],
        "new_tree_id": new["tree_id"],
        "audit_path": [old["root_hash"], new["root_hash"]],
        "old_root": proof.get("old_root"),
        "new_root": proof.get("new_root"),
        "prefix": prefix,
        "verified": bool(prefix and proof.get("valid") and proof.get("old_root") == old["root_hash"]),
        "verified_at": _iso(),
        "plain": (
            "New tree contains the old tree as a prefix."
            if prefix
            else "Consistency failed. A rewrite or deletion would look like this."
        ),
    }
    store = _load()
    store["consistencies"].append(rec)
    _save(store)
    return rec


def gossip(
    *,
    tree_id: str,
    observed_root_hash: str,
    observed_by: str,
) -> dict[str, Any]:
    who = sanitize_mod.strip_agent(observed_by, limit=120).strip()
    if not who:
        return {"spec": SPEC, "ok": False, "error": "observer_required", "plain": "Gossip needs an outside party."}
    if any(token == who.lower() or token in who.lower() for token in SELF_OPERATORS):
        return {
            "spec": SPEC,
            "ok": False,
            "error": "outside_party_required",
            "plain": "RFC 9162 split-view is outside inclusion/consistency. A Nisaba-run mirror is not gossip.",
        }
    tree = _tree(tree_id)
    if not tree:
        return {"spec": SPEC, "ok": False, "error": "tree_not_found", "plain": "Unknown tree_id."}
    seen = (observed_root_hash or "").strip().lower()
    if not seen:
        return {"spec": SPEC, "ok": False, "error": "root_required", "plain": "Need the root this verifier independently saw."}
    rec = {
        "spec": SPEC,
        "ok": True,
        "record_id": "gsp_" + uuid.uuid4().hex[:12],
        "tree_id": tree["tree_id"],
        "observed_root_hash": seen,
        "observed_by": who,
        "observed_at": _iso(),
        "matches_published_root": seen == tree["root_hash"],
        "plain": (
            "Gossip matches the published root."
            if seen == tree["root_hash"]
            else "Split-view signal: this outsider saw a different root than the log operator published."
        ),
    }
    store = _load()
    store["gossip"].append(rec)
    _save(store)
    return rec
