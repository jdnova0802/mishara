"""No-Software LIVE — Kittler: there is no software of permission.

Friedrich Kittler: software is an effect of hardware. LIVE is not a
feature flag, a policy document, or an LLM yes — it is an effect of
CHARGE on welded silicon-equivalent: exclusive door, epoch, fuse.
Dashboards that 'set live' are literature pretending to be physics.

Gatekeep only to ourselves: Kittler hardware a priori → LIVE has no software.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-no-software-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def assay(*, software_live_flag: bool | None = None, charge_id: str | None = None) -> dict[str, Any]:
    flag = bool(software_live_flag)
    charge = bool((charge_id or "").strip())
    if flag and not charge:
        posture = "literature_not_physics"
        claim = "software_cannot_write_live"
    elif charge:
        posture = "hardware_effect"
        claim = "live_is_effect_of_charge_on_chassis"
    else:
        posture = "unwritten"
        claim = "dead_has_no_software_story"
    return {
        "spec": SPEC,
        "name": "No-Software LIVE",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Friedrich Kittler — There is no software; hardware a priori",
            "Gate xenohardware + firmware fuse — LIVE is not a runtime story",
        ],
        "software_live_flag": flag,
        "charge_present": charge,
        "posture": posture,
        "claim": claim,
        "thesis": "There is no software of LIVE. CHARGE is the hardware event.",
        "gatekeep": "Proprietary Kittler doctrine for Gate. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "No-Software LIVE",
        "inventor": INVENTOR,
        "example_literature": assay(software_live_flag=True),
        "example_physics": assay(charge_id="chg_1"),
        "live": f"{base}/.well-known/no-software.json",
        "xenohardware": f"{base}/.well-known/xenohardware.json",
        "their_production": False,
    }
