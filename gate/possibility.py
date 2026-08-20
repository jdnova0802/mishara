"""Possibility Finality — beyond irreversibility.

Irreversibility says the spend won't rewind. That is necessary and not enough.

This layer adds three stronger claims Gate already behaves like:

  1. POSSIBILITY (constructor-shaped)
     Laws as possible vs impossible tasks. The mouth does not merely reverse
     time — it declares which irreversible writes are allowed to arbitrary
     accuracy on this hop, and which are forbidden.

  2. COUNTERFACTUAL POLICY DEPTH (active-inference-shaped)
     Before the act, a finite policy set is evaluated. Consciousness research
     (Friston): temporally thick inference needs counterfactual policies —
     "what would happen if I selected π". Gate publishes which π were
     represented and not selected. That is depth, not vibes.

  3. LEGAL-SHAPED FINALITY MOMENTS (SFD / PFMI Principle 8)
     Operational settlement ≠ institutional irrevocability.
       Finality I   — entry into the window (order accepted)
       Finality II  — irrevocable (cannot be unilaterally revoked)
       Finality III — binding against third parties (finality hash stamped)

Not a theory of mind. Not AI governance LinkedIn. Infrastructure language
borrowed from physics-of-tasks + settlement law so partners can cite moments.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-possibility-finality-v1"
POLICY_DEPTH_SPEC = "gate-policy-depth-v1"
FINALITY_MOMENTS_SPEC = "gate-finality-moments-v1"

# Married / refused writes Gate already treats as distinct tasks.
DEFAULT_POLICIES = (
    {
        "policy_id": "π_bind_only",
        "task": "POST /job/v1/jobs/{job_id}/bind-only",
        "spend_kind": "bind",
        "constructor_status": "possible_if_mouth_permits",
    },
    {
        "policy_id": "π_bind_and_issue",
        "task": "POST /job/v1/jobs/{job_id}/bind-and-issue",
        "spend_kind": "bind_and_issue",
        "constructor_status": "impossible_on_this_scanner",
    },
    {
        "policy_id": "π_issue",
        "task": "POST /policy/v1/policies/{policy_id}/issue",
        "spend_kind": "issue",
        "constructor_status": "impossible_on_this_scanner",
    },
    {
        "policy_id": "π_withdraw",
        "task": "withdraw / payout clear-before-wire",
        "spend_kind": "withdraw",
        "constructor_status": "possible_if_mouth_permits",
    },
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def policy_set(*, job_id: str | None = None, policy_id: str | None = None) -> list[dict]:
    jid = (job_id or "").strip() or "JOB_ID"
    pid = (policy_id or "").strip() or "POLICY_ID"
    out = []
    for p in DEFAULT_POLICIES:
        task = p["task"].format(job_id=jid, policy_id=pid)
        out.append({**p, "task": task, "job_id": jid})
    return out


def evaluate_policies(
    *,
    decision: str | None,
    acted: bool | None,
    selected_spend: str | None = None,
    job_id: str | None = None,
) -> dict[str, Any]:
    """Counterfactual policy depth for one hop.

    Returns selected policy (if any) and not-selected policies with reasons.
    HALT/BLOCK → no irreversible policy selected; all permit-gated tasks remain
    counterfactual for this observation.
    """
    d = (decision or "").upper()
    policies = policy_set(job_id=job_id)
    selected = None
    not_selected: list[dict] = []

    if acted is True and d == "ALLOW":
        want = (selected_spend or "bind").strip().lower()
        for p in policies:
            if p["spend_kind"] == want and p["constructor_status"].startswith("possible"):
                selected = {
                    **p,
                    "selected": True,
                    "claim": "policy_selected_and_mouth_permitted",
                }
            elif p["constructor_status"].startswith("impossible"):
                not_selected.append(
                    {
                        **p,
                        "selected": False,
                        "reason": "impossible_on_this_scanner",
                    }
                )
            else:
                not_selected.append(
                    {
                        **p,
                        "selected": False,
                        "reason": "represented_not_selected",
                    }
                )
    else:
        for p in policies:
            if p["constructor_status"].startswith("impossible"):
                reason = "impossible_on_this_scanner"
            else:
                reason = "mouth_forbade_or_halted"
            not_selected.append({**p, "selected": False, "reason": reason})

    depth = len(not_selected) + (1 if selected else 0)
    return {
        "spec": POLICY_DEPTH_SPEC,
        "claim": "finite_policy_set_evaluated_before_irreversible_act",
        "lineage": [
            "Active inference / free-energy: counterfactual policy depth before action",
            "Constructor theory: possible vs impossible tasks (Deutsch/Marletto)",
            "Gate counterfactual spend: forbidden transitions represented and not selected",
        ],
        "decision": d or None,
        "acted": acted,
        "policy_depth": depth,
        "selected": selected,
        "not_selected": not_selected,
        "not_consciousness": (
            "This is settlement/ops language for evaluated policies — "
            "not a theory of phenomenal experience."
        ),
        "their_production": False,
    }


def finality_moments(
    *,
    window_id: str,
    opened_at: str | None = None,
    cutoff_at: str | None = None,
    settled_at: str | None = None,
    finality_hash: str | None = None,
    state: str | None = None,
) -> dict[str, Any]:
    """SFD-shaped Finality I / II / III for one settlement window."""
    st = (state or "").upper()
    settled = st in ("SETTLED", "DEFAULTED") and bool(finality_hash)

    return {
        "spec": FINALITY_MOMENTS_SPEC,
        "window_id": window_id,
        "lineage": [
            "EU Settlement Finality Directive (98/26/EC) — entry / irrevocable / binding",
            "PFMI Principle 8 — final settlement is a legally defined moment",
            "Gate settlement windows — operational close + tamper-evident hash",
        ],
        "moments": {
            "I_entry": {
                "name": "Finality I — entry",
                "meaning": "Obligation accepted into the open window",
                "at": opened_at,
                "reached": bool(opened_at),
            },
            "II_irrevocable": {
                "name": "Finality II — irrevocable",
                "meaning": "Past cutoff: cannot unilaterally revoke membership in this window",
                "at": cutoff_at,
                "reached": bool(cutoff_at) and st in ("NETTING", "SETTLED", "DEFAULTED"),
            },
            "III_binding": {
                "name": "Finality III — binding / third-party durable",
                "meaning": "Finality hash stamped — exportable closure against later reinterpretation",
                "at": settled_at,
                "finality_hash": finality_hash,
                "reached": settled,
            },
        },
        "beyond_irreversibility": (
            "Irreversibility: the spend won't casually rewind. "
            "Finality III: the closure is citeable against third-party dispute and reinterpretation."
        ),
        "not_legal_advice": True,
        "their_production": False,
    }


def register_snapshot(
    *,
    public_url: str,
    decision: str | None = None,
    acted: bool | None = None,
    job_id: str | None = None,
    selected_spend: str | None = None,
    window: dict | None = None,
) -> dict[str, Any]:
    """Combined public artifact: policy depth + optional window finality moments."""
    depth = evaluate_policies(
        decision=decision,
        acted=acted,
        selected_spend=selected_spend,
        job_id=job_id,
    )
    moments = None
    if isinstance(window, dict) and window.get("id"):
        moments = finality_moments(
            window_id=str(window["id"]),
            opened_at=window.get("opened_at"),
            cutoff_at=window.get("cutoff_at"),
            settled_at=window.get("settled_at"),
            finality_hash=window.get("finality_hash"),
            state=window.get("state"),
        )
    return {
        "spec": SPEC,
        "name": "Possibility Finality",
        "thesis": (
            "Beyond irreversibility: possible vs impossible tasks, "
            "counterfactual policy depth, and SFD-shaped finality moments."
        ),
        "evaluated_at": _now(),
        "policy_depth": depth,
        "finality_moments": moments,
        "links": {
            "counterfactual_spend": f"{public_url}/.well-known/counterfactual-spend.json",
            "kappa": f"{public_url}/.well-known/kappa.json",
            "settlement": f"{public_url}/.well-known/settlement.json",
            "schism": f"{public_url}/.well-known/schism.json",
            "this": f"{public_url}/.well-known/possibility-finality.json",
            "mouth_constitution": f"{public_url}/.well-known/mouth-constitution.json",
        },
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Possibility Finality",
        "problem": (
            "Irreversibility explains why the wire matters. Partners need citeable structure: "
            "which tasks were possible, which policies were evaluated, and when closure became final."
        ),
        "solution": (
            "Publish policy depth (selected + not-selected π) and Finality I/II/III moments "
            "per settlement window — constructor-shaped possibility + SFD-shaped irrevocability."
        ),
        "layers": {
            "possibility": "possible vs impossible spend tasks on this scanner",
            "policy_depth": POLICY_DEPTH_SPEC,
            "finality_moments": FINALITY_MOMENTS_SPEC,
        },
        "not": [
            "a theory of phenomenal consciousness",
            "AI governance LinkedIn",
            "legal advice or designated SFD system status",
        ],
        "live": f"{base}/.well-known/possibility-finality.json",
        "counterfactual": f"{base}/.well-known/counterfactual-spend.json",
        "settlement": f"{base}/.well-known/settlement.json",
        "kappa": f"{base}/.well-known/kappa.json",
        "their_production": False,
    }
