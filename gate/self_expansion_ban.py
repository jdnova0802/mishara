"""Self-Expansion Ban — agents cannot widen their own LIVE.

arXiv 2605.01415: self-expansion authority S_exp is a sovereignty boundary.
Userspace promoting itself to LIVE is an illegal opcode.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-self-expansion-ban-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def police(
    *,
    self_issued_live: bool | None = None,
    widened_scope: bool | None = None,
    charge_id: str | None = None,
) -> dict[str, Any]:
    self_live = bool(self_issued_live)
    widen = bool(widened_scope)
    if self_live or (widen and not charge_id):
        posture = "expansion_blocked"
        claim = "illegal_self_promotion"
        ok = False
    else:
        posture = "expansion_sealed"
        claim = "only_charge_widens_regime"
        ok = True
    return {
        "spec": SPEC,
        "name": "Self-Expansion Ban",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "arXiv 2605.01415 — sovereignty boundary S_exp",
            "Gate privilege rings — ring 0 is CHARGE",
            "Mouth ISA — soft-yes illegal opcode",
        ],
        "self_issued_live": self_live,
        "widened_scope": widen,
        "charge_id": charge_id,
        "posture": posture,
        "claim": claim,
        "passes": ok,
        "thesis": "You cannot grant yourself LIVE. CHARGE is exterior.",
        "gatekeep": "Proprietary self-expansion ban. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Self-Expansion Ban",
        "inventor": INVENTOR,
        "example_blocked": police(self_issued_live=True),
        "example_ok": police(widened_scope=True, charge_id="chg_1"),
        "live": f"{base}/.well-known/self-expansion-ban.json",
        "hardest": f"{base}/.well-known/hardest.json",
        "their_production": False,
    }
