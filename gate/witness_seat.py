"""Witness Seat — read-only stranger principal that can verify but never LIVE.

Invention (NORTH_STAR applicable-now): examiner / regulator as first-class role.
Officer pack seed.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-witness-seat-v1"
INVENTION = "Witness Seat"
FAMILY = "applicable_now"

ROLE_WITNESS = "witness"
ROLE_OPERATOR = "operator"
ROLE_UW = "uw"

VERDICT_OK = "WITNESS_OK"
VERDICT_FORGED_LIVE = "WITNESS_CANNOT_LIVE"


def evaluate(
    *,
    role: str | None = None,
    would_live: bool | None = None,
    verify_only: bool | None = None,
    verify_url: str | None = None,
) -> dict[str, Any]:
    r = (role or ROLE_WITNESS).strip().lower()
    if r != ROLE_WITNESS:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "role": r,
            "verdict": VERDICT_OK,
            "may_verify": True,
            "may_live": r in (ROLE_OPERATOR, ROLE_UW),
            "detail": f"Role {r} — not Witness Seat constrained.",
            "rule": "Witness may verify; Witness never LIVE.",
        }

    if would_live:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "role": ROLE_WITNESS,
            "verdict": VERDICT_FORGED_LIVE,
            "may_verify": True,
            "may_live": False,
            "may_proceed": False,
            "reasons": ["witness_attempted_live"],
            "verify_url": verify_url,
            "detail": "Witness tried to mint LIVE — forged. Seat is verify-only.",
            "rule": "Witness may verify; Witness never LIVE.",
        }

    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "role": ROLE_WITNESS,
        "verdict": VERDICT_OK,
        "may_verify": True,
        "may_live": False,
        "may_proceed": True,
        "verify_only": True if verify_only is None else bool(verify_only),
        "verify_url": verify_url,
        "detail": "Witness Seat open — stranger verify without LIVE authority.",
        "rule": "Witness may verify; Witness never LIVE.",
        "pairs_with": "Hop Tattoo · Receipt Mirror · Officer pack",
    }


def attach(plan: dict) -> dict:
    result = evaluate(
        role=plan.get("role") or plan.get("principal_role"),
        would_live=bool(plan.get("witness_would_live")),
        verify_only=plan.get("verify_only"),
        verify_url=plan.get("verify_url"),
    )
    plan["witness_seat"] = result
    if result.get("verdict") == VERDICT_FORGED_LIVE:
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or "witness_cannot_live"
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Read-only stranger principal — verify yes, LIVE never.",
        "demo": f"POST {base}/demo/pas/witness-seat",
        "well_known": f"{base}/.well-known/witness-seat.json",
        "bind_room": f"{base}/bind-room",
        "officer_pack": f"{base}/bind-room/officer-pack.json",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Examiner / regulator first-class role.",
    }
