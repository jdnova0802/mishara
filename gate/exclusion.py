"""Proof of exclusion — this job has no redeemed spend leaf.

Inclusion proves a HALT is in the log. Exclusion proves the stronger object:

  job_id has no consumed bind-ticket leaf in the spend map.

A LIVE hop is not spend. Redeem is commit. Sorted Merkle neighbors bound the
missing key (Laurie–Kasper revocation transparency).
"""
from __future__ import annotations

import hashlib
from typing import Any

try:
    from gate import evidence_log as evidence_log_mod
except ImportError:
    import evidence_log as evidence_log_mod

SPEC = "gate-exclusion-v1"


def _leaf_hash(job_id: str) -> str:
    return hashlib.sha256(("gate-spend:" + job_id).encode("utf-8")).hexdigest()


def spent_job_ids(rows: list[dict] | None = None) -> list[str]:
    if rows is None:
        try:
            from gate import db
        except ImportError:
            import db
        return db.consumed_spend_job_ids()
    seen = set()
    out = []
    for r in rows:
        if r.get("acted") is not True:
            continue
        jid = (r.get("job_id") or "").strip()
        if not jid or jid in seen:
            continue
        seen.add(jid)
        out.append(jid)
    out.sort()
    return out


def leaves_for(job_ids: list[str]) -> list[str]:
    return [_leaf_hash(j) for j in job_ids]


def prove(job_id: str, spent_ids: list[str] | None = None) -> dict:
    jid = (job_id or "").strip()
    jobs = list(spent_ids) if spent_ids is not None else spent_job_ids(None)
    leaves = leaves_for(jobs)
    head = evidence_log_mod.signed_tree_head(leaves)
    head["spec"] = "gate-spend-map-v1"
    head["map"] = "redeemed_bind_ticket_job_id"
    if not jid:
        return {
            "spec": SPEC,
            "job_id": None,
            "spent": False,
            "reason": "job_id_required",
            "tree_head": head,
        }
    if jid in jobs:
        idx = jobs.index(jid)
        proof = evidence_log_mod.inclusion_proof(leaves, idx)
        return {
            "spec": SPEC,
            "job_id": jid,
            "spent": True,
            "claim": "redeemed_ticket_leaf_present",
            "leaf_hash": leaves[idx],
            "inclusion": proof,
            "tree_head": head,
            "not_global": "Spend present in Gate's redeemed-ticket map, not a claim about their PAS.",
            "their_production": False,
        }
    i = 0
    while i < len(jobs) and jobs[i] < jid:
        i += 1
    left = None
    right = None
    if i > 0:
        left = {
            "job_id": jobs[i - 1],
            "leaf_hash": leaves[i - 1],
            "inclusion": evidence_log_mod.inclusion_proof(leaves, i - 1),
        }
    if i < len(jobs):
        right = {
            "job_id": jobs[i],
            "leaf_hash": leaves[i],
            "inclusion": evidence_log_mod.inclusion_proof(leaves, i),
        }
    return {
        "spec": SPEC,
        "job_id": jid,
        "spent": False,
        "claim": "no_redeemed_ticket_for_job",
        "neighbors": {"left": left, "right": right},
        "tree_size": len(jobs),
        "tree_head": head,
        "verify": (
            "Confirm left.job_id < job_id < right.job_id (sentinels if missing), "
            "verify both neighbor inclusions against tree_head.root_hash."
        ),
        "not_global": "Proves absence within Gate's redeemed-ticket map, not metaphysical non-occurrence.",
        "winner": None,
        "crown_the_miss": False,
        "their_production": False,
    }


def verify_exclusion(proof: dict) -> bool:
    if proof.get("spent"):
        return False
    head = proof.get("tree_head") or {}
    root = head.get("root_hash")
    neighbors = proof.get("neighbors") or {}
    jid = proof.get("job_id") or ""
    left = neighbors.get("left")
    right = neighbors.get("right")
    if left and not (left.get("job_id") or "") < jid:
        return False
    if right and not jid < (right.get("job_id") or ""):
        return False
    for side in (left, right):
        if not side:
            continue
        inc = side.get("inclusion") or {}
        if not evidence_log_mod.verify_inclusion(
            leaf_hash=side["leaf_hash"],
            root_hash=root,
            proof=inc,
        ):
            return False
    if not left and not right:
        return root == evidence_log_mod.merkle_root([])
    return True


def manifest(public_url: str) -> dict:
    return {
        "spec": SPEC,
        "name": "Spend exclusion proof",
        "greater_than_ed25519": (
            "A signature on a HALT says we said no. An exclusion proof says "
            "no spend leaf for this job exists in the append-only map."
        ),
        "lookup": f"{public_url}/.well-known/exclusion.json?job_id={{job_id}}",
        "lineage": [
            "Laurie–Kasper Revocation Transparency (sorted Merkle non-inclusion)",
            "RFC 9162 Certificate Transparency (inclusion + consistency)",
        ],
        "their_production": False,
    }
