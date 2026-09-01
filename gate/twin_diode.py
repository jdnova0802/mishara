"""Twin Diode — digital twin may read plant; write requires Secure Write Macro + LIVE.

Invention (NORTH_STAR applicable-now): OT buyers fear twin→PLC. Diode is the
pitch — read path soft; write path forge-grade mouth.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-twin-diode-v1"
INVENTION = "Twin Diode"
FAMILY = "applicable_now"

DIR_READ = "read"
DIR_WRITE = "write"
VERDICT_PASS = "PASS"
VERDICT_BLOCK = "BLOCK"
VERDICT_CHOKE = "CHOKE"

REASON_WRITE_WITHOUT_MACRO = "twin_write_without_secure_macro"
REASON_WRITE_WITHOUT_LIVE = "twin_write_without_live"
REASON_SIM_AS_LIVE = "sim_treated_as_live"
REASON_OK_READ = "read_path_open"
REASON_OK_WRITE = "secure_macro_and_live"


def evaluate(
    *,
    direction: str | None = None,
    secure_write_macro: bool | None = None,
    live_cleared: bool | None = None,
    decision: str | None = None,
    sim_only: bool | None = None,
    would_actuate: bool | None = None,
) -> dict[str, Any]:
    d = (direction or "").strip().lower() or (DIR_WRITE if would_actuate else DIR_READ)
    live = bool(live_cleared) or (decision or "").strip().upper() in ("ALLOW", "LIVE", "GO")
    macro = bool(secure_write_macro)

    if d == DIR_READ and not would_actuate:
        return _result(
            VERDICT_PASS,
            direction=DIR_READ,
            reasons=[REASON_OK_READ],
            detail="Twin may read plant — diode open toward observation.",
            may_proceed=True,
        )

    # Write / actuate path
    if sim_only and would_actuate:
        return _result(
            VERDICT_CHOKE,
            direction=DIR_WRITE,
            reasons=[REASON_SIM_AS_LIVE],
            detail="Sim-only twin tried to actuate — Mirror Seal required.",
            may_proceed=False,
        )
    if not macro:
        return _result(
            VERDICT_BLOCK,
            direction=DIR_WRITE,
            reasons=[REASON_WRITE_WITHOUT_MACRO],
            detail="Twin write without Secure Write Macro — diode blocks.",
            may_proceed=False,
        )
    if not live:
        return _result(
            VERDICT_CHOKE,
            direction=DIR_WRITE,
            reasons=[REASON_WRITE_WITHOUT_LIVE],
            detail="Secure Macro present but no LIVE — write path chokes.",
            may_proceed=False,
        )
    return _result(
        VERDICT_PASS,
        direction=DIR_WRITE,
        reasons=[REASON_OK_WRITE],
        detail="Secure Write Macro + LIVE — diode opens write path under coordinators.",
        may_proceed=True,
    )


def _result(
    verdict: str,
    *,
    direction: str,
    reasons: list[str],
    detail: str,
    may_proceed: bool,
) -> dict[str, Any]:
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "verdict": verdict,
        "direction": direction,
        "reasons": reasons,
        "may_proceed": may_proceed,
        "detail": detail,
        "rule": "Twin may read. Twin write needs Secure Write Macro + LIVE.",
        "pairs_with": "Mirror Seal · Secure Write Macro · Plant Sheath Starter",
    }


def attach(plan: dict) -> dict:
    plan["twin_diode"] = evaluate(
        direction=plan.get("twin_direction"),
        secure_write_macro=plan.get("secure_write_macro"),
        live_cleared=plan.get("allow_bind") or (plan.get("decision") or "").upper() in ("ALLOW", "LIVE"),
        decision=plan.get("decision"),
        sim_only=plan.get("sim_only"),
        would_actuate=plan.get("would_actuate") or plan.get("write_kind") == "plc_write",
    )
    td = plan["twin_diode"]
    if td.get("direction") == DIR_WRITE and not td.get("may_proceed"):
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or (td.get("reasons") or ["twin_diode_block"])[0]
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Twin may read plant; write path needs Secure Write Macro + LIVE.",
        "demo": f"POST {base}/demo/pas/twin-diode",
        "well_known": f"{base}/.well-known/twin-diode.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. OT foothill — Plant Sheath Starter seed.",
    }
