"""Watchman Fuse — duty SLA deadman; silence becomes DERELICT.

Invention: on duty-class writes, timeout is not HALT theater — it is a
dereliction receipt. Coward's CHOKE (choking to dodge required CLEAR) is kin.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-watchman-fuse-v1"
INVENTION = "Watchman Fuse"
FAMILY = "foothill"

VERDICT_WATCHING = "WATCHING"
VERDICT_PULSE_OK = "PULSE_OK"
VERDICT_DERELICT = "DERELICT"
VERDICT_COWARD_CHOKE = "COWARD_CHOKE"
VERDICT_NOT_DUTY = "NOT_DUTY"

REASON_SLA_MISSED = "duty_sla_missed"
REASON_NO_PULSE = "watchman_pulse_missing"
REASON_COWARD = "choke_used_to_dodge_duty"


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    t = str(ts).strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(t)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def evaluate(
    *,
    duty_class: bool | None = None,
    duty_sla_seconds: int | None = None,
    armed_at: str | None = None,
    last_pulse_at: str | None = None,
    now: str | None = None,
    clear_required: bool | None = None,
    choked: bool | None = None,
    acted: bool | None = None,
) -> dict[str, Any]:
    if not duty_class:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "verdict": VERDICT_NOT_DUTY,
            "may_proceed": True,
            "state": None,
            "detail": "Not duty-class — Watchman Fuse stands aside.",
            "rule": "Duty-class silence past SLA is DERELICT. Coward's CHOKE is kin.",
        }

    sla = int(duty_sla_seconds if duty_sla_seconds is not None else 300)
    sla = max(30, min(sla, 86400))
    now_dt = _parse_iso(now) or datetime.now(timezone.utc)
    armed = _parse_iso(armed_at) or now_dt
    pulse = _parse_iso(last_pulse_at)

    if clear_required and choked and not acted:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_COWARD_CHOKE,
            "may_proceed": False,
            "state": "DERELICT",
            "reasons": [REASON_COWARD],
            "duty_sla_seconds": sla,
            "detail": "CHOKE used to dodge required CLEAR on duty-class — dereliction cousin.",
            "rule": "Duty-class silence past SLA is DERELICT. Coward's CHOKE is kin.",
        }

    ref = pulse or armed
    age = (now_dt - ref).total_seconds()
    if age > sla:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_DERELICT,
            "may_proceed": False,
            "state": "DERELICT",
            "reasons": [REASON_SLA_MISSED if pulse else REASON_NO_PULSE],
            "duty_sla_seconds": sla,
            "age_seconds": round(age, 3),
            "detail": "Watchman pulse missed — duty-class silence is DERELICT.",
            "rule": "Duty-class silence past SLA is DERELICT. Coward's CHOKE is kin.",
        }

    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "verdict": VERDICT_PULSE_OK if pulse else VERDICT_WATCHING,
        "may_proceed": True,
        "state": "HOLD",
        "duty_sla_seconds": sla,
        "age_seconds": round(age, 3),
        "detail": "Watchman fuse armed — pulse inside SLA.",
        "rule": "Duty-class silence past SLA is DERELICT. Coward's CHOKE is kin.",
        "pairs_with": "Deadman Echo · Panic Latch · Moral Throat",
    }


def attach(plan: dict) -> dict:
    result = evaluate(
        duty_class=plan.get("duty_class"),
        duty_sla_seconds=plan.get("duty_sla_seconds"),
        armed_at=plan.get("duty_armed_at"),
        last_pulse_at=plan.get("watchman_pulse_at") or plan.get("last_live_at"),
        clear_required=plan.get("clear_required"),
        choked=plan.get("choked")
        or (isinstance(plan.get("throat"), dict) and plan["throat"].get("state") == "CHOKE"),
        acted=plan.get("acted"),
    )
    plan["watchman_fuse"] = result
    if result.get("verdict") in (VERDICT_DERELICT, VERDICT_COWARD_CHOKE):
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or (result.get("reasons") or ["derelict"])[0]
        plan["moral_throat_state"] = "DERELICT"
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Duty-class deadman — silence past SLA is DERELICT; coward's CHOKE is kin.",
        "demo": f"POST {base}/demo/pas/watchman-fuse",
        "well_known": f"{base}/.well-known/watchman-fuse.json",
        "bind_room": f"{base}/bind-room",
        "temporal_sheath": "gate/TEMPORAL_SHEATH.md",
        "north_star": "gate/NORTH_STAR.md#moral-throat",
        "posture": "Under coordinators. Duty sets must stay tiny and published.",
    }
