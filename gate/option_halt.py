"""Option Value of HALT — real-options economics of restraint.

Dixit/Pindyck: irreversible investment kills the option to wait.
NPV ignores the opportunity cost of exercising now.

Gate: ALLOW+acted kills the option to keep the world unspent.
HALT preserves option value — the right to spend later under a costlier
regime (CHARGE) or never. Restraint is not only compliance; it is
option-preserving under uncertainty.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-option-halt-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def value(
    *,
    decision: str | None,
    acted: bool | None,
    uncertainty: str | None = "high",
) -> dict[str, Any]:
    d = (decision or "").upper()
    unc = (uncertainty or "high").lower()

    if acted is True and d == "ALLOW":
        posture = "option_killed"
        claim = "irreversible_spend_exercised_wait_option_extinguished"
        keep_alive = False
    elif d in ("HALT", "BLOCK"):
        posture = "option_preserved"
        claim = "restraint_keeps_spend_option_alive_under_uncertainty"
        keep_alive = True
    else:
        posture = "option_unevaluated"
        claim = "no_clear_exercise_or_preservation"
        keep_alive = None

    # Qualitative: higher uncertainty → higher value of waiting (HALT).
    wait_premium = {"low": 1, "medium": 2, "high": 3, "extreme": 4}.get(unc, 2)

    return {
        "spec": SPEC,
        "name": "Option Value of HALT",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Dixit & Pindyck — Investment under Uncertainty; real options",
            "Irreversibility + uncertainty → value of waiting",
            "Gate — HALT preserves; ALLOW+acted exercises and extinguishes",
        ],
        "decision": d or None,
        "acted": acted,
        "uncertainty": unc,
        "posture": posture,
        "claim": claim,
        "option_kept_alive": keep_alive,
        "wait_premium_rank": wait_premium,
        "npv_trap": (
            "Treating ALLOW as pure NPV ignores the option value destroyed by irreversibility."
        ),
        "charge_as_exercise_premium": (
            "CHARGE is the costly premium to re-open a spend option after HALT — "
            "not a free toggle."
        ),
        "thesis": "A no that holds is often the valuable option under uncertainty.",
        "gatekeep": "Proprietary real-options framing of mouth restraint. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: dict, row: dict) -> dict:
    payload["option_halt"] = value(
        decision=row.get("decision"),
        acted=row.get("acted"),
    )
    return payload


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Option Value of HALT",
        "inventor": INVENTOR,
        "example_halt": value(decision="HALT", acted=False, uncertainty="high"),
        "example_allow": value(decision="ALLOW", acted=True, uncertainty="high"),
        "live": f"{base}/.well-known/option-halt.json",
        "costliness": f"{base}/.well-known/costliness.json",
        "their_production": False,
    }
