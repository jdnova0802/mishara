"""Doomsday Bind Hand — Bulletin Atomic Scientists clock as may metric.

Real: Bulletin of the Atomic Scientists Doomsday Clock — 85 seconds to midnight (2026).
Science and Security Board; nuclear, climate, biothreat, disruptive tech including AI.

Twist: Each sacred bind without quorum / each ghost bind nudges the bind hand toward
midnight — publishable may metric for carriers, not marketing cosplay.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-doomsday-bind-hand-v1"
INVENTION = "Doomsday Bind Hand"
TIER = "S"
FAMILY = "s-tier"

REAL = {
    "institution": "Bulletin of the Atomic Scientists",
    "clock_2026": "85 seconds to midnight",
    "set_date": "2026-01-27",
    "prior_2025_seconds": 89,
    "board": "Science and Security Board + Board of Sponsors (8 Nobel laureates)",
    "url": "https://thebulletin.org/doomsday-clock/2026-statement/",
}

BASE_SECONDS = 85


def hand(
    *,
    ghost_events: int | None = None,
    sacred_bind_without_quorum: int | None = None,
    epoch_bypass_attempts: int | None = None,
    restraint_proved: int | None = None,
) -> dict[str, Any]:
    ghosts = max(0, int(ghost_events or 0))
    sacred = max(0, int(sacred_bind_without_quorum or 0))
    bypass = max(0, int(epoch_bypass_attempts or 0))
    restraint = max(0, int(restraint_proved or 0))
    delta = ghosts + sacred + bypass - restraint
    seconds = max(1, BASE_SECONDS - delta)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "tier": TIER,
        "real_institution": REAL,
        "bind_hand_seconds_to_midnight": seconds,
        "baseline_2026_seconds": BASE_SECONDS,
        "delta_from_restraint": -restraint,
        "delta_from_risk": ghosts + sacred + bypass,
        "verdict": "CLOSER" if delta > 0 else ("FARTHER" if delta < 0 else "HOLD"),
        "rule": "May metric strangers can cite — bind ghost events move the hand.",
    }


def attach(plan: dict) -> dict:
    ghost = plan.get("ghost_bind") if isinstance(plan.get("ghost_bind"), dict) else {}
    smpag = plan.get("smpag_quorum") if isinstance(plan.get("smpag_quorum"), dict) else {}
    ev = hand(
        ghost_events=1 if ghost.get("haunted") else 0,
        sacred_bind_without_quorum=1 if smpag.get("verdict") == "SMPAG_QUORUM_MISSING" else 0,
        epoch_bypass_attempts=1 if plan.get("override_attempt") else 0,
        restraint_proved=1 if (plan.get("refuse_ledger") or {}).get("rho_logged") else 0,
    )
    plan["doomsday_hand"] = ev
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "tier": TIER,
        "one_liner": "Doomsday Clock hand for bind-path may — ghosts move seconds toward midnight.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/doomsday-bind-hand",
        "well_known": f"{base}/.well-known/doomsday-bind-hand.json",
    }
