"""Counterfactual Spend Receipt — cryptographic proof of non-spend.

Not global absence. Scoped negative attestation:

  Within observation boundary B, forbidden transition T did not execute
  at the moment Gate evaluated the hop.

Lineage (public, not invented here):
- Haber–Stornetta linked timestamping (1991) — hash-chained commitments
- Certificate Transparency (RFC 9162) — Merkle inclusion + consistency proofs
- Proof-of-Behavior (IETF draft) — DENIED recorded before execution
- Counterfactual receipts / evidentiary absence (2025–2026 regulatory filings)
- MA-Commit / monotonic accountability (2026) — permission to spend cannot be
  retroactively reinterpreted; CHARGE-only resurrection is the only regime change

Gate applies this to irreversible commercial spend: bind-only is already Bound.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-counterfactual-spend-v1"
FORBIDDEN_BIND = [
    {"method": "POST", "path": "/job/v1/jobs/{job_id}/bind-only", "spend": "bind"},
    {"method": "POST", "path": "/job/v1/jobs/{job_id}/bind-and-issue", "spend": "bind_and_issue"},
    {"method": "POST", "path": "/policy/v1/policies/{policy_id}/issue", "spend": "issue"},
]

MONOTONIC_ACCOUNTABILITY = (
    "UW approve without CHARGE does not resurrect. "
    "Permission that justified a past bind cannot be retroactively shrunk for that job."
)


def forbidden_for_job(job_id: str | None, policy_id: str | None = None) -> list[dict]:
    jid = (job_id or "").strip() or "JOB_ID"
    pid = (policy_id or "").strip() or "POLICY_ID"
    out = []
    for t in FORBIDDEN_BIND:
        path = t["path"].format(job_id=jid, policy_id=pid)
        out.append({"method": t["method"], "path": path, "spend": t["spend"]})
    return out


def is_counterfactual(*, decision: str | None, acted: bool | None) -> bool:
    if acted is True:
        return False
    return (decision or "").upper() in ("HALT", "BLOCK")


def build_claim(
    *,
    event_id: str,
    fuse_id: str,
    job_id: str | None,
    decision: str,
    verify_url: str | None,
    created_at: str,
    receipt_hash: str | None,
    boundary: dict | None = None,
) -> dict:
    """Type I counterfactual: proof of inaction on forbidden spend transitions."""
    b = boundary or {}
    return {
        "spec": SPEC,
        "type": "INACTION",
        "claim": "forbidden_spend_did_not_execute_within_boundary",
        "event_id": event_id,
        "fuse_id": fuse_id,
        "job_id": job_id,
        "decision": decision,
        "forbidden_transitions": forbidden_for_job(job_id),
        "boundary": {
            "observation": "pre_bind_hop_before_PAS_write",
            "fail_closed": True,
            "exclusive_door_honored_if_welded": b.get("exclusive_door_honored_if_welded", True),
            "their_production": False,
        },
        "monotonic_accountability": MONOTONIC_ACCOUNTABILITY,
        "verify_url": verify_url,
        "receipt_hash": receipt_hash,
        "created_at": created_at,
        "not_global": "Proves absence within Gate's boundary B, not metaphysical non-occurrence.",
        "winner": None,
        "crown_the_miss": False,
    }


def attach_to_receipt_payload(payload: dict, row: dict) -> dict:
    if not is_counterfactual(decision=row.get("decision"), acted=row.get("acted")):
        payload["counterfactual_spend"] = None
        return payload
    payload["counterfactual_spend"] = build_claim(
        event_id=row.get("id"),
        fuse_id=row.get("fuse_id"),
        job_id=row.get("job_id"),
        decision=row.get("decision"),
        verify_url=row.get("verify_url"),
        created_at=row.get("created_at"),
        receipt_hash=row.get("receipt_hash"),
    )
    return payload


def manifest(public_url: str) -> dict:
    return {
        "spec": SPEC,
        "name": "Counterfactual Spend Receipt",
        "problem": "Logs prove what happened. Courts and carriers need proof of what did not happen.",
        "solution": (
            "Pre-execution hop mints a signed receipt that forbidden bind/issue transitions "
            "were evaluated and not permitted within boundary B."
        ),
        "types": {
            "INACTION": "forbidden spend transition did not execute (HALT/BLOCK on bind path)",
        },
        "monotonic_accountability": MONOTONIC_ACCOUNTABILITY,
        "forbidden_template": FORBIDDEN_BIND,
        "evidence_log": f"{public_url}/.well-known/evidence-head.json",
        "receipt": f"{public_url}/.well-known/receipt/{{event_id}}.json",
        "inclusion_proof": f"{public_url}/.well-known/receipt/{{event_id}}/proof.json",
        "lineage": [
            "Haber–Stornetta linked timestamping (1991)",
            "RFC 9162 Certificate Transparency Merkle proofs",
            "IETF draft Proof-of-Behavior (pre-execution DENIED)",
            "Counterfactual receipts / proving what didn't happen (2025–2026)",
            "MA-Commit monotonic accountability for irreversible execution (2026)",
        ],
        "not_in_contest": "Someone's irreversible that did occur — the climb is luxury.",
        "their_production": False,
        "page": f"{public_url}/capture",
    }
