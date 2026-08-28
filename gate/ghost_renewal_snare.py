"""Ghost Renewal Snare — auto-renew that would stick without fresh may.

Pairs with Ghost Bind and Renewal Day Throat. Hunts batch-scale soft yes on renewal night.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-ghost-renewal-snare-v1"
INVENTION = "Ghost Renewal Snare"
FAMILY = "competitive-response"

GHOST_STALE_TICKET = "stale_ticket_on_renew"
GHOST_NO_PREBIND = "renew_without_prebind_hop"
GHOST_PRIOR_TERM_TICKET = "prior_term_ticket_reused"
GHOST_AUTO_WITHOUT_MAY = "auto_renew_without_fresh_may"
GHOST_BATCH_BYPASS = "batch_path_bypasses_redeem"


def scan(scenario: dict | None = None) -> dict[str, Any]:
    s = scenario if isinstance(scenario, dict) else {}
    ghosts: list[dict[str, Any]] = []

    def flag(code: str, detail: str) -> None:
        ghosts.append({"ghost": code, "detail": detail, "severity": "critical"})

    if s.get("auto_renew") and not s.get("fresh_ticket"):
        flag(GHOST_AUTO_WITHOUT_MAY, "Auto-renew scheduled without fresh bind ticket.")
    if s.get("auto_renew") and s.get("ticket_from_prior_term"):
        flag(GHOST_PRIOR_TERM_TICKET, "Prior policy term ticket reused on renewal stick.")
    if s.get("auto_renew") and s.get("stale_ticket"):
        flag(GHOST_STALE_TICKET, "Expired or consumed ticket on renewal path.")
    if s.get("renew_path") and not s.get("prebind_hop"):
        flag(GHOST_NO_PREBIND, "Renewal write with no pre-bind hop — mouth missing.")
    if s.get("batch_renew") and s.get("skip_redeem"):
        flag(GHOST_BATCH_BYPASS, "Batch renewal bypasses redeem — Parakhin-class ghost stick.")

    haunted = bool(ghosts)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "haunted": haunted,
        "ghost_count": len(ghosts),
        "ghosts": ghosts,
        "verdict": "HAUNTED" if haunted else "CLEAR",
        "pairs_with": "Ghost Bind · Renewal Day Throat · Bind Ticket",
        "rule": "Renewal night is ghost-bind heaven at scale. Snare before premium moves.",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Auto-renew path that would stick without fresh may → CHOKE.",
        "demo": f"POST {base}/demo/pas/ghost-renewal-snare",
        "well_known": f"{base}/.well-known/ghost-renewal-snare.json",
        "posture": "Red-team on 03:00 batch — not CISO dashboard cosplay.",
    }
