"""Metastable HALT — Simondon: individuation waits in supersaturated DEAD.

Before CHARGE, the fuse is metastable — charged with potential LIVE but not
yet individuated into permitted spend. Soft-yes is a false individuation
(premature form). CHARGE is the costly nucleation that resolves metastability
into a welded individual act. Copycats skip metastability and ship LIVE toggles.

Gatekeep only to ourselves: Simondon individuation → metastable mouth.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-metastable-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def assay(
    *,
    fuse_live: bool | None = None,
    charge_id: str | None = None,
    soft_yes: bool | None = None,
) -> dict[str, Any]:
    live = bool(fuse_live)
    charge = bool((charge_id or "").strip())
    soft = bool(soft_yes)
    if not live and not charge and not soft:
        phase = "metastable_dead"
        claim = "supersaturated_potential_awaits_costly_nucleation"
    elif soft and not charge and not live:
        phase = "false_individuation"
        claim = "soft_yes_is_premature_form_without_charge"
    elif charge and live:
        phase = "individuated_live"
        claim = "charge_nucleated_permitted_spend"
    elif not live and charge:
        phase = "nucleation_in_progress"
        claim = "witness_present_status_pending"
    else:
        phase = "unevaluated"
        claim = "insufficient_phase_data"
    return {
        "spec": SPEC,
        "name": "Metastable HALT",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Gilbert Simondon — individuation, metastability, transduction",
            "Gate — DEAD as metastable; CHARGE as costly nucleation",
        ],
        "phase": phase,
        "claim": claim,
        "fuse_live": live,
        "charge_present": charge,
        "soft_yes": soft,
        "thesis": "DEAD is not empty — it is metastable. CHARGE individuates.",
        "gatekeep": "Proprietary Simondon framing of DEAD/CHARGE. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Metastable HALT",
        "inventor": INVENTOR,
        "example_metastable": assay(fuse_live=False, charge_id=None, soft_yes=False),
        "example_false": assay(fuse_live=False, soft_yes=True),
        "live": f"{base}/.well-known/metastable.json",
        "clinamen": f"{base}/.well-known/clinamen.json",
        "their_production": False,
    }
