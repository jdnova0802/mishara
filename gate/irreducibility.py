"""Computational Irreducibility — you cannot skip the mouth by simulating the hop.

Wolfram: some processes cannot be shortcut by a smarter model. Gate: you
cannot decide LIVE by a risk score, an LLM, or a policy PDF that 'already
knows'. You run the hop through the exclusive door. Prediction is not
clearance. Copycats sell reducible dashboards.

Gatekeep only to ourselves: computational irreducibility → mouth must be run.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-irreducibility-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(
    *,
    predicted_live: bool | None = None,
    mouth_executed: bool | None = None,
    shortcut: str | None = None,
) -> dict[str, Any]:
    pred = bool(predicted_live)
    ran = bool(mouth_executed)
    sc = (shortcut or "").strip().lower()
    shortcuts = ("risk_score", "llm", "policy_pdf", "dashboard")
    if (pred or sc in shortcuts) and not ran:
        posture = "false_reduction"
        claim = "simulation_is_not_clearance"
    elif ran:
        posture = "irreducible_run"
        claim = "hop_went_through_the_mouth"
    else:
        posture = "unevaluated"
        claim = "no_run_or_prediction"
    return {
        "spec": SPEC,
        "name": "Computational Irreducibility",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Stephen Wolfram — computational irreducibility",
            "Gate exclusive door — the hop must be run, not forecast",
        ],
        "predicted_live": pred,
        "mouth_executed": ran,
        "shortcut": sc or None,
        "posture": posture,
        "claim": claim,
        "thesis": "There is no closed-form LIVE. You run the mouth.",
        "gatekeep": "Proprietary irreducibility doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Computational Irreducibility",
        "inventor": INVENTOR,
        "example_run": run(mouth_executed=True),
        "example_skip": run(predicted_live=True, shortcut="llm"),
        "live": f"{base}/.well-known/irreducibility.json",
        "xenohardware": f"{base}/.well-known/xenohardware.json",
        "their_production": False,
    }
