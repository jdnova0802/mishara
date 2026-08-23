"""Payout Throat — same mouth on money-leave (release before wire).

Invention (NORTH_STAR applicable-now): SCIENCE first weld — second commercial
edge after bind. Withdraw / payout / release must OPEN, CLOSE, or CHOKE with
the same fail-closed grammar as bind.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import throat as throat_mod
except ImportError:
    import throat as throat_mod

SPEC = "gate-payout-throat-v1"
INVENTION = "Payout Throat"
FAMILY = "applicable_now"

PAYOUT_KINDS = frozenset(
    {"payout", "withdraw", "release", "wire", "disbursement", "settlement_release"}
)


def _is_payout(*, write_kind: str | None = None, spend_write: dict | None = None) -> bool:
    wk = (write_kind or "").strip().lower()
    if wk in PAYOUT_KINDS:
        return True
    if isinstance(spend_write, dict):
        sk = (spend_write.get("spend_kind") or spend_write.get("write_kind") or "").lower()
        if sk in PAYOUT_KINDS:
            return True
        path = (spend_write.get("path") or "").lower()
        return any(k in path for k in ("payout", "withdraw", "release", "/wire"))
    return False


def evaluate(
    *,
    decision: str | None = None,
    acted: bool | None = None,
    halt: bool | None = None,
    allow_payout: bool | None = None,
    verify_url: str | None = None,
    soft_pas: bool | None = None,
    timeout: bool | None = None,
    sight_only: bool | None = None,
    boss_said_yes: bool | None = None,
    write_kind: str | None = None,
    spend_write: dict | None = None,
    hop: dict | None = None,
) -> dict[str, Any]:
    """Evaluate payout edge with Throat grammar. Non-payout → not_applicable."""
    if not _is_payout(write_kind=write_kind, spend_write=spend_write) and write_kind is not None:
        # Explicit non-payout write_kind
        if (write_kind or "").strip().lower() not in PAYOUT_KINDS:
            return {
                "spec": SPEC,
                "invention": INVENTION,
                "applicable": False,
                "state": None,
                "detail": "Not a payout/withdraw edge — Payout Throat stands aside.",
            }
    # Default: treat as payout when called explicitly without write_kind, or when detected
    is_payout = write_kind is None or _is_payout(write_kind=write_kind, spend_write=spend_write)
    if not is_payout:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "applicable": False,
            "state": None,
            "detail": "Not a payout/withdraw edge — Payout Throat stands aside.",
        }
    allow = allow_payout
    throat = throat_mod.evaluate(
        decision=decision,
        acted=acted,
        halt=halt,
        allow_bind=allow,
        verify_url=verify_url,
        soft_pas=soft_pas,
        timeout=timeout,
        sight_only=sight_only,
        boss_said_yes=boss_said_yes,
        hop=hop,
    )
    return {
        **throat,
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "applicable": True,
        "edge": "payout",
        "rule": "Money-leave uses the same mouth as bind. Soft-yes never wires.",
        "pairs_with": "Throat — bind mouth; Payout Throat — money-leave mouth",
    }


def attach(plan: dict, *, spend_write: dict | None = None) -> dict:
    sw = spend_write if isinstance(spend_write, dict) else None
    if sw is None and isinstance(plan.get("spend_protocol"), dict):
        sw = plan["spend_protocol"].get("write")
    result = evaluate(
        decision=plan.get("decision"),
        acted=plan.get("acted"),
        halt=plan.get("halt"),
        allow_payout=plan.get("allow_payout") or plan.get("allow_bind"),
        verify_url=plan.get("verify_url"),
        soft_pas=plan.get("soft_pas"),
        timeout=plan.get("timeout"),
        sight_only=plan.get("sight_only"),
        boss_said_yes=plan.get("boss_said_yes"),
        write_kind=plan.get("write_kind"),
        spend_write=sw if isinstance(sw, dict) else None,
        hop=plan.get("hop") if isinstance(plan.get("hop"), dict) else None,
    )
    plan["payout_throat"] = result
    if result.get("applicable") and result.get("state") == throat_mod.CHOKE:
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["allow_payout"] = False
        plan["halt"] = True
        plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or (result.get("reasons") or ["payout_throat_choke"])[0]
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Same fail-closed mouth on money-leave — release before wire.",
        "demo": f"POST {base}/demo/pas/payout-throat",
        "well_known": f"{base}/.well-known/payout-throat.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. SCIENCE first weld after bind.",
    }
