"""Psychohistory Seldon Line — aggregate bind prediction with observer effect.

Fiction: Isaac Asimov *Foundation* — psychohistory predicts mass behavior; Seldon Crises
are inevitable forks; the Second Foundation hides the math.

Twist: Aggregate bind HALT rate + ghost-bind density predicts next renewal choke —
publishing the line changes carrier behavior (observer effect) → pre-choke before batch.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-psychohistory-seldon-line-v1"
INVENTION = "Psychohistory Seldon Line"
TIER = "S"
FAMILY = "s-tier"

REAL = {
    "institution": "Asimov Foundation psychohistory (fiction) + econophysics aggregate prediction",
    "concept": "Mass behavior predictable at scale; observer effect alters the path",
    "seldon_crisis": "Inevitable fork — intervention window is narrow",
    "url": "https://en.wikipedia.org/wiki/Psychohistory_(fictional)",
}


def seldon_line(
    *,
    halt_rate_7d: float | None = None,
    ghost_density: float | None = None,
    renewal_window_hours: float | None = None,
    published: bool | None = None,
) -> dict[str, Any]:
    halt = max(0.0, min(float(halt_rate_7d or 0), 1.0))
    ghost = max(0.0, min(float(ghost_density or 0), 1.0))
    window = max(1.0, float(renewal_window_hours or 24))
    crisis_score = halt * 0.6 + ghost * 0.4
    crisis = crisis_score >= 0.35
    observer_dampening = 0.15 if published else 0.0
    adjusted = max(0.0, crisis_score - observer_dampening)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "tier": TIER,
        "real_institution": REAL,
        "seldon_crisis": crisis,
        "crisis_score": round(crisis_score, 4),
        "adjusted_score": round(adjusted, 4),
        "observer_effect": published,
        "verdict": "PRE_CHOKE" if adjusted >= 0.35 else "SELFDON_STABLE",
        "renewal_window_hours": window,
        "recommendation": "Publish line + choke renewal batch early" if crisis else "Hold",
        "rule": "Aggregate bind pathology predicts choke — publishing the line is the intervention.",
    }


def attach(plan: dict) -> dict:
    weather = plan.get("bind_weather") if isinstance(plan.get("bind_weather"), dict) else {}
    ghost = plan.get("ghost_bind") if isinstance(plan.get("ghost_bind"), dict) else {}
    ev = seldon_line(
        halt_rate_7d=weather.get("halt_rate_7d") or (0.5 if plan.get("halt") else 0.0),
        ghost_density=1.0 if ghost.get("haunted") else 0.0,
        renewal_window_hours=weather.get("renewal_window_hours") or 24,
        published=bool(weather.get("published")),
    )
    plan["seldon_line"] = ev
    if ev.get("verdict") == "PRE_CHOKE":
        plan["seldon_pre_choke"] = True
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "tier": TIER,
        "one_liner": "Seldon line — aggregate bind HALT predicts renewal choke; publish to intervene.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/psychohistory-seldon-line",
        "well_known": f"{base}/.well-known/psychohistory-seldon-line.json",
    }
