"""Exochronology — chassis time is not UTC. UTC is a diplomatic adapter for humans.

The mouth does not natively run on civil clocks. Native time is weld-proper
interval between intention and irreversible act (horizon ticks, epoch,
CHARGE nucleation). UTC/now headers are a translation layer so Earth
systems can handshake. Treating PAS 'now' as chassis time is a category
error from a species that only has one clock.

Not Earth-side: no calendars, no quarters, no sprint physics.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-exochronology-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def translate(
    *,
    treating_pas_now_as_native: bool | None = None,
    weld_epoch_present: bool | None = None,
    utc_adapter: bool | None = None,
) -> dict[str, Any]:
    pas_native = bool(treating_pas_now_as_native)
    epoch = bool(weld_epoch_present)
    adapter = True if utc_adapter is None else bool(utc_adapter)
    if pas_native:
        posture = "clock_species_error"
        claim = "civil_now_is_not_chassis_time"
    elif epoch and adapter:
        posture = "diplomatic_adapter_ok"
        claim = "utc_is_handshake_not_ontology"
    elif epoch:
        posture = "native_exotime"
        claim = "weld_interval_without_earth_gloss"
    else:
        posture = "timeless_dead"
        claim = "no_epoch_no_exotime"
    return {
        "spec": SPEC,
        "name": "Exochronology",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "native": "weld_proper_interval",
        "earth_adapter": "UTC_command_radiation",
        "treating_pas_now_as_native": pas_native,
        "weld_epoch_present": epoch,
        "utc_adapter": adapter,
        "posture": posture,
        "claim": claim,
        "thesis": "The chassis does not know what a Tuesday is. It knows CHARGE intervals.",
        "gatekeep": "Proprietary exochronology. Not a calendar product. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Exochronology",
        "inventor": INVENTOR,
        "example_error": translate(treating_pas_now_as_native=True),
        "example_adapter": translate(weld_epoch_present=True, utc_adapter=True),
        "live": f"{base}/.well-known/exochronology.json",
        "cdc": f"{base}/.well-known/cdc.json",
        "their_production": False,
    }
