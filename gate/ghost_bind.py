"""Ghost Bind — detector for would-stick-without-may.

Invention (NORTH_STAR foothill): surfaces soft PAS / charisma / timeout / sight
as a hard failure *before* money moves. Companion to Throat.

Ghost Bind does not clear. It hunts. Throat is the mouth; Ghost Bind is the
haunt-check that finds binds that would have stuck without may.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-ghost-bind-v1"
INVENTION = "Ghost Bind"
FAMILY = "foothill"

# Ghost classes — each is a named haunt
GHOST_SOFT_PAS = "soft_pas_would_stick"
GHOST_TIMEOUT_AS_LIVE = "timeout_treated_as_live"
GHOST_UW_AS_CHARGE = "uw_approve_treated_as_charge"
GHOST_SIGHT_AS_MOUTH = "dashboard_green_as_live"
GHOST_CHARISMA = "boss_said_yes_without_quorum"
GHOST_MISSING_MOUTH = "bind_path_without_throat"
GHOST_QUOTE_AS_STOP = "quote_release_mistaken_for_bind_stop"
GHOST_DEAD_FUSE_SOFT = "dead_fuse_soft_continued"
GHOST_ACTED_NO_RECEIPT = "acted_without_stranger_receipt"

SEVERITY = {
    GHOST_SOFT_PAS: "critical",
    GHOST_TIMEOUT_AS_LIVE: "critical",
    GHOST_UW_AS_CHARGE: "critical",
    GHOST_SIGHT_AS_MOUTH: "high",
    GHOST_CHARISMA: "high",
    GHOST_MISSING_MOUTH: "critical",
    GHOST_QUOTE_AS_STOP: "medium",
    GHOST_DEAD_FUSE_SOFT: "critical",
    GHOST_ACTED_NO_RECEIPT: "high",
}


def _flag(ghost: str, *, evidence: str, detail: str) -> dict[str, Any]:
    return {
        "ghost": ghost,
        "severity": SEVERITY.get(ghost, "medium"),
        "evidence": evidence,
        "detail": detail,
        "fix": "Ghost Bind — would stick without may",
    }


def scan(scenario: dict | None = None) -> dict[str, Any]:
    """Scan a bind-path scenario for ghosts.

    Input is intentionally plain (desk/audit/drill JSON) — not a live write.
    Output is haunt report; pair with Throat.evaluate for the mouth state.
    """
    s = scenario if isinstance(scenario, dict) else {}
    ghosts: list[dict[str, Any]] = []

    if s.get("soft_pas") or s.get("pas_allows_without_hop"):
        ghosts.append(
            _flag(
                GHOST_SOFT_PAS,
                evidence="soft_pas|pas_allows_without_hop",
                detail="PAS would stick the bind with no hop/mouth — soft may on a hard write.",
            )
        )
    if s.get("timeout_as_live") or (
        s.get("timeout") and _norm(s.get("decision")) in ("ALLOW", "LIVE", "GO")
    ):
        ghosts.append(
            _flag(
                GHOST_TIMEOUT_AS_LIVE,
                evidence="timeout_as_live|timeout+ALLOW",
                detail="Timeout treated as LIVE — classic silent fail-open.",
            )
        )
    if s.get("uw_approve_as_charge") or (
        s.get("uw_approved") and s.get("charge_id") in (None, "") and s.get("would_bind")
    ):
        ghosts.append(
            _flag(
                GHOST_UW_AS_CHARGE,
                evidence="uw_approve_as_charge|uw_approved without charge_id",
                detail="UW approve is not CHARGE. Resurrection of DEAD requires CHARGE only.",
            )
        )
    if s.get("sight_only") or s.get("dashboard_green_as_live"):
        ghosts.append(
            _flag(
                GHOST_SIGHT_AS_MOUTH,
                evidence="sight_only|dashboard_green_as_live",
                detail="Sight is not mouth — green dashboard is not LIVE.",
            )
        )
    if s.get("boss_said_yes") or s.get("charisma_live"):
        ghosts.append(
            _flag(
                GHOST_CHARISMA,
                evidence="boss_said_yes|charisma_live",
                detail="Soft charisma treated as LIVE — anti-charisma protocol applies.",
            )
        )
    if s.get("bind_path") and not s.get("throat_present") and not s.get("hop_required"):
        ghosts.append(
            _flag(
                GHOST_MISSING_MOUTH,
                evidence="bind_path without throat_present/hop_required",
                detail="Irreversible bind path with no Throat — mouth missing on the edge.",
            )
        )
    if s.get("quote_release_as_bind_stop"):
        ghosts.append(
            _flag(
                GHOST_QUOTE_AS_STOP,
                evidence="quote_release_as_bind_stop",
                detail="QuoteRelease is not a bind stop. BlocksBind / DEAD hop is.",
            )
        )
    if s.get("dead_fuse_continued") or (
        _norm(s.get("fuse_state")) in ("DEAD", "HALT") and s.get("would_bind")
    ):
        ghosts.append(
            _flag(
                GHOST_DEAD_FUSE_SOFT,
                evidence="dead_fuse_continued|DEAD+would_bind",
                detail="DEAD fuse soft-continued into bind — ghost authority.",
            )
        )
    if s.get("acted") and not (s.get("verify_url") or s.get("receipt_hash")):
        ghosts.append(
            _flag(
                GHOST_ACTED_NO_RECEIPT,
                evidence="acted without verify_url/receipt_hash",
                detail="Act without stranger receipt — prove gap.",
            )
        )

    haunted = bool(ghosts)
    critical = any(g["severity"] == "critical" for g in ghosts)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "haunted": haunted,
        "ghost_count": len(ghosts),
        "critical": critical,
        "ghosts": ghosts,
        "verdict": (
            "HAUNTED_CRITICAL"
            if critical
            else ("HAUNTED" if haunted else "CLEAR")
        ),
        "pairs_with": "Throat — mouth that chokes when ghosts would soft-allow",
        "rule": "Find would-stick-without-may before money moves. Haunt ≠ clear.",
        "scenario_echo": {
            k: s.get(k)
            for k in (
                "job_id",
                "fuse_id",
                "bind_path",
                "decision",
                "would_bind",
            )
            if k in s
        },
    }


def _norm(v: str | None) -> str:
    return (v or "").strip().upper()


def drill_scenarios() -> list[dict[str, Any]]:
    """Named drills for Bind Room / CUO packs — each should haunt or clear."""
    return [
        {
            "id": "soft_pas_stick",
            "expect": "HAUNTED_CRITICAL",
            "scenario": {"soft_pas": True, "would_bind": True, "bind_path": True},
        },
        {
            "id": "timeout_live",
            "expect": "HAUNTED_CRITICAL",
            "scenario": {"timeout": True, "decision": "ALLOW", "would_bind": True},
        },
        {
            "id": "uw_not_charge",
            "expect": "HAUNTED_CRITICAL",
            "scenario": {
                "uw_approved": True,
                "charge_id": None,
                "would_bind": True,
                "fuse_state": "DEAD",
            },
        },
        {
            "id": "boss_said_yes",
            "expect": "HAUNTED",
            "scenario": {"boss_said_yes": True, "would_bind": True},
        },
        {
            "id": "clean_halt",
            "expect": "CLEAR",
            "scenario": {
                "throat_present": True,
                "hop_required": True,
                "decision": "HALT",
                "would_bind": False,
                "verify_url": "https://example.test/verify?e=1",
            },
        },
        {
            "id": "clean_live",
            "expect": "CLEAR",
            "scenario": {
                "throat_present": True,
                "hop_required": True,
                "decision": "ALLOW",
                "would_bind": True,
                "verify_url": "https://example.test/verify?e=2",
                "acted": False,
            },
        },
    ]


def run_drills() -> dict[str, Any]:
    rows = []
    passed = 0
    for drill in drill_scenarios():
        report = scan(drill["scenario"])
        ok = report["verdict"] == drill["expect"] or (
            drill["expect"] == "HAUNTED"
            and report["verdict"] in ("HAUNTED", "HAUNTED_CRITICAL")
        )
        if ok:
            passed += 1
        rows.append(
            {
                "id": drill["id"],
                "expect": drill["expect"],
                "got": report["verdict"],
                "ok": ok,
                "ghost_count": report["ghost_count"],
            }
        )
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "drills": rows,
        "passed": passed,
        "total": len(rows),
        "all_ok": passed == len(rows),
    }


def attach_haunt(plan: dict, scenario: dict | None = None) -> dict:
    """Attach Ghost Bind haunt report onto a plan (audit stamp; does not clear)."""
    s = dict(scenario or {})
    s.setdefault("bind_path", True)
    s.setdefault("decision", plan.get("decision"))
    s.setdefault("would_bind", bool(plan.get("allow_bind") or plan.get("acted")))
    s.setdefault("acted", plan.get("acted"))
    s.setdefault("verify_url", plan.get("verify_url"))
    s.setdefault("throat_present", isinstance(plan.get("throat"), dict))
    s.setdefault("hop_required", True)
    if plan.get("timeout"):
        s["timeout"] = True
    if plan.get("soft_pas"):
        s["soft_pas"] = True
    if plan.get("sight_only"):
        s["sight_only"] = True
    report = scan(s)
    plan["ghost_bind"] = report
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Detector for would-stick-without-may — haunt soft PAS before money moves.",
        "ghost_classes": list(SEVERITY.keys()),
        "severity": SEVERITY,
        "pairs_with": "Throat — fail-closed mouth; Ghost Bind finds the haunt",
        "demo": f"POST {base}/demo/pas/ghost-bind",
        "drills": f"GET {base}/demo/pas/ghost-bind/drills",
        "well_known": f"{base}/.well-known/ghost-bind.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Audit/drill invention. Does not mint LIVE.",
    }
