"""Deviance Breaker — Vaughan: soft-yes is normalized deviance; the mouth denormalizes.

Diane Vaughan: disasters grow from deviance made normal. Ops form: UW
approve without CHARGE becomes 'how we ship'. Gate denormalizes: each
soft-yes is classified as not-LIVE, published as restraint when it HALTs,
never promoted by familiarity. Copycats onboard the deviance.

Gatekeep only to ourselves: normalization of deviance → mouth as denormalizer.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-deviance-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def denormalize(
    *,
    familiar_soft_yes: bool | None = None,
    charge_id: str | None = None,
    decision: str | None = None,
) -> dict[str, Any]:
    fam = bool(familiar_soft_yes)
    charge = bool((charge_id or "").strip())
    d = (decision or "").upper()
    if fam and not charge and d == "ALLOW":
        posture = "deviance_normalized"
        claim = "familiarity_promoted_soft_yes_to_live"
    elif fam and d in ("HALT", "BLOCK"):
        posture = "denormalized"
        claim = "mouth_refused_to_let_familiarity_become_physics"
    elif fam and not charge:
        posture = "deviance_visible"
        claim = "soft_yes_named_as_not_live"
    else:
        posture = "no_deviance_signal"
        claim = "unevaluated"
    return {
        "spec": SPEC,
        "name": "Deviance Breaker",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Diane Vaughan — normalization of deviance (Challenger)",
            "Gate apophatic + parasite filter — familiarity ≠ CHARGE",
        ],
        "familiar_soft_yes": fam,
        "charge_present": charge,
        "decision": d or None,
        "posture": posture,
        "claim": claim,
        "thesis": "How we always do it is not LIVE. The mouth denormalizes.",
        "gatekeep": "Proprietary deviance-breaker doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Deviance Breaker",
        "inventor": INVENTOR,
        "example_norm": denormalize(familiar_soft_yes=True, decision="ALLOW"),
        "example_broke": denormalize(familiar_soft_yes=True, decision="HALT"),
        "live": f"{base}/.well-known/deviance.json",
        "apophatic": f"{base}/.well-known/apophatic.json",
        "their_production": False,
    }
