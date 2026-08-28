"""Great Filter Gate — irreversible bind as civilizational filter step.

Real: Great Filter hypothesis (Hanson 1996, Bostrom) — something destroys civilizations
before they spread; late-stage tech without restraint may be the filter.

Twist: Bind without epoch lock + quorum + stranger verify is a filter candidate —
carriers that pass export the artifact; those that ghost-bind don't survive audit.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-great-filter-gate-v1"
INVENTION = "Great Filter Gate"
TIER = "S"
FAMILY = "s-tier"

REAL = {
    "institution": "Great Filter hypothesis — Hanson 1996 / Bostrom existential risk",
    "concept": "Late-stage civilization bottleneck before interstellar spread",
    "url": "https://en.wikipedia.org/wiki/Great_Filter",
}


def filter_step(
    *,
    epoch_locked: bool | None = None,
    stranger_verify: bool | None = None,
    quorum_met: bool | None = None,
    ghost_bind: bool | None = None,
    acted_without_may: bool | None = None,
) -> dict[str, Any]:
    failures = []
    if not epoch_locked:
        failures.append("no_epoch_lock")
    if not stranger_verify:
        failures.append("no_stranger_verify")
    if ghost_bind:
        failures.append("ghost_bind")
    if acted_without_may:
        failures.append("acted_without_may")
    if quorum_met is False:
        failures.append("sacred_quorum_missing")
    passed = len(failures) == 0
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "tier": TIER,
        "real_institution": REAL,
        "verdict": "FILTER_PASSED" if passed else "FILTER_CANDIDATE",
        "passed": passed,
        "failures": failures,
        "survival": passed,
        "rule": "Irreversible bind without restraint artifacts is a Great Filter step — fail audit, fail lineage.",
    }


def attach(plan: dict) -> dict:
    epoch = plan.get("epoch") if isinstance(plan.get("epoch"), dict) else {}
    smpag = plan.get("smpag_quorum") if isinstance(plan.get("smpag_quorum"), dict) else {}
    ev = filter_step(
        epoch_locked=bool(epoch.get("locked") or plan.get("epoch_locked")),
        stranger_verify=bool(plan.get("verify_url")),
        quorum_met=smpag.get("may_stick") if smpag else None,
        ghost_bind=bool((plan.get("ghost_bind") or {}).get("haunted")),
        acted_without_may=bool(plan.get("acted") and not plan.get("allow_bind")),
    )
    plan["great_filter"] = ev
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "tier": TIER,
        "one_liner": "Great Filter gate — ghost bind is civilizational filter failure.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/great-filter-gate",
        "well_known": f"{base}/.well-known/great-filter-gate.json",
    }
