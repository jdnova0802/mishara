"""Agential Cut CHARGE — Barad: CHARGE enacts the cut that makes LIVE/DEAD matter.

Agential realism: apparatuses enact cuts that produce phenomena — not
pre-given objects observed from nowhere. Gate's CHARGE is the apparatus
cut: before it, DEAD/LIVE is not yet the spent phenomenon; after it,
permitted irreversible spend exists as a welded mattering. Dashboards
pretend to observe without cutting. Gate refuses the god-trick.

Gatekeep only to ourselves: Barad agential cut → CHARGE as apparatus.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-agential-cut-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def cut(
    *,
    decision: str | None = None,
    acted: bool | None = None,
    charge_id: str | None = None,
) -> dict[str, Any]:
    d = (decision or "").upper()
    acted_b = bool(acted)
    has_charge = bool((charge_id or "").strip())
    if acted_b and d == "ALLOW" and has_charge:
        posture = "cut_enacted_live"
        claim = "charge_apparatus_produced_permitted_spend_phenomenon"
    elif d in ("HALT", "BLOCK"):
        posture = "cut_enacted_restraint"
        claim = "mouth_apparatus_produced_no_as_phenomenon"
    elif acted_b and d == "ALLOW" and not has_charge:
        posture = "cut_without_apparatus"
        claim = "god_trick_allow_without_charge"
    else:
        posture = "pre_cut"
        claim = "phenomenon_not_yet_enacted"
    return {
        "spec": SPEC,
        "name": "Agential Cut CHARGE",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Karen Barad — agential realism; apparatuses enact cuts",
            "Donna Haraway — situated knowledge vs god-trick",
            "Gate — CHARGE/HALT as apparatus, not observation",
        ],
        "decision": d or None,
        "acted": acted_b,
        "charge_present": has_charge,
        "posture": posture,
        "claim": claim,
        "thesis": "CLEAR is not observed. It is enacted by a costly apparatus.",
        "gatekeep": "Proprietary Barad framing of CHARGE as cut. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["agential_cut"] = cut(
        decision=row.get("decision"),
        acted=row.get("acted"),
        charge_id=row.get("charge_id"),
    )
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Agential Cut CHARGE",
        "inventor": INVENTOR,
        "example_live": cut(decision="ALLOW", acted=True, charge_id="chg_1"),
        "example_halt": cut(decision="HALT", acted=False),
        "live": f"{base}/.well-known/agential-cut.json",
        "performative": f"{base}/.well-known/performative.json",
        "their_production": False,
    }
