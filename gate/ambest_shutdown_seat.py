"""AM Best Shutdown Seat — kill switch outside the agent loop.

Real institution: AM Best (Director Edin Imsirovic, NAIC Summer National Meeting
2026) — agentic AI governance must reconstruct actions, stop systems, return to
safe state. Kill switch must live outside agent reasoning (industry consensus).

Twist: epoch lock IS the shutdown seat — Velaru CHARGE outside PAS/agent mesh;
agent cannot unpause itself. Beats AI Governance Institute session/class/deploy scopes.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-ambest-shutdown-seat-v1"
INVENTION = "AM Best Shutdown Seat"
FAMILY = "institutional-twist"

REAL = {
    "institution": "AM Best + NAIC Summer National Meeting 2026",
    "speaker": "Edin Imsirovic, Director AM Best",
    "presentation": "Aug 13 2026, Columbus OH — BDAI Working Group",
    "requirement": "reconstruct action, stop system, return to safe state",
    "outside_loop": "shutdown authority must not live inside agent reasoning",
    "competitor_cosplay": "AI Governance Institute agent kill switch scopes",
}


def evaluate(
    *,
    agent_can_self_stop: bool | None = None,
    shutdown_outside_loop: bool | None = None,
    charge_id: str | None = None,
    reconstructable: bool | None = None,
    tested_shutdown: bool | None = None,
    procedural_review_only: bool | None = None,
) -> dict[str, Any]:
    ghosts: list[str] = []
    if agent_can_self_stop and not shutdown_outside_loop:
        ghosts.append("shutdown_inside_agent_loop")
    if not reconstructable:
        ghosts.append("action_not_reconstructable")
    if not tested_shutdown:
        ghosts.append("untested_kill_switch")
    if procedural_review_only:
        ghosts.append("procedural_click_not_hitl")

    if ghosts:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "real_institution": REAL,
            "verdict": "UNSAFE_AGENT_BIND",
            "ghosts": ghosts,
            "may_bind": False,
        }
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "real_institution": REAL,
        "verdict": "SHUTDOWN_SEAT_ARMED",
        "may_bind": True,
        "shutdown_path": "epoch_lock_velaru_charge_outside_pas",
        "charge_id": charge_id,
        "rule": "AM Best wants stop outside the agent — epoch lock is that seat.",
        "vs_kill_switch_cosplay": "Session stop < epoch HALT that agent cannot lift.",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "AM Best shutdown seat — outside agent loop, epoch lock not kill-switch cosplay.",
        "real_institution": REAL,
        "demo": f"POST {base}/demo/pas/ambest-shutdown-seat",
        "well_known": f"{base}/.well-known/ambest-shutdown-seat.json",
        "pairs_with": "Epoch lock · Override Impossibility · Mariana Pause Latch",
    }
