"""Apophatic Clearance — LIVE is known by what cannot be said without CHARGE.

Apophatic (negative) theology: speak the divine by negation. Gate's LIVE
is apophatic operationally: you cannot affirm permitted irreversible spend
by soft-yes, risk score, or dashboard green — only by costly CHARGE witness.
What LIVE is not: UW approve, demo flag, admin toggle, AI badge.

Gatekeep only to ourselves: apophatic method → CHARGE as sole positive speech.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-apophatic-v1"
INVENTOR = "Nisaba LLC / Gate"

NOT_LIVE = (
    "uw_approve",
    "risk_score_green",
    "dashboard_ok",
    "ai_approved_badge",
    "policy_pdf",
    "demo_hop_success",
    "admin_toggle",
    "soft_yes_email",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def speak(*, claim: str | None = None, charge_id: str | None = None) -> dict[str, Any]:
    c = (claim or "").strip().lower()
    has_charge = bool((charge_id or "").strip())
    if c in ("live", "permitted", "allow_spend") and not has_charge:
        verdict = "apophatic_refusal"
        speech = "cannot_affirm_live_without_charge"
    elif has_charge and c in ("live", "permitted", "allow_spend", ""):
        verdict = "cataphatic_via_charge"
        speech = "charge_is_the_only_positive_speech_of_live"
    elif c in NOT_LIVE or c.startswith("soft_"):
        verdict = "named_as_not_live"
        speech = "negation_holds"
    else:
        verdict = "unevaluated"
        speech = "state_what_it_is_not_first"
    return {
        "spec": SPEC,
        "name": "Apophatic Clearance",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Apophatic theology — knowledge by negation",
            "Gate — LIVE only via CHARGE; everything else is not-LIVE speech",
        ],
        "not_live": list(NOT_LIVE),
        "claim": c or None,
        "charge_present": has_charge,
        "verdict": verdict,
        "speech": speech,
        "thesis": "You may not say LIVE without CHARGE. Negation is the mouth's grammar.",
        "gatekeep": "Proprietary apophatic doctrine of clearance speech. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Apophatic Clearance",
        "inventor": INVENTOR,
        "example_refusal": speak(claim="live", charge_id=None),
        "example_charge": speak(claim="live", charge_id="chg_1"),
        "live": f"{base}/.well-known/apophatic.json",
        "costliness": f"{base}/.well-known/costliness.json",
        "their_production": False,
    }
