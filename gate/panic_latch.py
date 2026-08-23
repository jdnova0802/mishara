"""Panic Latch — during declared incident, all new hard commits escalate or DENY.

Invention (NORTH_STAR applicable-now): anti-charisma under catastrophe.
Carrier ops room seed.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-panic-latch-v1"
INVENTION = "Panic Latch"
FAMILY = "applicable_now"

MODE_NORMAL = "NORMAL"
MODE_PANIC = "PANIC"
MODE_ESCALATE = "ESCALATE_ONLY"

VERDICT_CLEAR = "CLEAR"
VERDICT_DENY = "DENY"
VERDICT_ESCALATE = "ESCALATE"


def evaluate(
    *,
    incident_declared: bool | None = None,
    panic_mode: str | None = None,
    would_commit: bool | None = None,
    escalated: bool | None = None,
    mass_class: str | None = None,
    boss_said_yes: bool | None = None,
) -> dict[str, Any]:
    mode = (panic_mode or "").strip().upper()
    if incident_declared or mode in ("PANIC", "1", "TRUE", "ON"):
        mode = MODE_PANIC
    elif mode in ("ESCALATE", "ESCALATE_ONLY"):
        mode = MODE_ESCALATE
    else:
        mode = MODE_NORMAL

    if mode == MODE_NORMAL:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "mode": MODE_NORMAL,
            "verdict": VERDICT_CLEAR,
            "may_proceed": True,
            "detail": "No declared incident — Panic Latch idle.",
            "rule": "During declared incident: new hard commits escalate or DENY — never soft-yes.",
        }

    if boss_said_yes and would_commit:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "mode": mode,
            "verdict": VERDICT_DENY,
            "may_proceed": False,
            "reasons": ["charisma_under_panic"],
            "detail": "Boss said yes during panic — forged. Latch DENY.",
            "rule": "During declared incident: new hard commits escalate or DENY — never soft-yes.",
        }

    if would_commit and not escalated:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "mode": mode,
            "verdict": VERDICT_ESCALATE if mode == MODE_ESCALATE else VERDICT_DENY,
            "may_proceed": False,
            "reasons": ["hard_commit_during_incident"],
            "mass_class": mass_class,
            "detail": (
                "Hard commit during incident without escalation — escalate path required."
                if mode == MODE_ESCALATE
                else "Hard commit during panic — DENY until incident cleared."
            ),
            "rule": "During declared incident: new hard commits escalate or DENY — never soft-yes.",
        }

    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "mode": mode,
        "verdict": VERDICT_CLEAR if escalated or not would_commit else VERDICT_DENY,
        "may_proceed": bool(escalated) or not would_commit,
        "detail": "Incident active; commit allowed only via escalation receipt.",
        "rule": "During declared incident: new hard commits escalate or DENY — never soft-yes.",
    }


def attach(plan: dict) -> dict:
    result = evaluate(
        incident_declared=plan.get("incident_declared"),
        panic_mode=plan.get("panic_mode"),
        would_commit=bool(plan.get("allow_bind") or plan.get("acted") or plan.get("would_bind")),
        escalated=plan.get("escalated"),
        mass_class=plan.get("mass_class")
        or (plan.get("mass_tag") or {}).get("mass_class")
        if isinstance(plan.get("mass_tag"), dict)
        else plan.get("mass_class"),
        boss_said_yes=plan.get("boss_said_yes"),
    )
    plan["panic_latch"] = result
    if not result.get("may_proceed"):
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or (result.get("reasons") or ["panic_latch"])[0]
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Declared incident → new hard commits escalate or DENY.",
        "modes": [MODE_NORMAL, MODE_PANIC, MODE_ESCALATE],
        "demo": f"POST {base}/demo/pas/panic-latch",
        "well_known": f"{base}/.well-known/panic-latch.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Carrier ops room seed.",
    }
