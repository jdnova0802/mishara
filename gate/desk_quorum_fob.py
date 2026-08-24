"""Desk Quorum Fob — soft N-of-M for high-mass binds (two UW + charge).

Invention (NORTH_STAR applicable-now): Senate Socket for the bind desk.
Sacred / heavy mass expects quorum; light mass may proceed with single mouth.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import stick_meter as stick_mod
except ImportError:
    import stick_meter as stick_mod

SPEC = "gate-desk-quorum-fob-v1"
INVENTION = "Desk Quorum Fob"
FAMILY = "applicable_now"

VERDICT_OK = "QUORUM_OK"
VERDICT_SHORT = "QUORUM_SHORT"
VERDICT_NOT_REQUIRED = "QUORUM_NOT_REQUIRED"


def evaluate(
    *,
    mass_class: str | None = None,
    score: int | None = None,
    uw_approvals: int | None = None,
    charge_present: bool | None = None,
    required_n: int | None = None,
    fob_tokens: list | None = None,
) -> dict[str, Any]:
    mc = (mass_class or "").strip().lower()
    if not mc and score is not None:
        if score >= 75:
            mc = stick_mod.CLASS_SACRED
        elif score >= 40:
            mc = stick_mod.CLASS_HEAVY
        else:
            mc = stick_mod.CLASS_LIGHT

    if mc == stick_mod.CLASS_SACRED:
        need = required_n if required_n is not None else 2
        need_charge = True
    elif mc == stick_mod.CLASS_HEAVY:
        need = required_n if required_n is not None else 2
        need_charge = False
    else:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_NOT_REQUIRED,
            "mass_class": mc or stick_mod.CLASS_LIGHT,
            "required_n": 0,
            "got_n": int(uw_approvals or 0),
            "charge_required": False,
            "charge_present": bool(charge_present),
            "may_proceed": True,
            "detail": "Light mass — single mouth sufficient.",
            "rule": "Heavy/sacred mass needs N-of-M desk quorum; sacred also needs CHARGE.",
        }

    tokens = fob_tokens if isinstance(fob_tokens, list) else []
    got = int(uw_approvals if uw_approvals is not None else len(tokens))
    charge_ok = (not need_charge) or bool(charge_present)
    short = got < need or not charge_ok
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "verdict": VERDICT_SHORT if short else VERDICT_OK,
        "mass_class": mc,
        "required_n": need,
        "got_n": got,
        "charge_required": need_charge,
        "charge_present": bool(charge_present),
        "fob_tokens": tokens,
        "may_proceed": not short,
        "detail": (
            "Quorum short — sacred/heavy bind needs more mouths."
            if short
            else "Desk quorum satisfied under coordinators."
        ),
        "rule": "Heavy/sacred mass needs N-of-M desk quorum; sacred also needs CHARGE.",
        "pairs_with": "Mass Tag · Stick Meter · Charge Bride · Senate Socket",
    }


def attach(plan: dict) -> dict:
    sm = plan.get("stick_meter") if isinstance(plan.get("stick_meter"), dict) else {}
    mt = plan.get("mass_tag") if isinstance(plan.get("mass_tag"), dict) else {}
    result = evaluate(
        mass_class=mt.get("mass_class") or sm.get("mass_class") or plan.get("mass_class"),
        score=sm.get("score"),
        uw_approvals=plan.get("uw_approvals"),
        charge_present=bool(plan.get("charge_id") or plan.get("charge_present")),
        fob_tokens=plan.get("fob_tokens") if isinstance(plan.get("fob_tokens"), list) else None,
    )
    plan["desk_quorum_fob"] = result
    if not result.get("may_proceed") and result.get("verdict") == VERDICT_SHORT:
        # Only halt when bind would otherwise proceed
        if plan.get("allow_bind") or plan.get("acted"):
            plan["allow_bind"] = False
            if "bind_allowed" in plan:
                plan["bind_allowed"] = False
            plan["halt"] = True
            plan["decision"] = "HALT"
            plan["reason"] = plan.get("reason") or "desk_quorum_short"
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Soft N-of-M for high-mass binds — two UW + charge on sacred.",
        "demo": f"POST {base}/demo/pas/desk-quorum-fob",
        "well_known": f"{base}/.well-known/desk-quorum-fob.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. High-limit MGA desk seed.",
    }
