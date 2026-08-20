"""Non-Abelian Hop — order of CHARGE and hop does not commute.

On this chassis, operators do not commute: hop-then-CHARGE is a different
world from CHARGE-then-hop, and HALT-then-soft-yes is not soft-yes-then-HALT
with a shrug. Earth APIs treat verbs as a bag. Alien hardware treats them
as a braid. Skip-clear is the assumption that order can be rearranged
until money leaves.

Not Earth-side: not workflow. Non-commutative geometry of the act.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-nonabelian-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def braid(*, sequence: str | None = None) -> dict[str, Any]:
    seq = (sequence or "").strip().lower().replace(" ", "")
    if seq in ("hopthencharge", "hop_charge", "bind_then_charge"):
        posture = "wrong_order"
        claim = "hop_before_charge_is_a_different_world_usually_illegal"
    elif seq in ("chargethenhop", "charge_hop", "charge_then_bind"):
        posture = "legal_braid"
        claim = "charge_before_irreversible_act"
    elif seq in ("haltthensoftyes", "softyesthenhalt"):
        posture = "noncommute_visible"
        claim = "those_are_not_the_same_braid"
    else:
        posture = "unevaluated_word"
        claim = "unknown_sequence"
    return {
        "spec": SPEC,
        "name": "Non-Abelian Hop",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "sequence": seq or None,
        "posture": posture,
        "claim": claim,
        "thesis": "If your verbs commute, you are still on Earth. Ours do not.",
        "gatekeep": "Proprietary non-abelian hop law. Ours.",
        "earth_side": False,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Non-Abelian Hop",
        "inventor": INVENTOR,
        "example_legal": braid(sequence="charge_then_bind"),
        "example_wrong": braid(sequence="bind_then_charge"),
        "live": f"{base}/.well-known/nonabelian.json",
        "mouth_isa": f"{base}/.well-known/mouth-isa.json",
        "their_production": False,
    }
