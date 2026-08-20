"""Exergy of Clearance — useful work of status change vs dashboard waste heat.

Exergy: maximum useful work extractable from a system relative to environment.
Gate: CHARGE→LIVE is high-exergy work (status actually changes under costliness).
Risk dashboards, AI badges, and policy PDFs are low-exergy heat — they
dissipate attention without changing the weld. Copycats sell heat.

Gatekeep only to ourselves: thermodynamics metaphor → exergy ranking of acts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-exergy-v1"
INVENTOR = "Nisaba LLC / Gate"

EXERGY_RANK = (
    ("charge_dead_to_live", "high", "changes weld status with costly witness"),
    ("halt_under_pressure", "high", "preserves optionality against soft-yes"),
    ("exclusive_door_block", "medium", "removes a bypass path"),
    ("restraint_publish", "medium", "citeable no enters public inventory"),
    ("risk_dashboard", "low", "heat — attention without status change"),
    ("ai_governance_pdf", "waste", "heat — costume without mouth"),
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def rank(*, act: str | None = None) -> dict[str, Any]:
    a = (act or "").strip().lower()
    match = next((r for r in EXERGY_RANK if r[0] == a), None)
    if match:
        level = match[1]
        meaning = match[2]
    elif a.startswith("charge") or a == "halt":
        level = "high"
        meaning = "status-relevant mouth act"
    elif a.startswith("dashboard") or a.startswith("pdf") or a.startswith("badge"):
        level = "waste"
        meaning = "heat without weld change"
    else:
        level = "unknown"
        meaning = "classify against exergy table"
    return {
        "spec": SPEC,
        "name": "Exergy of Clearance",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Thermodynamic exergy — useful work vs environment",
            "Gate — prefer high-exergy status acts; refuse waste-heat governance",
        ],
        "table": [
            {"act": x, "exergy": y, "meaning": z} for x, y, z in EXERGY_RANK
        ],
        "act": a or None,
        "exergy": level,
        "meaning": meaning,
        "thesis": "Sell useful work on the weld. Do not sell dashboard heat.",
        "gatekeep": "Proprietary exergy ranking of clearance acts. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Exergy of Clearance",
        "inventor": INVENTOR,
        "example_high": rank(act="charge_dead_to_live"),
        "example_waste": rank(act="ai_governance_pdf"),
        "live": f"{base}/.well-known/exergy.json",
        "via_negativa": f"{base}/.well-known/via-negativa.json",
        "their_production": False,
    }
