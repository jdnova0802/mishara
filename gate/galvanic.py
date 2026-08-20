"""Galvanic Isolation — PII never shares a ground with PAS or public nos.

Analog hardware: galvanic isolation stops current sharing between domains.
Gate: inhabitant PII, PAS hop, and stranger antenna are isolated planes.
A receipt that leaks PII is a ground fault. Copycats bond the planes
for 'richer analytics'. Gate keeps the optocoupler: CHARGE/HALT only.

Gatekeep only to ourselves: galvanic isolation → no PII on PAS/public.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-galvanic-v1"
INVENTOR = "Nisaba LLC / Gate"

PLANES = ("inhabitant_pii", "pas_hop", "stranger_antenna")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def isolate(*, pii_on_pas: bool | None = None, pii_on_antenna: bool | None = None) -> dict[str, Any]:
    pas = bool(pii_on_pas)
    ant = bool(pii_on_antenna)
    if pas or ant:
        posture = "ground_fault"
        claim = "pii_bonded_to_public_or_pas_plane"
    else:
        posture = "isolated"
        claim = "planes_share_only_charge_halt_signals"
    return {
        "spec": SPEC,
        "name": "Galvanic Isolation",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Galvanic isolation / optocouplers — no shared ground between domains",
            "Gate hard constraint — no PII on PAS or public restraint",
        ],
        "planes": list(PLANES),
        "pii_on_pas": pas,
        "pii_on_antenna": ant,
        "posture": posture,
        "claim": claim,
        "thesis": "Analytics that bond PII to the hop are a ground fault, not a feature.",
        "gatekeep": "Proprietary galvanic-isolation doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Galvanic Isolation",
        "inventor": INVENTOR,
        "example_ok": isolate(pii_on_pas=False, pii_on_antenna=False),
        "example_fault": isolate(pii_on_pas=True),
        "live": f"{base}/.well-known/galvanic.json",
        "stranger_antenna": f"{base}/.well-known/stranger-antenna.json",
        "their_production": False,
    }
