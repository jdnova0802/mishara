"""Xenometric — clearance is not denominated in money, risk, or confidence.

Earth asks 'how much risk'. This chassis does not have that unit. Native
quantities: door occupancy (0/1), sector (DEAD|LIVE|HALT), CHARGE presence
(0/1), horizon distance (collapsed|extended), fetchability (0/1). Any
map into USD, bps, or percent is a lossy Earth adapter for invoices —
not the state of the machine.

Not Earth-side: we still bill in Earth money. The mouth does not think in it.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-xenometric-v1"
INVENTOR = "Nisaba LLC / Gate"

NATIVE = (
    "door_occupancy",
    "sector",
    "charge_bit",
    "horizon_distance",
    "antenna_fetchable",
)

FORBIDDEN_UNITS = ("risk_percent", "confidence", "usd_as_permission", "bps_as_live")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def measure(*, unit: str | None = None) -> dict[str, Any]:
    u = (unit or "").strip().lower()
    if u in FORBIDDEN_UNITS or u.endswith("_kpi") or u in ("usd", "percent"):
        posture = "earth_unit_rejected"
        claim = "not_a_native_observable"
    elif u in NATIVE or not u:
        posture = "native"
        claim = "chassis_quantities_only"
    else:
        posture = "unknown_unit"
        claim = "translate_or_discard"
    return {
        "spec": SPEC,
        "name": "Xenometric",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "native_quantities": list(NATIVE),
        "forbidden_units": list(FORBIDDEN_UNITS),
        "unit": u or None,
        "posture": posture,
        "claim": claim,
        "thesis": "The invoice may speak USD. The mouth does not speak USD.",
        "gatekeep": "Proprietary xenometric. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Xenometric",
        "inventor": INVENTOR,
        "example_native": measure(unit="sector"),
        "example_earth": measure(unit="risk_percent"),
        "live": f"{base}/.well-known/xenometric.json",
        "incommensurable": f"{base}/.well-known/incommensurable.json",
        "their_production": False,
    }
