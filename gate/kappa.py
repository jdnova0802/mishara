"""The κ (Kappa) Register — mouth invariant + settlement schism.

Invention (2026): permission mass is conserved; restraint is measurable; cutoff
observation collapses parallel settlement timelines.

  Conservation (mouth invariant):
    M_total = M_cf + M_live
    M_cf  = counterfactual mass (HALT/BLOCK inaction receipts)
    M_live = collapsed live mass (ALLOW or acted bind)

  κ (kappa) = M_cf / M_total  — restraint coefficient ∈ [0, 1]
    High κ: civilization is holding the line (more prevented than cleared).
    Low κ: mouths are clearing (more binds than halts).

  Permission velocity V = hops / day (rolling 24h window).
  Tension τ = κ × V — macro-adjacent "permission pressure" on the rail.

  Schism (settlement cutoff):
    An obligation arriving after cutoff_at exists in two timelines until the
    window state transitions to SETTLED (observation). Timeline A would have
    netted in window W; timeline B settles in W+1. Same quantum-mechanics shape
    as DEAD|LIVE until CHARGE — here it is W|W+1 until cutoff finality.

Not SaaS. A published invariant operators and regulators can cite.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

SPEC = "gate-kappa-register-v1"
SCHISM_SPEC = "gate-schism-v1"
INVARIANT = "M_total = M_cf + M_live"
COLLAPSE = "CHARGE collapses DEAD|LIVE superposition into M_live; cutoff finality collapses W|W+1 into one window."


def _parse_iso(ts: str) -> datetime:
    t = (ts or "").strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    dt = datetime.fromisoformat(t)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def classify_mass(*, decision: str | None, acted: bool | None) -> str:
    """Return counterfactual | live | other for one hop."""
    d = (decision or "").upper()
    if d in ("HALT", "BLOCK") and acted is not True:
        return "counterfactual"
    if d == "ALLOW" or acted is True:
        return "live"
    return "other"


def tally_mass(events: list[dict]) -> dict[str, int]:
    m_cf = m_live = m_other = 0
    for ev in events or []:
        bucket = classify_mass(decision=ev.get("decision"), acted=ev.get("acted"))
        if bucket == "counterfactual":
            m_cf += 1
        elif bucket == "live":
            m_live += 1
        else:
            m_other += 1
    m_total = m_cf + m_live + m_other
    return {
        "M_cf": m_cf,
        "M_live": m_live,
        "M_other": m_other,
        "M_total": m_total,
    }


def restraint_coefficient(m_cf: int, m_live: int, *, m_other: int = 0) -> float | None:
    denom = m_cf + m_live
    if denom <= 0:
        return None
    return round(m_cf / denom, 6)


def permission_velocity(events: list[dict], *, window_hours: int = 24) -> float | None:
    """Hops per day in the trailing window (UTC)."""
    if not events:
        return None
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=max(1, window_hours))
    recent = 0
    for ev in events:
        created = ev.get("created_at")
        if not created:
            continue
        try:
            if _parse_iso(created) >= cutoff:
                recent += 1
        except ValueError:
            continue
    if recent <= 0:
        return 0.0
    days = window_hours / 24.0
    return round(recent / days, 4)


def permission_tension(kappa: float | None, velocity: float | None) -> float | None:
    if kappa is None or velocity is None:
        return None
    return round(kappa * velocity, 4)


def schism_at_cutoff(
    *,
    obligation_id: str,
    obligation_at: str,
    cutoff_at: str,
    would_window_id: str,
    actual_window_id: str,
) -> dict[str, Any] | None:
    """Mint a schism receipt when an obligation arrives after window cutoff.

    Returns None if the obligation is on-time (no parallel timeline).
    """
    try:
        ob_t = _parse_iso(obligation_at)
        cut_t = _parse_iso(cutoff_at)
    except ValueError:
        return None
    if ob_t <= cut_t:
        return None
    delta = (ob_t - cut_t).total_seconds()
    return {
        "spec": SCHISM_SPEC,
        "type": "SCHISM",
        "claim": "obligation_straddles_cutoff_observation",
        "obligation_id": obligation_id,
        "obligation_at": obligation_at,
        "cutoff_at": cutoff_at,
        "delta_seconds_after_cutoff": round(delta, 3),
        "timeline_a": {
            "window_id": would_window_id,
            "claim": "would_have_netted_if_arrived_before_cutoff",
            "observed": False,
        },
        "timeline_b": {
            "window_id": actual_window_id,
            "claim": "settles_in_next_open_window",
            "observed": True,
        },
        "observation": "window finality hash at SETTLED collapses W|W+1 membership",
        "quantum_analogy": "DEAD|LIVE until CHARGE; here W|W+1 until cutoff finality",
        "not_global": "Schism is scoped to Gate settlement windows, not metaphysics.",
        "their_production": False,
    }


def register_from_events(events: list[dict], *, public_url: str) -> dict[str, Any]:
    mass = tally_mass(events)
    kappa = restraint_coefficient(mass["M_cf"], mass["M_live"])
    velocity = permission_velocity(events)
    tension = permission_tension(kappa, velocity)
    conserved = mass["M_total"] == mass["M_cf"] + mass["M_live"] + mass["M_other"]
    return {
        "spec": SPEC,
        "name": "The κ (Kappa) Register",
        "invariant": INVARIANT,
        "collapse": COLLAPSE,
        "conserved": conserved,
        "mass": mass,
        "kappa": kappa,
        "interpretation": {
            "kappa": "restraint coefficient — share of permission mass still counterfactual",
            "high_kappa": "more halts than clears; mouth is holding",
            "low_kappa": "more clears than halts; rails are moving",
        },
        "velocity": {
            "V_hops_per_day": velocity,
            "window_hours": 24,
            "macro_adjacent": "permission velocity on welded mouths — not M2, but mouth-local flow temperature",
        },
        "tension": {
            "tau": tension,
            "formula": "τ = κ × V",
            "meaning": "restraint × velocity — pressure when a hot rail is also heavily gated",
        },
        "schism": {
            "spec": SCHISM_SPEC,
            "when": "obligation.created_at > window.cutoff_at",
            "manifest": f"{public_url}/.well-known/schism.json",
        },
        "links": {
            "counterfactual_spend": f"{public_url}/.well-known/counterfactual-spend.json",
            "settlement": f"{public_url}/.well-known/settlement.json",
            "restraint": f"{public_url}/.well-known/restraint.json",
            "register": f"{public_url}/.well-known/register.json",
        },
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    return {
        "spec": SPEC,
        "name": "The κ (Kappa) Register",
        "problem": (
            "Counterfactual receipts prove what did not spend. Settlement windows prove what cleared. "
            "Nobody publishes the conservation law between them."
        ),
        "solution": (
            "M_total = M_cf + M_live. κ measures restraint. τ = κ×V measures permission tension. "
            "Schism receipts mark obligations that straddle cutoff observation."
        ),
        "invariant": INVARIANT,
        "collapse": COLLAPSE,
        "live_register": f"{public_url}/.well-known/kappa.json",
        "schism": f"{public_url}/.well-known/schism.json",
        "counterfactual": f"{public_url}/.well-known/counterfactual-spend.json",
        "settlement": f"{public_url}/.well-known/settlement.json",
        "their_production": False,
    }


def schism_manifest(public_url: str) -> dict[str, Any]:
    return {
        "spec": SCHISM_SPEC,
        "name": "Settlement schism receipts",
        "when": "obligation timestamp is strictly after window.cutoff_at",
        "timelines": {
            "A": "would have netted in window W if it arrived before cutoff",
            "B": "actually routes to window W+1",
        },
        "observation": "SETTLED finality hash collapses parallel window membership",
        "analogy": "Same observation-collapse shape as CHARGE on DEAD|LIVE permission",
        "kappa_register": f"{public_url}/.well-known/kappa.json",
        "their_production": False,
    }
