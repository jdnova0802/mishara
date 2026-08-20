"""Double-Bind Dissolver — Bateson: soft-yes creates binds; the mouth cuts them.

Double bind: contradictory injunctions with no exit ("be autonomous / obey").
Ops form: "fail closed" + "never block revenue" with no exclusive door.
Gate dissolves the bind by making HALT/ALLOW a single alphabet on one weld —
exit is always nameable. Copycats leave the bind and call it culture.

Gatekeep only to ourselves: Bateson double bind → mouth as exit grammar.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-double-bind-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def dissolve(
    *,
    fail_closed_said: bool | None = None,
    never_block_revenue_said: bool | None = None,
    exclusive_door: bool | None = None,
    decision: str | None = None,
) -> dict[str, Any]:
    fc = bool(fail_closed_said)
    nbr = bool(never_block_revenue_said)
    door = bool(exclusive_door)
    d = (decision or "").upper()
    if fc and nbr and not door:
        posture = "double_bind_active"
        claim = "contradictory_injunctions_no_exit"
    elif door and d in ("HALT", "BLOCK", "ALLOW"):
        posture = "bind_dissolved"
        claim = "mouth_alphabet_names_the_exit"
    elif door:
        posture = "exit_available"
        claim = "exclusive_door_ready_awaiting_decision"
    else:
        posture = "unevaluated"
        claim = "insufficient_injunction_data"
    return {
        "spec": SPEC,
        "name": "Double-Bind Dissolver",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Gregory Bateson — double bind theory",
            "Gate — exclusive door + ALLOW/HALT/BLOCK as exit grammar",
        ],
        "fail_closed_said": fc,
        "never_block_revenue_said": nbr,
        "exclusive_door": door,
        "decision": d or None,
        "posture": posture,
        "claim": claim,
        "thesis": "Contradictory slogans without a mouth are a double bind. The weld cuts it.",
        "gatekeep": "Proprietary Bateson framing for Gate doors. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Double-Bind Dissolver",
        "inventor": INVENTOR,
        "example_bind": dissolve(fail_closed_said=True, never_block_revenue_said=True, exclusive_door=False),
        "example_exit": dissolve(
            fail_closed_said=True, never_block_revenue_said=True, exclusive_door=True, decision="HALT"
        ),
        "live": f"{base}/.well-known/double-bind.json",
        "variety": f"{base}/.well-known/variety.json",
        "their_production": False,
    }
