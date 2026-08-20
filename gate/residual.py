"""Residual Control CHARGE — Hart: who may change LIVE is residual control, not a committee.

Grossman-Hart-Moore: when contracts are incomplete, residual rights of
control matter. Gate: the contract of hop/PAS is always incomplete.
Residual control of DEAD→LIVE is CHARGE — not UW, not admin, not the
model. Copycats leave residual control with whoever has the dashboard.

Gatekeep only to ourselves: GHM residual rights → CHARGE holds residual LIVE.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-residual-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def control(*, holder: str | None = None, charge_id: str | None = None) -> dict[str, Any]:
    h = (holder or "").strip().lower()
    charge = bool((charge_id or "").strip())
    bad = h in ("uw", "admin", "dashboard", "model", "committee")
    if bad and not charge:
        posture = "misallocated_residual"
        claim = "dashboard_holds_rights_it_cannot_complete"
    elif charge or h in ("charge", "weld"):
        posture = "residual_with_charge"
        claim = "incomplete_contract_resolved_by_costly_witness"
    else:
        posture = "unallocated"
        claim = "no_holder_named"
    return {
        "spec": SPEC,
        "name": "Residual Control CHARGE",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Grossman-Hart-Moore — residual rights of control under incomplete contracts",
            "Gate CHARGE-only regime change",
        ],
        "holder": h or None,
        "charge_present": charge,
        "posture": posture,
        "claim": claim,
        "thesis": "Contracts will be incomplete. Residual LIVE must sit with CHARGE.",
        "gatekeep": "Proprietary residual-control doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Residual Control CHARGE",
        "inventor": INVENTOR,
        "example_ok": control(holder="charge", charge_id="chg_1"),
        "example_bad": control(holder="admin"),
        "live": f"{base}/.well-known/residual.json",
        "regime_function": f"{base}/.well-known/regime-function.json",
        "their_production": False,
    }
