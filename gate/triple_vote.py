"""Item 21 — three independent graders must agree on high-stakes ALLOW."""
from __future__ import annotations

from typing import Any

SPEC = "gate-triple-vote-v1"


def _hop_grade(hop: dict | None) -> str:
    hop = hop if isinstance(hop, dict) else {}
    if hop.get("halt") or str(hop.get("state") or "").upper() == "DEAD":
        return "BLOCK"
    if hop.get("verdict") is False:
        return "BLOCK"
    return "ALLOW"


def _constraint_grade(plan: dict | None) -> str:
    reasons = (plan or {}).get("reasons") or []
    if reasons:
        return "BLOCK"
    if (plan or {}).get("halt"):
        return "BLOCK"
    if (plan or {}).get("result") == "BLOCK":
        return "BLOCK"
    return "ALLOW"


def _circuit_grade(breaker: dict | None) -> str:
    if breaker and breaker.get("open"):
        return "HOLD"
    return "ALLOW"


def grade(*, hop: dict | None, plan: dict | None, breaker: dict | None = None) -> dict[str, Any]:
    votes = {
        "hop": _hop_grade(hop),
        "constraints": _constraint_grade(plan),
        "circuit": _circuit_grade(breaker),
    }
    unique = set(votes.values())
    agreed = len(unique) == 1
    result = next(iter(unique)) if agreed else "HOLD"
    return {
        "spec": SPEC,
        "votes": votes,
        "agreed": agreed,
        "result": result,
        "plain": (
            "All three graders agree."
            if agreed
            else "Graders disagree — HOLD until a human reads the split."
        ),
    }
