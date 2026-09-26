"""Human-facing NEVER / SPENT over spend exclusion proofs.

Apple-simple words. Laurie–Kasper sorted Merkle non-inclusion underneath.
claim_scope + write_state are first-class on every response.
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
    phase = (proof.get("spend_phase") or (proof.get("write_state") or {}).get("phase") or "ABSENT")
    if spent:
        word = "SPENT"
        plain = "A redeemed ticket leaf is on the spend map for this job."
    elif not verified:
        word = "BROKEN"
        plain = "Exclusion proof did not verify. Treat as uncertain — fail closed."
    elif phase == "IN_FLIGHT":
        word = "NEVER"
        plain = (
            "No redeemed spend leaf — neighbors bound the gap. "
            "IN_FLIGHT: an unconsumed ticket still exists; it may redeem or expire. "
            "This Never is weaker than an ABSENT Never."
        )
    else:
        word = "NEVER"
        plain = "No redeemed spend leaf for this job — neighbors bound the gap."
    out = {
        "spec": SPEC,
        "job_id": jid,
        "word": word,
        "plain": plain,
        "spent": spent,
        "verified": verified,
        "tree_size": (proof.get("tree_head") or {}).get("tree_size")
        or proof.get("tree_size"),
        "claim": proof.get("claim"),
        "claim_scope": proof.get("claim_scope"),
        "signed_claim": proof.get("signed_claim"),
        "write_state": proof.get("write_state"),
        "spend_phase": phase,
        "in_flight": bool(proof.get("in_flight")),
        "atoms": {
            "exclusion": f"/.well-known/exclusion.json?job_id={jid}",
        },
        "their_production": False,
        "not_global": proof.get("not_global"),
    }
    return out


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
            "Signed claim_scope (boundary of the Never)",
            "IN_FLIGHT vs ABSENT spend_phase",
        ],
        "lookup": f"{base}/.well-known/exclusion.json?job_id={{job_id}}",
        "their_production": False,
    }
