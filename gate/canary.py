"""Bypass canaries — detect irreversible writes that skipped Gate.

A canary is an attestation that spend occurred (or was attempted) on a welded
path *without* a matching redeemed Gate ticket in the spend map.

When a canary fires:
- record the alarm (append-only)
- optionally DEAD the named license parent (children cannot redeem)
- never flip their_production; never treat canary as clearance permit

Ops-reported for now. Future: worker heartbeat / dual-rail sensors.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import license_fuse as license_fuse_mod
except ImportError:
    import license_fuse as license_fuse_mod

try:
    from gate import exclusion as exclusion_mod
except ImportError:
    import exclusion as exclusion_mod

SPEC = "gate-bypass-canary-v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def evaluate(*, write_path: str, job_id: str | None = None) -> dict[str, Any]:
    """Does Gate's redeemed-ticket map contain a spend leaf for this job?"""
    jid = (job_id or "").strip() or None
    path = (write_path or "").strip()
    spent = False
    exclusion = None
    if jid:
        exclusion = exclusion_mod.prove(jid)
        spent = bool(exclusion.get("spent"))
    return {
        "spec": SPEC,
        "write_path": path,
        "job_id": jid,
        "spent_in_gate_map": spent,
        "bypass_suspected": bool(jid) and not spent,
        "exclusion": exclusion,
        "note": (
            "Absence in Gate's map is not metaphysical non-occurrence — "
            "it is evidence the exclusive door may have been skipped."
            if (jid and not spent)
            else None
        ),
    }


def report(
    *,
    write_path: str,
    job_id: str | None = None,
    reporter: str,
    note: str = "",
    license_id: str | None = None,
    kill_parent: bool = False,
    confirm: bool = False,
) -> dict[str, Any]:
    """Record a bypass canary. Requires confirm=True."""
    if not confirm:
        return {
            "ok": False,
            "error": "confirm=True required — canary is a civilizational alarm, not a drill checkbox",
            "their_production": False,
        }
    path = (write_path or "").strip()
    who = (reporter or "").strip()
    if not path or not who:
        return {"ok": False, "error": "write_path and reporter required"}
    ev = evaluate(write_path=path, job_id=job_id)
    parent_state = None
    if kill_parent and license_id:
        dead = license_fuse_mod.dead(license_id=license_id)
        parent_state = dead
    row = db.record_bypass_canary(
        write_path=path,
        job_id=(job_id or "").strip() or None,
        reporter=who,
        note=note,
        license_id=(license_id or "").strip() or None,
        bypass_suspected=bool(ev.get("bypass_suspected")),
        killed_parent=bool(kill_parent and license_id),
    )
    return {
        "ok": True,
        "spec": SPEC,
        "canary": row,
        "evaluation": ev,
        "parent": parent_state,
        "severity": "BYPASS" if ev.get("bypass_suspected") else "REPORTED",
        "their_production": False,
        "evaluated_at": _now(),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    recent = db.list_bypass_canaries(limit=25)
    open_alarms = [c for c in recent if c.get("bypass_suspected")]
    return {
        "spec": SPEC,
        "name": "Bypass canary",
        "what": "Alarm when a welded irreversible write may have skipped Gate's exclusive door.",
        "not": [
            "OSINT product",
            "SOC dashboard",
            "permission to spend",
            "SaaS alert tier",
        ],
        "open_alarms": len(open_alarms),
        "recent": recent[:10],
        "report": f"{base}/v1/canary/bypass",
        "live": f"{base}/live",
        "live_json": f"{base}/.well-known/live.json",
        "their_production": False,
        "gatekeep": "Canary proves suspicion in Gate's map. Exclusive door is still physics.",
    }
