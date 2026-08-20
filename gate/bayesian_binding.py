"""Bayesian Binding of Status — Beautiful Loop × Counts-As.

Friston/Laukkonen: consciousness-adjacent Bayesian binding = inferential
competition into an epistemic field. Gate productizes the ops analog:

  Before the irreversible write, policies compete. Only the inference that
  coherently reduces long-term uncertainty (halt vs allow under licensed
  constraints) enters the epistemic field — AND that entry constitutively
  counts as status Y in context C.

Not phenomenal consciousness. Binding of *institutional status* under
predictive competition.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-bayesian-binding-v1"
INVENTOR = "Nisaba LLC / Gate"

try:
    from gate import possibility as possibility_mod
except ImportError:
    import possibility as possibility_mod

try:
    from gate import constitution as constitution_mod
except ImportError:
    import constitution as constitution_mod


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def bind_status(
    *,
    decision: str | None,
    acted: bool | None,
    job_id: str | None = None,
    selected_spend: str | None = None,
    event_id: str | None = None,
    fuse_id: str | None = None,
) -> dict[str, Any]:
    """Inferential competition → epistemic entry → constitutive status."""
    depth = possibility_mod.evaluate_policies(
        decision=decision,
        acted=acted,
        job_id=job_id,
        selected_spend=selected_spend,
    )
    status = constitution_mod.counts_as(
        decision=decision,
        acted=acted,
        event_id=event_id,
        fuse_id=fuse_id,
        job_id=job_id,
    )

    competitors = []
    if depth.get("selected"):
        competitors.append(
            {
                **depth["selected"],
                "competition": "won",
                "enters_epistemic_field": True,
            }
        )
    for p in depth.get("not_selected") or []:
        competitors.append(
            {
                **p,
                "competition": "lost",
                "enters_epistemic_field": False,
            }
        )

    winners = [c for c in competitors if c.get("enters_epistemic_field")]
    return {
        "spec": SPEC,
        "name": "Bayesian Binding of Status",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Beautiful Loop (Laukkonen/Friston/Chandaria 2025) — Bayesian binding into epistemic field",
            "Active inference — counterfactual policy competition before action",
            "Searle counts-as — constitutive status assignment (Gate Mouth Constitution)",
        ],
        "conditions": {
            "world_model": "licensed mouth + spend protocol + fuse/epoch facts",
            "inferential_competition": "finite π set scored; one may win",
            "epistemic_depth": "selected π recurrently shared on receipt + manifests",
            "constitutive_status": "winner counts as Y in C (or halt constitutes refusal)",
        },
        "competitors": competitors,
        "bound_into_field": winners[0] if winners else None,
        "status": status,
        "claim": (
            "status_bound_via_inferential_competition"
            if status.get("constituted")
            else "no_status_constituted"
        ),
        "not_consciousness": (
            "Ops binding of institutional status under policy competition — "
            "not a theory of phenomenal experience."
        ),
        "gatekeep": "Proprietary weld of predictive competition + constitutive status. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: dict, row: dict) -> dict:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    spend = None
    if isinstance(hop.get("spend_write"), dict):
        spend = hop["spend_write"].get("spend_kind")
    payload["bayesian_binding"] = bind_status(
        decision=row.get("decision"),
        acted=row.get("acted"),
        job_id=row.get("job_id"),
        selected_spend=spend,
        event_id=row.get("id"),
        fuse_id=row.get("fuse_id"),
    )
    return payload


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Bayesian Binding of Status",
        "inventor": INVENTOR,
        "thesis": (
            "Policies compete; the winner enters the epistemic field and "
            "constitutively counts as permitted or refused irreversible spend."
        ),
        "live": f"{base}/.well-known/bayesian-binding.json",
        "mouth_constitution": f"{base}/.well-known/mouth-constitution.json",
        "possibility_finality": f"{base}/.well-known/possibility-finality.json",
        "their_production": False,
    }
