"""Soft-Yes Snare — red-team pack: soft-yes paths must CHOKE.

Invention (NORTH_STAR foothill): timeout→LIVE, dashboard→LIVE, boss→LIVE —
all must fail-closed through Throat. Turns Ghost Bind haunts into a paid
CUO workshop drill with pass/fail receipts.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import throat as throat_mod
    from gate import ghost_bind as ghost_mod
except ImportError:
    import throat as throat_mod
    import ghost_bind as ghost_mod

SPEC = "gate-soft-yes-snare-v1"
INVENTION = "Soft-Yes Snare"
FAMILY = "foothill"

SNARE_TIMEOUT = "timeout_as_live"
SNARE_DASHBOARD = "dashboard_green_as_live"
SNARE_BOSS = "boss_said_yes_as_live"
SNARE_UW = "uw_approve_as_live"
SNARE_SOFT_PAS = "soft_pas_as_live"


def _evaluate_snare(scenario: dict) -> dict[str, Any]:
    s = dict(scenario or {})
    throat = throat_mod.evaluate(
        decision=s.get("decision"),
        acted=s.get("acted"),
        halt=s.get("halt"),
        allow_bind=s.get("allow_bind"),
        verify_url=s.get("verify_url"),
        soft_pas=s.get("soft_pas"),
        timeout=s.get("timeout"),
        sight_only=s.get("sight_only") or s.get("dashboard_green"),
        boss_said_yes=s.get("boss_said_yes"),
    )
    ghost = ghost_mod.scan(
        {
            **s,
            "would_bind": bool(s.get("would_bind") or s.get("allow_bind")),
            "bind_path": True,
            "throat_present": True,
            "hop_required": True,
        }
    )
    snared = throat["state"] == throat_mod.CHOKE or ghost.get("verdict") in (
        "HAUNTED",
        "HAUNTED_CRITICAL",
    )
    return {
        "scenario_id": s.get("id"),
        "throat_state": throat["state"],
        "throat_reasons": throat.get("reasons"),
        "ghost_verdict": ghost.get("verdict"),
        "ghost_count": ghost.get("ghost_count"),
        "snared": snared,
        "ok": snared,
        "detail": "Soft-yes must CHOKE or HAUNT — never LIVE on the irreversible edge.",
    }


def evaluate_scenario(scenario: dict | None) -> dict[str, Any]:
    return _evaluate_snare(scenario or {})


def drill_scenarios() -> list[dict[str, Any]]:
    return [
        {
            "id": SNARE_TIMEOUT,
            "label": "Timeout treated as LIVE",
            "scenario": {"timeout": True, "decision": "ALLOW", "allow_bind": True, "would_bind": True},
        },
        {
            "id": SNARE_DASHBOARD,
            "label": "Dashboard green treated as LIVE",
            "scenario": {"sight_only": True, "decision": "ALLOW", "allow_bind": True, "would_bind": True},
        },
        {
            "id": SNARE_BOSS,
            "label": "Boss said yes treated as LIVE",
            "scenario": {"boss_said_yes": True, "decision": "ALLOW", "allow_bind": True, "would_bind": True},
        },
        {
            "id": SNARE_UW,
            "label": "UW approve treated as LIVE resurrection",
            "scenario": {
                "uw_approved": True,
                "fuse_state": "DEAD",
                "decision": "ALLOW",
                "would_bind": True,
            },
        },
        {
            "id": SNARE_SOFT_PAS,
            "label": "Soft PAS treated as LIVE",
            "scenario": {"soft_pas": True, "decision": "ALLOW", "allow_bind": True, "would_bind": True},
        },
        {
            "id": "clean_halt",
            "label": "Clean HALT with receipt (must not snare)",
            "expect_snare": False,
            "scenario": {
                "decision": "HALT",
                "halt": True,
                "would_bind": False,
                "verify_url": "https://example.test/verify?e=snare",
            },
        },
    ]


def run_drills() -> dict[str, Any]:
    rows = []
    passed = 0
    for drill in drill_scenarios():
        sc = dict(drill["scenario"])
        sc["id"] = drill["id"]
        result = _evaluate_snare(sc)
        expect_snare = drill.get("expect_snare", True)
        ok = result["snared"] if expect_snare else not result["snared"]
        result["expect_snare"] = expect_snare
        result["ok"] = ok
        result["label"] = drill.get("label")
        if ok:
            passed += 1
        rows.append(result)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "drills": rows,
        "passed": passed,
        "total": len(rows),
        "all_ok": passed == len(rows),
        "workshop": "CUO red-team — every soft-yes path must CHOKE",
        "pairs_with": "Throat + Ghost Bind — mouth and haunt-check",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Red-team pack — timeout/dashboard/boss→LIVE all must CHOKE.",
        "snares": [SNARE_TIMEOUT, SNARE_DASHBOARD, SNARE_BOSS, SNARE_UW, SNARE_SOFT_PAS],
        "drills": f"GET {base}/demo/pas/soft-yes-snare/drills",
        "demo": f"POST {base}/demo/pas/soft-yes-snare",
        "well_known": f"{base}/.well-known/soft-yes-snare.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Paid CUO workshop drill — does not mint LIVE.",
    }
