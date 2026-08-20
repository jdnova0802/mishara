"""Regime Function — FDT-shaped predictability without LessWrong cosplay.

Functional decision theory: treat the decision as output of a fixed function —
which output of *this* function yields the best outcome?

Gate: the mouth is a fixed regime function f(fuse, epoch, license, spend) →
{ALLOW, HALT, BLOCK}. Counterparties (carriers, attestors, processors) can
predict the mouth because the function is published and CHARGE is the only
regime change. Predictability is the product — not Newcomb fanfic.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-regime-function-v1"
INVENTOR = "Nisaba LLC / Gate"

INPUTS = (
    "fuse_state",
    "license_parent_state",
    "epoch_lock",
    "exclusion",
    "spend_fingerprint",
    "ticket_live",
)
OUTPUTS = ("ALLOW", "HALT", "BLOCK")
REGIME_CHANGE = "CHARGE / charge_id / operator weld only"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def evaluate(
    *,
    fuse_live: bool | None = None,
    license_parent_live: bool | None = None,
    license_fused: bool | None = None,
    epoch_locked: bool | None = None,
    ticket_live: bool | None = None,
    exclusion_ok: bool | None = None,
) -> dict[str, Any]:
    """Deterministic sketch of the published regime function."""
    reasons = []
    if fuse_live is False:
        reasons.append("fuse_not_live")
    if license_fused and license_parent_live is False:
        reasons.append("license_parent_not_live")
    if epoch_locked:
        reasons.append("epoch_locked")
    if ticket_live is False:
        reasons.append("ticket_not_live")
    if exclusion_ok is False:
        reasons.append("exclusion_gap")

    if reasons:
        out = "HALT"
    elif fuse_live is True and (not license_fused or license_parent_live is True):
        # ALLOW only when no halt triggers; ticket/exclusion unknown → still not auto-ALLOW
        if ticket_live is True and exclusion_ok is not False:
            out = "ALLOW"
        elif ticket_live is None and exclusion_ok is None and license_fused is not True:
            out = "ALLOW"  # minimal path: live fuse, no license fused
        else:
            out = "HALT"
            if ticket_live is not True:
                reasons.append("ticket_required_or_unknown")
    else:
        out = "HALT"
        reasons.append("insufficient_facts_fail_closed")

    return {
        "spec": SPEC,
        "name": "Regime Function",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Functional decision theory — decide as output of a fixed decision function",
            "Gate epoch / license fuse — published regime; CHARGE-only change",
        ],
        "function": {
            "name": "mouth",
            "inputs": list(INPUTS),
            "outputs": list(OUTPUTS),
            "regime_change": REGIME_CHANGE,
            "fail_closed": True,
        },
        "inputs": {
            "fuse_live": fuse_live,
            "license_parent_live": license_parent_live,
            "license_fused": license_fused,
            "epoch_locked": epoch_locked,
            "ticket_live": ticket_live,
            "exclusion_ok": exclusion_ok,
        },
        "output": out,
        "reasons": reasons,
        "predictability": {
            "claim": "counterparties_can_model_the_mouth_because_f_is_published",
            "not": "Newcomb problems, acausal trade essays, or LessWrong costume",
        },
        "thesis": "The mouth is a fixed function. CHARGE changes the regime. Soft-yes does not.",
        "gatekeep": "Proprietary regime-function framing for clear-before-wire predictability. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Regime Function",
        "inventor": INVENTOR,
        "example_halt": evaluate(fuse_live=True, license_fused=True, license_parent_live=False),
        "example_allow": evaluate(
            fuse_live=True, license_fused=False, ticket_live=True, exclusion_ok=True
        ),
        "live": f"{base}/.well-known/regime-function.json",
        "costliness": f"{base}/.well-known/costliness.json",
        "their_production": False,
    }
