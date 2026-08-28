"""Agorá Atomic Bind — BIS Project Agorá conditional settlement for bind path.

Real institution: BIS + IIF Project Agorá (2024–2025) — tokenised deposits +
CBDC reserves on shared platform; smart contracts embed compliance + conditional
triggers; atomic multi-currency settlement.

Twist: bind is one atomic Agorá leg — epoch clear + ticket redeem + spend fingerprint
+ premium mass must settle together or none fire. No partial ghost bind.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-agora-atomic-bind-v1"
INVENTION = "Agorá Atomic Bind"
FAMILY = "institutional-twist"

REAL = {
    "institution": "Bank for International Settlements + Institute of International Finance",
    "project": "Project Agorá — programmable wholesale cross-border platform",
    "capability": "atomic settlement + embedded compliance triggers",
    "url": "https://www.bis.org/publ/othp110.htm",
}

LEGS = (
    "epoch_clear",
    "ticket_redeemed",
    "spend_fingerprint_match",
    "premium_mass_within_bounds",
    "license_parent_live",
)


def evaluate(
    *,
    epoch_clear: bool | None = None,
    ticket_redeemed: bool | None = None,
    fingerprint_match: bool | None = None,
    premium_ok: bool | None = None,
    license_live: bool | None = None,
    partial_bind_attempt: bool | None = None,
) -> dict[str, Any]:
    legs = {
        "epoch_clear": bool(epoch_clear),
        "ticket_redeemed": bool(ticket_redeemed),
        "spend_fingerprint_match": bool(fingerprint_match),
        "premium_mass_within_bounds": bool(premium_ok),
        "license_parent_live": bool(license_live),
    }
    all_ok = all(legs.values())
    if partial_bind_attempt and not all_ok:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "real_institution": REAL,
            "verdict": "ATOMIC_ABORT",
            "atomic": False,
            "legs": legs,
            "failed": [k for k, v in legs.items() if not v],
            "rule": "Agorá leg partiality is ghost bind — all legs or none.",
        }
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "verdict": "ATOMIC_BIND" if all_ok else "LEGS_INCOMPLETE",
        "atomic": all_ok,
        "legs": legs,
        "leg_names": list(LEGS),
    }


def attach(plan: dict) -> dict:
    ep = plan.get("epoch") if isinstance(plan.get("epoch"), dict) else {}
    plan["agora_atomic_bind"] = evaluate(
        epoch_clear=not ep.get("locked"),
        ticket_redeemed=bool(plan.get("acted") and plan.get("allow_bind")),
        fingerprint_match=bool((plan.get("spend_protocol") or {}).get("fingerprint")),
        premium_ok=(plan.get("stick_meter") or {}).get("mass_class") != "sacred"
        or bool(plan.get("desk_quorum_fob")),
        license_live=(plan.get("license_fuse") or {}).get("state") != "DEAD",
        partial_bind_attempt=bool(plan.get("allow_bind")) or bool(plan.get("would_bind")),
    )
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "BIS Agorá atomic legs — epoch + ticket + fingerprint + mass or abort.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/agora-atomic-bind",
        "well_known": f"{base}/.well-known/agora-atomic-bind.json",
    }
