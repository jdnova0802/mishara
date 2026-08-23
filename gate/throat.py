"""Throat — fail-closed wedge on the bind edge.

Invention (NORTH_STAR foothill): no PAS stick without cleared LIVE or proved DENY.
Ambiguity, timeout, missing hop, soft config → CHOKE (never soft-allow).

Throat is the mouth before the irreversible write. Bind Room's first welded invention.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-throat-v1"
INVENTION = "Throat"
FAMILY = "foothill"

# Mouth states
OPEN = "OPEN"  # LIVE cleared — bind may proceed under coordinator policy
CLOSED = "CLOSED"  # DENY proved — bind must not proceed; stranger can verify halt
CHOKE = "CHOKE"  # Fail-closed — cannot prove LIVE or DENY; never soft-allow

REASON_LIVE = "live_cleared"
REASON_DENY_PROVED = "deny_proved"
REASON_MISSING_DECISION = "missing_decision"
REASON_TIMEOUT = "timeout_is_halt_not_live"
REASON_SOFT_CONFIG = "soft_pas_without_mouth"
REASON_AMBIGUOUS = "ambiguous_without_receipt"
REASON_ACTED_WITHOUT_LIVE = "acted_without_live"
REASON_SIGHT_AS_MOUTH = "sight_treated_as_mouth"


def _norm(decision: str | None) -> str:
    return (decision or "").strip().upper()


def evaluate(
    *,
    decision: str | None = None,
    acted: bool | None = None,
    halt: bool | None = None,
    allow_bind: bool | None = None,
    verify_url: str | None = None,
    hop: dict | None = None,
    soft_pas: bool | None = None,
    timeout: bool | None = None,
    sight_only: bool | None = None,
) -> dict[str, Any]:
    """Evaluate whether the Throat opens, closes, or chokes.

    OPEN  — decision ALLOW/LIVE and not halted; bind write may proceed.
    CLOSED — decision BLOCK/HALT/DENY with (or without) receipt; stick forbidden.
    CHOKE — anything that would soft-fail-open (timeout, missing, soft PAS, sight-as-mouth).
    """
    hop = hop if isinstance(hop, dict) else {}
    d = _norm(decision) or _norm(hop.get("decision"))
    halted = bool(halt) or bool(hop.get("halt")) or d in ("HALT", "BLOCK", "DENY", "DEAD")
    allow = allow_bind if allow_bind is not None else hop.get("allow_bind")
    if allow is None and d in ("ALLOW", "LIVE", "GO"):
        allow = True
    if allow is None and halted:
        allow = False
    verify = (verify_url or hop.get("verify_url") or "").strip() or None
    reasons: list[str] = []

    if timeout or hop.get("timeout"):
        return _result(
            CHOKE,
            reasons=[REASON_TIMEOUT],
            decision=d or "HALT",
            verify_url=verify,
            detail="Timeout is HALT, never LIVE. Throat chokes.",
        )
    if soft_pas or hop.get("soft_pas"):
        return _result(
            CHOKE,
            reasons=[REASON_SOFT_CONFIG],
            decision=d or None,
            verify_url=verify,
            detail="Soft PAS without mouth — Throat refuses silent stick.",
        )
    if sight_only or hop.get("sight_only"):
        return _result(
            CHOKE,
            reasons=[REASON_SIGHT_AS_MOUTH],
            decision=d or None,
            verify_url=verify,
            detail="Dashboard green is sight, not mouth.",
        )
    if not d and allow is None and not halted:
        return _result(
            CHOKE,
            reasons=[REASON_MISSING_DECISION],
            decision=None,
            verify_url=verify,
            detail="No decision on the irreversible edge — choke.",
        )
    if acted and not (allow and d in ("ALLOW", "LIVE", "GO") and not halted):
        reasons.append(REASON_ACTED_WITHOUT_LIVE)
        return _result(
            CHOKE,
            reasons=reasons or [REASON_AMBIGUOUS],
            decision=d or None,
            verify_url=verify,
            detail="Act without cleared LIVE — Throat chokes.",
        )
    if allow and d in ("ALLOW", "LIVE", "GO") and not halted:
        return _result(
            OPEN,
            reasons=[REASON_LIVE],
            decision=d,
            verify_url=verify,
            detail="LIVE cleared — Throat open under coordinator policy.",
            may_proceed=True,
        )
    if halted or d in ("HALT", "BLOCK", "DENY", "DEAD") or allow is False:
        reasons.append(REASON_DENY_PROVED)
        return _result(
            CLOSED,
            reasons=reasons,
            decision=d or "HALT",
            verify_url=verify,
            detail="DENY/HALT on the edge — Throat closed; stick forbidden.",
            deny_proved=True,
        )
    return _result(
        CHOKE,
        reasons=[REASON_AMBIGUOUS],
        decision=d or None,
        verify_url=verify,
        detail="Ambiguous edge — Throat never soft-allows.",
    )


def _result(
    state: str,
    *,
    reasons: list[str],
    decision: str | None,
    verify_url: str | None,
    detail: str,
    may_proceed: bool = False,
    deny_proved: bool = False,
) -> dict[str, Any]:
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "state": state,
        "may_proceed": may_proceed and state == OPEN,
        "deny_proved": deny_proved or state == CLOSED,
        "fail_closed": state == CHOKE,
        "decision": decision,
        "reasons": reasons,
        "verify_url": verify_url,
        "detail": detail,
        "rule": "No PAS stick without cleared LIVE or proved DENY. Ambiguity ⇒ CHOKE.",
    }


def attach(plan: dict, *, hop: dict | None = None) -> dict:
    """Stamp Throat onto a pre-bind / bind-check plan."""
    hop_d = hop if isinstance(hop, dict) else (plan.get("hop") if isinstance(plan.get("hop"), dict) else {})
    decision = plan.get("decision") or plan.get("result")
    throat = evaluate(
        decision=decision,
        acted=plan.get("acted"),
        halt=plan.get("halt") or hop_d.get("halt"),
        allow_bind=plan.get("allow_bind") if "allow_bind" in plan else plan.get("bind_allowed"),
        verify_url=plan.get("verify_url") or hop_d.get("verify_url"),
        hop=hop_d,
        soft_pas=plan.get("soft_pas"),
        timeout=plan.get("timeout"),
        sight_only=plan.get("sight_only"),
    )
    plan["throat"] = throat
    if throat["state"] == CHOKE:
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or throat["reasons"][0]
    elif throat["state"] == CLOSED:
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Fail-closed wedge on the bind edge — no stick without LIVE or proved DENY.",
        "states": {
            OPEN: "LIVE cleared — may proceed under coordinator policy",
            CLOSED: "DENY proved — stick forbidden; stranger can verify",
            CHOKE: "Fail-closed — ambiguity/timeout/soft PAS never soft-allows",
        },
        "pairs_with": "Ghost Bind — detects would-stick-without-may before money moves",
        "demo": f"POST {base}/demo/pas/throat",
        "well_known": f"{base}/.well-known/throat.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Never sovereign. Mountain invention welded to Bind Room seed.",
    }
