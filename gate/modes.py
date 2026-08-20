"""Modes of Clearance — Latour: [TEC] hop is not [LAW] permission.

Modes of existence: different felicity conditions. A technical success
(bind API 200) is not a legal/permission success (LIVE under license).
Gate attaches modes explicitly so partners stop smuggling TEC into LAW.
Crossing modes without CHARGE is category error — and a spend hazard.

Gatekeep only to ourselves: Latour modes → refuse TEC→LAW smuggling.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-modes-v1"
INVENTOR = "Nisaba LLC / Gate"

MODES = (
    ("TEC", "technical hop success — latency, 200, schema"),
    ("LAW", "licensed permission — LIVE parent, CHARGE, exclusive door"),
    ("REF", "reference / evidence — receipt hash, verify fetch"),
    ("ORG", "organizational — weld economics, operator skin"),
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def classify(
    *,
    tec_ok: bool | None = None,
    law_live: bool | None = None,
    charge_id: str | None = None,
    claimed_permission: bool | None = None,
) -> dict[str, Any]:
    tec = bool(tec_ok)
    law = bool(law_live)
    charge = bool((charge_id or "").strip())
    claimed = bool(claimed_permission)
    if claimed and tec and not law and not charge:
        posture = "mode_smuggle"
        claim = "tec_success_smuggled_as_law_permission"
    elif law and (charge or law):
        posture = "modes_aligned"
        claim = "law_permission_not_inferred_from_tec_alone"
    elif tec and not claimed:
        posture = "tec_honest"
        claim = "technical_success_without_permission_claim"
    else:
        posture = "unevaluated"
        claim = "insufficient_mode_data"
    return {
        "spec": SPEC,
        "name": "Modes of Clearance",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Bruno Latour — An Inquiry into Modes of Existence (AIME)",
            "Gate performative + costliness — LAW mode requires CHARGE",
        ],
        "modes": [{"id": a, "meaning": b} for a, b in MODES],
        "tec_ok": tec,
        "law_live": law,
        "charge_present": charge,
        "claimed_permission": claimed,
        "posture": posture,
        "claim": claim,
        "thesis": "HTTP 200 is not LIVE. Modes do not smuggle.",
        "gatekeep": "Proprietary Latour modes doctrine for Gate. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Modes of Clearance",
        "inventor": INVENTOR,
        "example_smuggle": classify(tec_ok=True, law_live=False, claimed_permission=True),
        "example_aligned": classify(tec_ok=True, law_live=True, charge_id="chg_1", claimed_permission=True),
        "live": f"{base}/.well-known/modes.json",
        "performative": f"{base}/.well-known/performative.json",
        "their_production": False,
    }
