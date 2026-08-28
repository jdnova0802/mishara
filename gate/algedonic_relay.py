"""Algedonic Relay — Cybersyn escalation when bind autonomy fails.

Real: Stafford Beer Project Cybersyn (Chile 1971–73). Cyberfilter emits algedonic
signals when a subsystem exceeds intervention elapse time — red flashing arrows
escalate recursion upward. Designing freedom: autonomy forfeited when whole-system cohesion requires it.

Twist: PAS bind desk has elapse time; ghost bind / failed redeem / epoch lock triggers
algedonic relay to CUO — not silent dashboard green.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-algedonic-relay-v1"
INVENTION = "Algedonic Relay"
FAMILY = "s-tier"
TIER = "S"

REAL = {
    "institution": "Project Cybersyn — Stafford Beer / CORFO / Chile",
    "years": "1971–1973",
    "concept": "Algedonic signal — pain/pleasure escalation when intervention elapse exceeded",
    "source": "Cyberfilter · Opsroom red flashing arrows",
    "url": "https://metaphorum.org/staffords-work/cybersyn",
}


def evaluate(
    *,
    elapse_seconds: int | None = None,
    age_seconds: float | None = None,
    resolved: bool | None = None,
    recursion_level: int | None = None,
) -> dict[str, Any]:
    elapse = max(30, min(int(elapse_seconds or 300), 86400))
    age = float(age_seconds or 0)
    level = max(0, min(int(recursion_level or 0), 12))
    escalate = (not resolved) and age > elapse
    color = "green" if resolved else ("yellow" if age > elapse * 0.5 else "green")
    if escalate:
        color = "red"
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "tier": TIER,
        "real_institution": REAL,
        "verdict": "ALGEDONIC_ESCALATE" if escalate else "WITHIN_ELAPSE",
        "escalate": escalate,
        "recursion_level": level,
        "next_recursion": level + 1 if escalate else level,
        "opsroom_color": color,
        "elapse_seconds": elapse,
        "age_seconds": round(age, 3),
        "rule": "Designing freedom: bind desk autonomy ends when elapse exceeded — relay upward.",
        "carrier_analog": "PAS desk → MGA CUO → regulator examiner",
    }


def attach(plan: dict) -> dict:
    halted = plan.get("halt") or (plan.get("decision") or "").upper() in ("HALT", "BLOCK")
    ghost = (plan.get("ghost_bind") or {}).get("haunted")
    ev = evaluate(
        elapse_seconds=plan.get("duty_sla_seconds") or 300,
        age_seconds=(plan.get("watchman_fuse") or {}).get("age_seconds") or (900 if halted else 0),
        resolved=not halted and not ghost,
        recursion_level=2 if ghost else 1,
    )
    plan["algedonic_relay"] = ev
    if ev.get("escalate"):
        plan["algedonic_escalated"] = True
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "tier": TIER,
        "one_liner": "Cybersyn algedonic relay — bind failure escalates red, not dashboard green.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/algedonic-relay",
        "well_known": f"{base}/.well-known/algedonic-relay.json",
    }
