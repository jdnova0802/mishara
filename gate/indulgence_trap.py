"""Indulgence Trap — paid / favored / relationship mercy is forged.

Invention: Hard Mercy watched. Money, AE path, prestige letterhead, or
self-pardon masquerading as mercy → trap fire. Companion to Pardon Sunset.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-indulgence-trap-v1"
INVENTION = "Indulgence Trap"
FAMILY = "foothill"

VERDICT_CLEAR = "CLEAR"
VERDICT_TRIPPED = "TRIPPED"

TRAP_PAID = "paid_mercy"
TRAP_RELATIONSHIP = "relationship_live_mercy"
TRAP_SELF = "self_pardon"
TRAP_LETTERHEAD = "prestige_letterhead_sheath"
TRAP_EMOJI = "emoji_quorum_mercy"
TRAP_PANIC_FAVOR = "panic_voice_favor"
TRAP_NO_SCAR = "mercy_without_scar"
TRAP_NO_SUNSET = "forever_pardon"


def evaluate(
    *,
    mercy_attempt: bool | None = None,
    paid: bool | None = None,
    relationship_path: bool | None = None,
    self_pardon: bool | None = None,
    letterhead_only: bool | None = None,
    emoji_quorum: bool | None = None,
    panic_favor: bool | None = None,
    scar: bool | None = None,
    has_sunset: bool | None = None,
) -> dict[str, Any]:
    if not mercy_attempt:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "verdict": VERDICT_CLEAR,
            "tripped": False,
            "traps": [],
            "may_proceed": True,
            "detail": "No mercy attempt — Indulgence Trap idle.",
            "rule": "Mercy bought with money, favor, prestige, or self-pardon is indulgence — forged.",
        }

    traps: list[str] = []
    if paid:
        traps.append(TRAP_PAID)
    if relationship_path:
        traps.append(TRAP_RELATIONSHIP)
    if self_pardon:
        traps.append(TRAP_SELF)
    if letterhead_only:
        traps.append(TRAP_LETTERHEAD)
    if emoji_quorum:
        traps.append(TRAP_EMOJI)
    if panic_favor:
        traps.append(TRAP_PANIC_FAVOR)
    if scar is False:
        traps.append(TRAP_NO_SCAR)
    if has_sunset is False:
        traps.append(TRAP_NO_SUNSET)

    tripped = bool(traps)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "verdict": VERDICT_TRIPPED if tripped else VERDICT_CLEAR,
        "tripped": tripped,
        "traps": traps,
        "may_proceed": not tripped,
        "detail": (
            "Indulgence Trap fired — mercy path is favor/money/prestige theater."
            if tripped
            else "Mercy path clean of indulgence markers — still requires Pardon Sunset grammar."
        ),
        "rule": "Mercy bought with money, favor, prestige, or self-pardon is indulgence — forged.",
        "pairs_with": "Pardon Sunset · Charisma Nullifier · May Quarantine",
        "penalty_hint": "trip → HALT; repeat → nominate may-quarantine",
    }


def drills() -> dict[str, Any]:
    cases = [
        ("paid", {"mercy_attempt": True, "paid": True}, True),
        ("relationship", {"mercy_attempt": True, "relationship_path": True}, True),
        ("self", {"mercy_attempt": True, "self_pardon": True}, True),
        ("clean_mercy_markers", {"mercy_attempt": True, "scar": True, "has_sunset": True}, False),
        ("idle", {"mercy_attempt": False}, False),
    ]
    rows = []
    passed = 0
    for cid, kwargs, expect_trip in cases:
        r = evaluate(**kwargs)
        ok = r["tripped"] is expect_trip
        if ok:
            passed += 1
        rows.append({"id": cid, "expect_tripped": expect_trip, "got": r["tripped"], "ok": ok})
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "drills": rows,
        "passed": passed,
        "total": len(rows),
        "all_ok": passed == len(rows),
    }


def attach(plan: dict) -> dict:
    mercy = bool(plan.get("mercy") or plan.get("against_score"))
    result = evaluate(
        mercy_attempt=mercy,
        paid=plan.get("paid_mercy"),
        relationship_path=plan.get("relationship_live"),
        self_pardon=(plan.get("mercy_grantor_id") or "") == (plan.get("job_id") or plan.get("subject_id") or "")
        and bool(plan.get("mercy_grantor_id")),
        letterhead_only=plan.get("letterhead_only"),
        emoji_quorum=plan.get("emoji_quorum"),
        panic_favor=plan.get("panic_favor"),
        scar=plan.get("mercy_scar"),
        has_sunset=bool(plan.get("mercy_sunset_at") or plan.get("mercy_ttl_seconds")) if mercy else None,
    )
    plan["indulgence_trap"] = result
    if result.get("tripped"):
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or (result.get("traps") or ["indulgence"])[0]
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Paid/favored/prestige mercy is indulgence — trap fires.",
        "traps": [
            TRAP_PAID,
            TRAP_RELATIONSHIP,
            TRAP_SELF,
            TRAP_LETTERHEAD,
            TRAP_EMOJI,
            TRAP_PANIC_FAVOR,
            TRAP_NO_SCAR,
            TRAP_NO_SUNSET,
        ],
        "demo": f"POST {base}/demo/pas/indulgence-trap",
        "drills": f"GET {base}/demo/pas/indulgence-trap/drills",
        "well_known": f"{base}/.well-known/indulgence-trap.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#moral-throat",
        "posture": "Under coordinators. Anti-charisma metallurgy.",
    }
