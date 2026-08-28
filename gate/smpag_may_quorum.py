"""SMPAG May Quorum — UN planetary defense has no strike button; bind gets one.

Real: UN Space Mission Planning Advisory Group (UNOOSA/COPUOS). SMPAG advises on
NEO mitigation; recommendations not legally binding; >1% impact + >50m triggers
monitoring; IAA Planetary Defense Conference exercises (2025 Stellenbosch, 2027 Montreal).

Twist: Sacred-mass bind (Stick Meter sacred) requires SMPAG-class multi-agency quorum —
no single desk strikes the premium.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-smpag-may-quorum-v1"
INVENTION = "SMPAG May Quorum"
TIER = "S"
FAMILY = "s-tier"

REAL = {
    "institution": "UN SMPAG — UNOOSA / COPUOS",
    "chair": "ESA (2026)",
    "threshold": ">1% impact probability + >50m → SMPAG active monitoring",
    "binding": False,
    "exercise": "IAA Planetary Defense Conference 2027 Montreal",
    "url": "https://www.unoosa.org/oosa/en/ourwork/topics/neos/smpag.html",
}


def evaluate(
    *,
    mass_class: str | None = None,
    quorum_present: bool | None = None,
    agencies: list[str] | None = None,
    single_desk_strike: bool | None = None,
) -> dict[str, Any]:
    mc = (mass_class or "light").strip().lower()
    sacred = mc == "sacred"
    agencies = [a for a in (agencies or []) if a]
    if not sacred:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "tier": TIER,
            "verdict": "QUORUM_NOT_REQUIRED",
            "smpag_active": False,
            "may_stick": True,
        }
    if single_desk_strike and not quorum_present:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "tier": TIER,
            "real_institution": REAL,
            "verdict": "SMPAG_QUORUM_MISSING",
            "may_stick": False,
            "reason": "sacred_mass_single_desk_forbidden",
            "required_agencies_min": 2,
            "agencies_present": agencies,
        }
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "tier": TIER,
        "real_institution": REAL,
        "verdict": "SMPAG_QUORUM_OK" if quorum_present else "SMPAG_ADVISORY_ONLY",
        "may_stick": bool(quorum_present),
        "smpag_active": True,
        "agencies_present": agencies,
        "rule": "Planetary binds need more than one hunter — sacred premium is SMPAG-class.",
    }


def attach(plan: dict) -> dict:
    sm = plan.get("stick_meter") if isinstance(plan.get("stick_meter"), dict) else {}
    agencies = plan.get("agencies") if isinstance(plan.get("agencies"), list) else []
    ev = evaluate(
        mass_class=sm.get("mass_class"),
        quorum_present=bool(plan.get("quorum_present") or len(agencies) >= 2),
        agencies=agencies,
        single_desk_strike=bool(plan.get("single_desk_strike") or not plan.get("quorum_present")),
    )
    plan["smpag_quorum"] = ev
    if not ev.get("may_stick") and ev.get("verdict") == "SMPAG_QUORUM_MISSING":
        plan["smpag_quorum_missing"] = True
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "tier": TIER,
        "one_liner": "UN SMPAG quorum for sacred bind mass — no single desk asteroid-strike.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/smpag-may-quorum",
        "well_known": f"{base}/.well-known/smpag-may-quorum.json",
    }
