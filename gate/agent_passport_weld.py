"""Agent Passport Weld — Tool Throat + signed pre-action auth on irreversible tools.

Invention (NORTH_STAR applicable-now): agents shipping now with passwords, no
permission slips. OAP cousin — blocking hook before the tool.
"""
from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import Any

try:
    from gate import throat as throat_mod
except ImportError:
    import throat as throat_mod

SPEC = "gate-agent-passport-weld-v1"
INVENTION = "Agent Passport Weld"
FAMILY = "applicable_now"

IRREVERSIBLE = frozenset(
    {
        "wire",
        "payout",
        "bind",
        "delete",
        "shell",
        "send_email",
        "plc_write",
        "sanction_flag",
        "transfer",
        "deploy",
    }
)

VERDICT_CLEAR = "CLEAR"
VERDICT_CHOKE = "CHOKE"
VERDICT_FORGED = "FORGED"
VERDICT_EXPIRED = "EXPIRED"


def _secret() -> str:
    return (os.getenv("GATE_PASSPORT_SECRET") or os.getenv("GATE_SECRET_KEY") or "").strip()


def mint_passport(
    *,
    agent_id: str,
    tool_class: str,
    subject: str | None = None,
    ttl_seconds: int = 300,
) -> dict[str, Any]:
    """Mint a signed pre-action passport (demo/ops helper)."""
    secret = _secret()
    exp = int(time.time()) + max(30, min(int(ttl_seconds), 3600))
    body = f"{agent_id}|{tool_class}|{subject or ''}|{exp}"
    sig = ""
    if secret:
        sig = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    token = f"ppt:{exp}:{sig}" if sig else f"ppt:{exp}:unsigned"
    return {
        "spec": SPEC,
        "passport": token,
        "agent_id": agent_id,
        "tool_class": tool_class,
        "subject": subject,
        "expires_at": exp,
        "signed": bool(sig),
    }


def _verify_passport(token: str | None, *, agent_id: str, tool_class: str, subject: str | None) -> dict:
    raw = (token or "").strip()
    if not raw.startswith("ppt:"):
        return {"ok": False, "reason": "passport_missing"}
    parts = raw.split(":")
    if len(parts) != 3:
        return {"ok": False, "reason": "passport_malformed"}
    try:
        exp = int(parts[1])
    except ValueError:
        return {"ok": False, "reason": "passport_malformed"}
    if exp < int(time.time()):
        return {"ok": False, "reason": "passport_expired", "expired": True}
    secret = _secret()
    if not secret:
        # Dev: accept structurally valid unexpired token without HMAC when unconfigured
        if parts[2] in ("unsigned", "dev"):
            return {"ok": True, "authority": "dev_unsigned"}
        return {"ok": False, "reason": "passport_secret_unconfigured"}
    body = f"{agent_id}|{tool_class}|{subject or ''}|{exp}"
    expect = hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expect, parts[2].lower()):
        return {"ok": False, "reason": "passport_forged"}
    return {"ok": True, "authority": "hmac_sig"}


def evaluate(
    *,
    tool_class: str | None = None,
    agent_id: str | None = None,
    passport: str | None = None,
    subject: str | None = None,
    decision: str | None = None,
    soft_yes: bool | None = None,
    password_as_auth: bool | None = None,
) -> dict[str, Any]:
    tc = (tool_class or "").strip().lower()
    aid = (agent_id or "").strip() or "agent_unknown"
    irreversible = tc in IRREVERSIBLE or not tc

    if password_as_auth or soft_yes:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_FORGED,
            "may_proceed": False,
            "tool_class": tc or None,
            "agent_id": aid,
            "irreversible": irreversible,
            "reasons": ["password_or_soft_yes_not_passport"],
            "detail": "Password / chat yes is not pre-action auth. Passport required.",
            "rule": "Irreversible tools need signed passport before execution.",
        }

    if not irreversible:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_CLEAR,
            "may_proceed": True,
            "tool_class": tc,
            "agent_id": aid,
            "irreversible": False,
            "reasons": ["reversible_tool"],
            "detail": "Reversible tool class — passport optional.",
            "rule": "Irreversible tools need signed passport before execution.",
        }

    auth = _verify_passport(passport, agent_id=aid, tool_class=tc, subject=subject)
    if auth.get("expired"):
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_EXPIRED,
            "may_proceed": False,
            "tool_class": tc,
            "agent_id": aid,
            "irreversible": True,
            "passport_authority": auth,
            "reasons": ["passport_expired"],
            "detail": "Passport expired — re-mint before tool.",
            "rule": "Irreversible tools need signed passport before execution.",
        }
    if not auth.get("ok"):
        # Also run throat on soft failure shape
        throat = throat_mod.evaluate(decision=decision or None, soft_pas=True)
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_CHOKE,
            "may_proceed": False,
            "tool_class": tc,
            "agent_id": aid,
            "irreversible": True,
            "passport_authority": auth,
            "throat": throat,
            "reasons": [auth.get("reason") or "passport_required"],
            "detail": "Irreversible tool without valid passport — Agent Passport Weld chokes.",
            "rule": "Irreversible tools need signed passport before execution.",
        }

    throat = throat_mod.evaluate(decision=decision or "ALLOW", allow_bind=True)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "verdict": VERDICT_CLEAR if throat.get("state") == throat_mod.OPEN else throat.get("state"),
        "may_proceed": bool(throat.get("may_proceed")),
        "tool_class": tc,
        "agent_id": aid,
        "irreversible": True,
        "passport_authority": auth,
        "throat": throat,
        "reasons": ["passport_ok"],
        "detail": "Signed passport + mouth clear — tool may proceed under coordinators.",
        "rule": "Irreversible tools need signed passport before execution.",
    }


def attach(plan: dict) -> dict:
    result = evaluate(
        tool_class=plan.get("tool_class") or plan.get("write_kind"),
        agent_id=plan.get("agent_id"),
        passport=plan.get("passport") or plan.get("agent_passport"),
        subject=plan.get("job_id") or plan.get("subject"),
        decision=plan.get("decision"),
        soft_yes=plan.get("soft_yes") or plan.get("boss_said_yes"),
        password_as_auth=plan.get("password_as_auth"),
    )
    plan["agent_passport_weld"] = result
    if result.get("irreversible") and not result.get("may_proceed"):
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or (result.get("reasons") or ["passport_required"])[0]
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Tool Throat + signed pre-action passport on irreversible tool classes.",
        "irreversible_classes": sorted(IRREVERSIBLE),
        "demo": f"POST {base}/demo/pas/agent-passport-weld",
        "mint": f"POST {base}/demo/pas/agent-passport-weld/mint",
        "well_known": f"{base}/.well-known/agent-passport-weld.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Agent Mouth Kit seed — OAP cousin.",
    }
