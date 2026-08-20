"""PvP Mouth — Herstatt bite. Two FX legs linked; no solo pay-away.

CLS remains the FMI apex for PvP. Gate mouths each irreversible release
before a leg can fire without its counter-leg permission. ~$1.4T/day still
gross bilateral (BIS 2025) — that is the residual Gate addresses at the hop.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-pvp-mouth-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def link_legs(
    *,
    pay_leg_cleared: bool | None = None,
    receive_leg_armed: bool | None = None,
    pvp_eligible: bool | None = None,
) -> dict[str, Any]:
    pay = bool(pay_leg_cleared)
    recv = bool(receive_leg_armed)
    eligible = True if pvp_eligible is None else bool(pvp_eligible)
    if pay and not recv:
        posture = "herstatt_exposure"
        claim = "solo_pay_away_blocked"
        allow = False
    elif pay and recv:
        posture = "legs_linked"
        claim = "pvp_mouth_permit"
        allow = True
    else:
        posture = "awaiting_legs"
        claim = "no_release"
        allow = False
    return {
        "spec": SPEC,
        "name": "PvP Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Herstatt Bank 1974 — FX principal risk",
            "CLSSettlement PvP — FMI apex unchanged",
            "BIS Triennial 2025 — residual gross bilateral",
            "Gate DvP mouth — same physics, FX legs",
        ],
        "pay_leg_cleared": pay,
        "receive_leg_armed": recv,
        "pvp_eligible": eligible,
        "posture": posture,
        "claim": claim,
        "allow_release": allow,
        "thesis": "No solo pay-away. Counter-leg armed or HALT.",
        "not": "replace CLS; invent new currency eligibility",
        "gatekeep": "Proprietary PvP mouth. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "PvP Mouth",
        "inventor": INVENTOR,
        "example_herstatt_blocked": link_legs(pay_leg_cleared=True, receive_leg_armed=False),
        "example_linked": link_legs(pay_leg_cleared=True, receive_leg_armed=True),
        "live": f"{base}/.well-known/pvp-mouth.json",
        "hardest": f"{base}/.well-known/hardest.json",
        "their_production": False,
    }
