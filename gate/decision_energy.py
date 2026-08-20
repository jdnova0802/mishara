"""Decision Energy Bound — irreversible alphabet limits decision density.

arXiv 2605.01415: safety = control of irreversibility under rising decision-energy.
Gate bounds the alphabet: ALLOW/HALT/BLOCK/CHARGE — not infinite soft scores.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-decision-energy-v1"
INVENTOR = "Nisaba LLC / Gate"

ALPHABET = ("ALLOW", "HALT", "BLOCK", "CHARGE")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def bound(
    *,
    proposed_outcomes: int | None = None,
    soft_score_live: bool | None = None,
) -> dict[str, Any]:
    n = int(proposed_outcomes) if proposed_outcomes is not None else len(ALPHABET)
    soft = bool(soft_score_live)
    if soft:
        posture = "unbounded_density"
        claim = "reject_percent_live"
        ok = False
    elif n > len(ALPHABET):
        posture = "alphabet_overflow"
        claim = "reject_extra_outcomes"
        ok = False
    else:
        posture = "density_bounded"
        claim = "finite_irreversible_alphabet"
        ok = True
    return {
        "spec": SPEC,
        "name": "Decision Energy Bound",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "arXiv 2605.01415 — decision-energy density",
            "Gate Mouth ISA — closed opcode set",
            "Superselection LIVE — no percent-LIVE",
        ],
        "alphabet": list(ALPHABET),
        "proposed_outcomes": n,
        "soft_score_live": soft,
        "posture": posture,
        "claim": claim,
        "passes": ok,
        "thesis": "Irreversible power stays behind a finite alphabet at one door.",
        "gatekeep": "Proprietary decision-energy bound. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Decision Energy Bound",
        "inventor": INVENTOR,
        "example_ok": bound(),
        "example_reject": bound(soft_score_live=True),
        "live": f"{base}/.well-known/decision-energy.json",
        "hardest": f"{base}/.well-known/hardest.json",
        "their_production": False,
    }
