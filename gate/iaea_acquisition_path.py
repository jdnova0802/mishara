"""IAEA Acquisition Path — state-level safeguards for ghost bind cheating paths.

Real: IAEA State-Level Concept — acquisition path analysis ranks undeclared
nuclear material routes; holistic state profile; irreversible disarmament verification
literature (2024+).

Twist: Rank bind-path cheating routes (soft PAS, admin resurrect, offline ticket)
like acquisition paths — optimize inspection on highest-risk path.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-iaea-acquisition-path-v1"
INVENTION = "IAEA Acquisition Path"
TIER = "S"
FAMILY = "s-tier"

REAL = {
    "institution": "International Atomic Energy Agency",
    "concept": "State-Level Concept — Acquisition Path Analysis (APA)",
    "focus": "Rank undeclared material routes; holistic safeguards conclusions",
    "url": "https://www.iaea.org/topics/nuclear-verification-and-security",
}

PATHS = (
    {"id": "soft_pas_bind", "risk": 0.95, "detect": "ghost_bind"},
    {"id": "admin_resurrect_epoch", "risk": 0.92, "detect": "override_impossibility"},
    {"id": "offline_bearer_ticket", "risk": 0.88, "detect": "spend_protocol"},
    {"id": "uw_as_charge", "risk": 0.90, "detect": "charge_bride"},
    {"id": "renewal_batch_bypass", "risk": 0.85, "detect": "ghost_renewal_snare"},
)


def analyze(*, scenario: dict | None = None) -> dict[str, Any]:
    s = scenario if isinstance(scenario, dict) else {}
    active = []
    for p in PATHS:
        key = p["id"]
        if s.get(key) or s.get(key.replace("_", "-")):
            active.append({**p, "active": True})
    ranked = sorted(active or PATHS, key=lambda x: -x["risk"])
    top = ranked[0] if ranked else None
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "tier": TIER,
        "real_institution": REAL,
        "paths_ranked": ranked[:5],
        "highest_risk": top,
        "safeguards_conclusion": "HALT" if active else "CLEAR",
        "rule": "Treat ghost bind routes like undeclared acquisition paths — inspect the top one.",
    }


def attach(plan: dict) -> dict:
    scenario = {
        "soft_pas_bind": bool((plan.get("ghost_bind") or {}).get("haunted")),
        "admin_resurrect_epoch": bool(plan.get("override_attempt")),
        "offline_bearer_ticket": bool((plan.get("bind_ticket") or {}).get("offline_bearer")),
        "uw_as_charge": bool((plan.get("charge_bride") or {}).get("forged")),
        "renewal_batch_bypass": bool(plan.get("renewal_batch_bypass")),
    }
    plan["iaea_acquisition_path"] = analyze(scenario=scenario)
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "tier": TIER,
        "one_liner": "IAEA acquisition-path ranker for bind cheating routes.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/iaea-acquisition-path",
        "well_known": f"{base}/.well-known/iaea-acquisition-path.json",
    }
