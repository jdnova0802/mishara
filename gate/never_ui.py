"""Human-facing NEVER / SPENT over spend exclusion proofs.

Apple-simple words. Laurie–Kasper sorted Merkle non-inclusion underneath.
"""

from __future__ import annotations

from typing import Any

try:
    from gate import exclusion as exclusion_mod
except ImportError:
    import exclusion as exclusion_mod

SPEC = "gate-never-v1"


def clear_job(job_id: str) -> dict[str, Any]:
    jid = (job_id or "").strip()
    if not jid:
        return {
            "spec": SPEC,
            "word": "MISSING",
            "plain": "Paste a job id.",
            "their_production": False,
        }
    proof = exclusion_mod.prove(jid)
    spent = bool(proof.get("spent"))
    verified = (
        True
        if spent
        else exclusion_mod.verify_exclusion(proof)
    )
    if spent:
        word = "SPENT"
        plain = "A redeemed ticket leaf is on the spend map for this job."
    elif verified:
        word = "NEVER"
        plain = "No redeemed spend leaf for this job — neighbors bound the gap."
    else:
        word = "BROKEN"
        plain = "Exclusion proof did not verify. Treat as uncertain — fail closed."
    return {
        "spec": SPEC,
        "job_id": jid,
        "word": word,
        "plain": plain,
        "spent": spent,
        "verified": verified,
        "tree_size": (proof.get("tree_head") or {}).get("tree_size")
        or proof.get("tree_size"),
        "claim": proof.get("claim"),
        "atoms": {
            "exclusion": f"/.well-known/exclusion.json?job_id={jid}",
        },
        "their_production": False,
        "not_global": proof.get("not_global"),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Never",
        "promise": "Has this job already spent through the exclusive door?",
        "words": ["NEVER", "SPENT", "BROKEN", "MISSING"],
        "page": f"{base}/never",
        "api": f"{base}/v1/never",
        "atoms": [
            "Sorted Merkle non-inclusion (Laurie–Kasper)",
            "Redeemed bind-ticket spend map",
        ],
        "lookup": f"{base}/.well-known/exclusion.json?job_id={{job_id}}",
        "their_production": False,
    }
