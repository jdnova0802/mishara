"""Knightian HALT — unmeasurable uncertainty is HALT, not a fake probability of LIVE.

Frank Knight: risk is measurable; uncertainty is not. Gate: when the hop
cannot be measured into a CHARGE witness (missing fuse, unknown door,
garbage clock), that is uncertainty — HALT. A softmax '0.81 LIVE' is
fake risk. Copycats price Knightian fog as if it were casinos.

Gatekeep only to ourselves: Knightian uncertainty → HALT, not a calibrated yes.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-knightian-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def face(
    *,
    measurable_witness: bool | None = None,
    fake_probability: bool | None = None,
    decision: str | None = None,
) -> dict[str, Any]:
    meas = bool(measurable_witness)
    fake = bool(fake_probability)
    d = (decision or "").upper()
    if fake and d == "ALLOW":
        posture = "fake_risk"
        claim = "softmax_is_not_a_charge_witness"
    elif not meas and d in ("HALT", "BLOCK"):
        posture = "knightian_halt"
        claim = "unmeasurable_uncertainty_does_not_become_live"
    elif meas:
        posture = "risk_or_witness_present"
        claim = "measurable_path_may_charge"
    else:
        posture = "unevaluated"
        claim = "no_uncertainty_assay"
    return {
        "spec": SPEC,
        "name": "Knightian HALT",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Frank Knight — risk vs uncertainty",
            "Gate fail-closed — unknown is HALT, not 81%",
        ],
        "measurable_witness": meas,
        "fake_probability": fake,
        "decision": d or None,
        "posture": posture,
        "claim": claim,
        "thesis": "Fog is not a probability of LIVE. Fog is HALT.",
        "gatekeep": "Proprietary Knightian-HALT doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Knightian HALT",
        "inventor": INVENTOR,
        "example_halt": face(measurable_witness=False, decision="HALT"),
        "example_fake": face(fake_probability=True, decision="ALLOW"),
        "live": f"{base}/.well-known/knightian.json",
        "nmi_halt": f"{base}/.well-known/nmi-halt.json",
        "their_production": False,
    }
