"""FedNow Mouth — irrevocable instant-rail pre-release.

OC 8: settlement final when debits/credits record. No ACH float.
Post-hoc kill governs nothing. Mouth must sit before release.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-fednow-mouth-v1"
INVENTOR = "Nisaba LLC / Gate"

IRREVOCABLE_RAILS = ("fednow", "rtp", "wire", "crypto_l1")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def pre_release(
    *,
    rail: str | None = None,
    hop_permit: bool | None = None,
    charge_id: str | None = None,
    soft_yes: bool | None = None,
) -> dict[str, Any]:
    r = (rail or "fednow").strip().lower()
    permit = bool(hop_permit)
    soft = bool(soft_yes)
    irrevocable = r in IRREVOCABLE_RAILS
    if soft and not charge_id:
        posture = "soft_yes_rejected"
        claim = "charge_only_on_irrevocable_rail"
        allow = False
    elif irrevocable and not permit:
        posture = "pre_release_halt"
        claim = "no_pay_away_without_mouth"
        allow = False
    elif irrevocable and permit:
        posture = "pre_release_cleared"
        claim = "mouth_before_instant_finality"
        allow = True
    else:
        posture = "non_instant_rail"
        claim = "still_fail_closed"
        allow = permit
    return {
        "spec": SPEC,
        "name": "FedNow Mouth",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "FedNow Operating Circular 8 — settlement finality",
            "RTP / TCH irrevocable instant payments",
            "IMF 2026 agentic payments — ex-ante interruption",
        ],
        "rail": r,
        "irrevocable": irrevocable,
        "hop_permit": permit,
        "charge_id": charge_id,
        "soft_yes": soft,
        "posture": posture,
        "claim": claim,
        "allow_release": allow,
        "thesis": "On irrevocable rails, the mouth is the only control that exists.",
        "gatekeep": "Proprietary FedNow mouth. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "FedNow Mouth",
        "inventor": INVENTOR,
        "example_halt": pre_release(rail="fednow", hop_permit=False),
        "example_soft_reject": pre_release(rail="fednow", hop_permit=True, soft_yes=True),
        "live": f"{base}/.well-known/fednow-mouth.json",
        "hardest": f"{base}/.well-known/hardest.json",
        "their_production": False,
    }
