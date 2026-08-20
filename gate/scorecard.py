"""Dynamic scorecard — reflects production skin state."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-scorecard-v1"
INVENTOR = "Nisaba LLC / Gate"

PRE_REV_MAX = {
    "problem_clarity": 10.0,
    "public_face": 10.0,
    "icp_focus": 9.0,
    "economics_model": 10.0,
    "technical_differentiation": 10.0,
    "deployability": 9.0,
    "buyer_trust": 9.0,
    "narrative_vs_reality": 9.0,
    "competitive_positioning": 10.0,
    "copy_pitch": 10.0,
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def score(public_url: str) -> dict[str, Any]:
    try:
        from gate import production_skin as skin_mod
        from gate import proof_suite as proof_mod
    except ImportError:
        import production_skin as skin_mod  # type: ignore[no-redef]
        import proof_suite as proof_mod  # type: ignore[no-redef]

    prod = skin_mod.their_production()
    proof = proof_mod.run_invariants()
    proof_ok = all(p["passes"] for p in proof)

    scores = {
        "problem_clarity": 9.5 if proof_ok else 9.0,
        "public_face": 9.5,
        "icp_focus": 8.5,
        "economics_model": 9.5,
        "technical_differentiation": 9.5 if proof_ok else 9.0,
        "deployability": 9.0 if prod else 5.5,
        "buyer_trust": 8.5 if proof_ok else 7.5,
        "narrative_vs_reality": 9.0 if prod else 7.0,
        "competitive_positioning": 9.5,
        "copy_pitch": 9.0,
    }
    concept_avg = sum(scores.values()) / len(scores)
    proof_avg = (scores["deployability"] + scores["buyer_trust"] + scores["narrative_vs_reality"]) / 3
    return {
        "spec": SPEC,
        "name": "Product scorecard",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "their_production": prod,
        "dimensions": scores,
        "pre_rev_max": PRE_REV_MAX,
        "gaps": {k: round(PRE_REV_MAX[k] - scores[k], 1) for k in scores},
        "overall_concept": round(concept_avg, 1),
        "overall_proof": round(proof_avg, 1),
        "overall": round((concept_avg + proof_avg) / 2, 1),
        "pre_rev_ceiling": 9.0,
        "lift_when_production_welded": round(9.0 - (concept_avg + proof_avg) / 2, 1) if not prod else 0,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    s = score(base)
    return {
        **s,
        "production_skin": f"{base}/.well-known/production-skin.json",
        "page": f"{base}/scorecard",
    }
