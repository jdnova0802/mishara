"""Xenohardware Chassis — the mouth is apparatus, not a dashboard skin.

Alien-like: a chassis whose ports, vacuum, and fail-closed seals do not
map onto SaaS screens. You weld to it. You do not theme it. Copycats
clone pixels; they cannot clone a chassis that only speaks ALLOW/HALT/BLOCK
on an exclusive bus.

Gatekeep only to ourselves: xenohardware → mouth as non-UI apparatus.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-xenohardware-v1"
INVENTOR = "Nisaba LLC / Gate"

PORTS = (
    ("exclusive_door", "only hop bus that can request irreversible spend"),
    ("charge_port", "sole DEAD→LIVE flash; no JTAG of admin toggles"),
    ("verify_antenna", "stranger-readable evidence, no PII"),
    ("restraint_vent", "published nos leave the chassis; they do not hide"),
    ("license_fuse", "parent LIVE is chassis power; children cannot outlive it"),
)

ILLEGAL_PORTS = (
    "admin_live_jtag",
    "uw_approve_sideband",
    "dashboard_permission_gpio",
    "demo_production_strap",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def chassis(
    *,
    exclusive_door: bool | None = None,
    charge_port: bool | None = None,
    illegal_port: str | None = None,
) -> dict[str, Any]:
    door = bool(exclusive_door)
    charge = True if charge_port is None else bool(charge_port)
    illegal = (illegal_port or "").strip().lower()
    if illegal and illegal in ILLEGAL_PORTS:
        posture = "chassis_breach"
        claim = "illegal_port_is_not_xenohardware_it_is_a_skin"
    elif door and charge:
        posture = "sealed_chassis"
        claim = "alien_apparatus_ports_only"
    elif not door:
        posture = "open_frame"
        claim = "no_exclusive_bus_not_a_chassis"
    else:
        posture = "incomplete_seal"
        claim = "missing_charge_port_or_door"
    return {
        "spec": SPEC,
        "name": "Xenohardware Chassis",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Hardware chassis / fail-closed seals — not UX metaphor",
            "Lem / Strugatsky — artifact whose ports you do not renegotiate",
            "Gate exclusive door + CHARGE port + license fuse",
        ],
        "ports": [{"id": a, "function": b} for a, b in PORTS],
        "illegal_ports": list(ILLEGAL_PORTS),
        "exclusive_door": door,
        "charge_port": charge,
        "illegal_port": illegal or None,
        "posture": posture,
        "claim": claim,
        "thesis": "If it has a themeable UI for LIVE, it is not the chassis.",
        "gatekeep": "Proprietary xenohardware chassis doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Xenohardware Chassis",
        "inventor": INVENTOR,
        "example_sealed": chassis(exclusive_door=True, charge_port=True),
        "example_breach": chassis(exclusive_door=True, illegal_port="admin_live_jtag"),
        "live": f"{base}/.well-known/xenohardware.json",
        "moat": f"{base}/.well-known/moat.json",
        "their_production": False,
    }
