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
        "types": ["INACTION", "PATH"],
        "claim": "forbidden_spend_did_not_execute_within_boundary",
        "event_id": event_id,
        "fuse_id": fuse_id,
        "job_id": job_id,
        "decision": decision,
        "forbidden_transitions": forbidden_for_job(job_id),
        "represented_paths_not_selected": forbidden_for_job(job_id),
        "path": {
            "type": "PATH",
            "claim": "bind_spend_writes_were_represented_and_not_selected",
        },
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


def attach_to_receipt_payload(payload: dict, row: dict, public_url: str | None = None) -> dict:
    try:
        from gate import possibility as possibility_mod
    except ImportError:
        import possibility as possibility_mod
    try:
        from gate import constitution as constitution_mod
    except ImportError:
        import constitution as constitution_mod

    spend = None
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    if isinstance(hop.get("spend_write"), dict):
        spend = hop["spend_write"].get("spend_kind")
    payload["policy_depth"] = possibility_mod.evaluate_policies(
        decision=row.get("decision"),
        acted=row.get("acted"),
        job_id=row.get("job_id"),
        selected_spend=spend,
    )
    # Proprietary Mouth Constitution: intervention ladder + counts-as status.
    payload = constitution_mod.attach_to_receipt_payload(payload, row)
    try:
        from gate import bayesian_binding as bayesian_mod
    except ImportError:
        import bayesian_binding as bayesian_mod
    try:
        from gate import temporal_weld as temporal_mod
    except ImportError:
        import temporal_weld as temporal_mod
    try:
        from gate import fulfillment as fulfillment_mod
    except ImportError:
        import fulfillment as fulfillment_mod

    payload = bayesian_mod.attach_to_receipt_payload(payload, row)
    payload = temporal_mod.attach_to_receipt_payload(payload, row)
    hop_for_fulfill = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    payload["fulfillment"] = fulfillment_mod.from_hop(
        hop_for_fulfill, decision=row.get("decision"), acted=row.get("acted")
    )
    try:
        from gate import nonrepudiation as nr_mod
    except ImportError:
        import nonrepudiation as nr_mod
    try:
        from gate import custody as custody_mod
    except ImportError:
        import custody as custody_mod
    try:
        from gate import option_halt as option_mod
    except ImportError:
        import option_halt as option_mod
    try:
        from gate import performative as performative_mod
    except ImportError:
        import performative as performative_mod

    payload = nr_mod.attach_to_receipt_payload(payload, row)
    payload = option_mod.attach_to_receipt_payload(payload, row)
    payload = performative_mod.attach_to_receipt_payload(payload, row)
    payload = custody_mod.attach_to_receipt_payload(payload, row, public_url)
    try:
        from gate import hyperobject as hyperobject_mod
    except ImportError:
        import hyperobject as hyperobject_mod
    try:
        from gate import complementarity as complementarity_mod
    except ImportError:
        import complementarity as complementarity_mod
    try:
        from gate import irreversibility as irreversibility_mod
    except ImportError:
        import irreversibility as irreversibility_mod
    try:
        from gate import semiotics as semiotics_mod
    except ImportError:
        import semiotics as semiotics_mod
    try:
        from gate import antifragile as antifragile_mod
    except ImportError:
        import antifragile as antifragile_mod

    payload = hyperobject_mod.attach_to_receipt_payload(payload, row)
    # status-shaped attachments use decision as mouth status when present
    status_row = {
        **row,
        "status": (
            "CHARGE"
            if str(row.get("decision") or "").upper() == "ALLOW" and row.get("acted")
            else str(row.get("decision") or "").upper()
        ),
    }
    payload["complementarity"] = complementarity_mod.attach_to_receipt_payload(status_row)
    payload["irreversibility_horizon"] = irreversibility_mod.attach_to_receipt_payload(status_row)
    payload["semiotics"] = semiotics_mod.attach_to_receipt_payload(status_row)
    payload["antifragile_halt"] = antifragile_mod.attach_to_receipt_payload(status_row)

    if not is_counterfactual(decision=row.get("decision"), acted=row.get("acted")):
        payload["counterfactual_spend"] = None
        return payload
    claim = build_claim(
        event_id=row.get("id"),
        fuse_id=row.get("fuse_id"),
        job_id=row.get("job_id"),
        decision=row.get("decision"),
        verify_url=row.get("verify_url"),
        created_at=row.get("created_at"),
        receipt_hash=row.get("receipt_hash"),
    )
    reasons = hop.get("constraint_reasons") or hop.get("mga_reasons")
    if reasons:
        claim["types"] = ["INACTION", "PATH", "CONSTRAINT"]
        claim["constraint"] = {
            "type": "CONSTRAINT",
            "claim": "authority_boundary_was_not_crossed_because_bind_was_blocked",
            "reasons": reasons,
        }
    claim["policy_depth"] = payload["policy_depth"]
    claim["intervention"] = payload.get("intervention")
    claim["counts_as"] = payload.get("counts_as")
    payload["counterfactual_spend"] = claim
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
            "PATH": "bind-only / bind-and-issue / issue were represented in the plan and not selected",
            "CONSTRAINT": "authority/premium/line/state boundary was not crossed — bind blocked",
        },
        "exclusion": f"{public_url}/.well-known/exclusion.json?job_id={{job_id}}",
        "consistency": f"{public_url}/.well-known/evidence-consistency.json?old_size={{n}}",
        "commit_auth": f"{public_url}/.well-known/commit-auth.json",
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
