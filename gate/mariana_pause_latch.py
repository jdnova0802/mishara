"""Mariana Pause Latch — BIS wCBDC pause without operator unpause.

Real institution: BIS Project Mariana (SNB, Banque de France, BIS Innovation Hub).
Requirement T3: each central bank may pause wCBDC transactions on-chain — but
central bank can also unpause itself.

Twist: Mariana Pause Latch — pause sticks until Velaru CHARGE. Operator cannot
self-unpause. Non-resurrecting HALT beats programmable kill switch.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-mariana-pause-latch-v1"
INVENTION = "Mariana Pause Latch"
FAMILY = "institutional-twist"

REAL = {
    "institution": "Bank for International Settlements",
    "project": "Project Mariana — wholesale CBDC AMM",
    "requirement": "T3 — central bank may pause wCBDC transactions",
    "requirement_alias": "C.3 (final report numbering)",
    "gap_they_leave": "Pauser can unpause — operator-resurrectable",
    "url": "https://www.bis.org/publ/othp_mariana.pdf",
}


def evaluate(
    *,
    paused: bool | None = None,
    pause_authority: str | None = None,
    charge_id: str | None = None,
    self_unpause_attempt: bool | None = None,
) -> dict[str, Any]:
    if paused and self_unpause_attempt and not charge_id:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "real_institution": REAL,
            "verdict": "PAUSE_STICKS",
            "may_unpause": False,
            "reason": "mariana_pause_latch — no self-unpause without CHARGE",
            "vs_bis": "Requirement T3 pause without Requirement T3 unpause for operator.",
        }
    if paused and charge_id:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "verdict": "REGIME_CHANGE",
            "may_unpause": True,
            "charge_id": charge_id,
        }
    if paused:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "verdict": "PAUSED",
            "may_unpause": False,
            "pause_authority": pause_authority,
        }
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "verdict": "LIVE",
        "may_unpause": True,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "BIS Mariana T3 pause — without operator self-unpause. Epoch lock for CBDC class.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/mariana-pause-latch",
        "well_known": f"{base}/.well-known/mariana-pause-latch.json",
    }
