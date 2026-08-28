"""Sophon Lock — client-side proof is tamper theater; server redeem is truth.

Fiction: Liu Cixin *The Three-Body Problem* — sophons (proton-dimensional unfold)
lock human particle accelerators and make client-side physics untrustworthy.

Twist: Any bind "proof" that never hits server redeem is sophon-locked theater —
only POST /redeem + epoch consume is proton-grade; client JWT alone = PROTON_LOCK.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-sophon-lock-v1"
INVENTION = "Sophon Lock"
TIER = "S"
FAMILY = "s-tier"

REAL = {
    "institution": "Three-Body Problem sophon interference (fiction)",
    "concept": "Client-side measurement untrustworthy when observer can tamper",
    "formal_analog": "Server-authoritative redeem vs bearer client proof",
    "url": "https://en.wikipedia.org/wiki/The_Three-Body_Problem_(novel)",
}


def lock_status(
    *,
    client_proof_only: bool | None = None,
    server_redeem_ok: bool | None = None,
    epoch_consumed: bool | None = None,
    offline_bearer: bool | None = None,
) -> dict[str, Any]:
    theater = bool(client_proof_only or offline_bearer) and not server_redeem_ok
    proton_grade = bool(server_redeem_ok and epoch_consumed)
    if theater:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "tier": TIER,
            "real_institution": REAL,
            "verdict": "PROTON_LOCK",
            "may_stick": False,
            "sophon_locked": True,
            "reason": "client_proof_without_server_redeem",
            "rule": "Sophons lock client physics — only server redeem escapes the lock.",
        }
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "tier": TIER,
        "real_institution": REAL,
        "verdict": "PROTON_GRADE" if proton_grade else "REDEEM_PENDING",
        "may_stick": proton_grade,
        "sophon_locked": False,
        "server_authoritative": True,
    }


def attach(plan: dict) -> dict:
    ticket = plan.get("bind_ticket") if isinstance(plan.get("bind_ticket"), dict) else {}
    ev = lock_status(
        client_proof_only=bool(ticket.get("signature") and not ticket.get("consumed")),
        server_redeem_ok=bool(ticket.get("consumed")),
        epoch_consumed=bool((plan.get("epoch") or {}).get("locked")),
        offline_bearer=bool(ticket.get("offline_bearer")),
    )
    plan["sophon_lock"] = ev
    if ev.get("verdict") == "PROTON_LOCK":
        plan["sophon_locked"] = True
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "tier": TIER,
        "one_liner": "Sophon lock — client bind proof is theater until server redeem lands.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/sophon-lock",
        "well_known": f"{base}/.well-known/sophon-lock.json",
    }
