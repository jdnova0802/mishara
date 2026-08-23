"""Deadman Echo — during long tool/agent chains: periodic re-LIVE or CHOKE.

Invention (NORTH_STAR applicable-now): stops “authorized at t0, wrong at t5”.
Agent Mouth Kit seed.
"""
from __future__ import annotations

import time
from typing import Any

SPEC = "gate-deadman-echo-v1"
INVENTION = "Deadman Echo"
FAMILY = "applicable_now"

DEFAULT_TTL_SECONDS = 300  # 5 minutes between re-LIVE

VERDICT_LIVE = "LIVE"
VERDICT_CHOKE = "CHOKE"
VERDICT_STALE = "STALE"


def evaluate(
    *,
    last_live_at: float | int | None = None,
    now: float | int | None = None,
    ttl_seconds: int | None = None,
    chain_step: int | None = None,
    re_live_presented: bool | None = None,
    soft_continue: bool | None = None,
) -> dict[str, Any]:
    ttl = int(ttl_seconds if ttl_seconds is not None else DEFAULT_TTL_SECONDS)
    ttl = max(30, min(ttl, 3600))
    ts = float(now if now is not None else time.time())
    last = float(last_live_at) if last_live_at is not None else None

    if soft_continue and not re_live_presented and last is None:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_CHOKE,
            "may_proceed": False,
            "ttl_seconds": ttl,
            "chain_step": chain_step,
            "reasons": ["soft_continue_without_re_live"],
            "detail": "Long chain soft-continued without re-LIVE — Deadman Echo chokes.",
            "rule": "During long tool/agent chains: periodic re-LIVE or CHOKE.",
        }

    if last is None:
        if re_live_presented:
            return {
                "spec": SPEC,
                "invention": INVENTION,
                "family": FAMILY,
                "verdict": VERDICT_LIVE,
                "may_proceed": True,
                "ttl_seconds": ttl,
                "chain_step": chain_step,
                "detail": "Re-LIVE presented — echo renewed.",
                "rule": "During long tool/agent chains: periodic re-LIVE or CHOKE.",
            }
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_CHOKE,
            "may_proceed": False,
            "ttl_seconds": ttl,
            "chain_step": chain_step,
            "reasons": ["no_live_timestamp"],
            "detail": "No last LIVE timestamp on chain — choke until mouth clears.",
            "rule": "During long tool/agent chains: periodic re-LIVE or CHOKE.",
        }

    age = ts - last
    if age > ttl and not re_live_presented:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_STALE,
            "may_proceed": False,
            "ttl_seconds": ttl,
            "age_seconds": round(age, 3),
            "chain_step": chain_step,
            "reasons": ["live_stale"],
            "detail": f"LIVE older than {ttl}s — re-LIVE required.",
            "rule": "During long tool/agent chains: periodic re-LIVE or CHOKE.",
        }

    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "verdict": VERDICT_LIVE,
        "may_proceed": True,
        "ttl_seconds": ttl,
        "age_seconds": round(age, 3),
        "chain_step": chain_step,
        "detail": "Echo within TTL — chain may continue under coordinators.",
        "rule": "During long tool/agent chains: periodic re-LIVE or CHOKE.",
    }


def attach(plan: dict) -> dict:
    result = evaluate(
        last_live_at=plan.get("last_live_at"),
        ttl_seconds=plan.get("deadman_ttl_seconds"),
        chain_step=plan.get("chain_step"),
        re_live_presented=plan.get("re_live_presented"),
        soft_continue=plan.get("soft_continue") or plan.get("agent_chain"),
    )
    plan["deadman_echo"] = result
    # Only enforce when agent_chain / soft_continue is active
    if (plan.get("agent_chain") or plan.get("soft_continue")) and not result.get("may_proceed"):
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or (result.get("reasons") or ["deadman_stale"])[0]
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Long tool/agent chains: periodic re-LIVE or CHOKE.",
        "default_ttl_seconds": DEFAULT_TTL_SECONDS,
        "demo": f"POST {base}/demo/pas/deadman-echo",
        "well_known": f"{base}/.well-known/deadman-echo.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Agent Mouth Kit seed.",
    }
