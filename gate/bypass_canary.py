"""Bypass Canary pack — invention surface on gate.canary for Bind Room / CUO.

Invention (NORTH_STAR applicable-now): alarm when bind/write path is reachable
without a Gate hop. Proves they didn't go around you.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import canary as canary_mod
except ImportError:
    import canary as canary_mod

SPEC = "gate-bypass-canary-pack-v1"
INVENTION = "Bypass Canary"
FAMILY = "applicable_now"


def probe(*, write_path: str, job_id: str | None = None) -> dict[str, Any]:
    ev = canary_mod.evaluate(write_path=write_path, job_id=job_id)
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        **ev,
        "alarm": bool(ev.get("bypass_suspected")),
        "rule": "Welded irreversible write without redeemed Gate ticket → canary fires.",
        "not": ["clearance", "OSINT product", "SOC dashboard"],
    }


def fire(
    *,
    write_path: str,
    reporter: str,
    job_id: str | None = None,
    note: str = "",
    license_id: str | None = None,
    kill_parent: bool = False,
    confirm: bool = False,
) -> dict[str, Any]:
    report = canary_mod.report(
        write_path=write_path,
        job_id=job_id,
        reporter=reporter,
        note=note,
        license_id=license_id,
        kill_parent=kill_parent,
        confirm=confirm,
    )
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        **report,
        "rule": "Canary is civilizational alarm — never clearance permit.",
    }


def drills() -> dict[str, Any]:
    rows = []
    # Probe without job — no alarm
    a = probe(write_path="POST /job/v1/jobs/x/bind-only", job_id=None)
    rows.append({"id": "no_job_no_alarm", "ok": not a.get("alarm"), "got": a.get("alarm")})
    # Probe with job — suspected until ticket redeemed (map empty in unit context)
    b = probe(write_path="POST /job/v1/jobs/pc:CANARY/bind-only", job_id="pc:CANARY")
    rows.append(
        {
            "id": "unspent_job_suspects",
            "ok": b.get("bypass_suspected") is True,
            "got": b.get("bypass_suspected"),
        }
    )
    # Fire without confirm must fail
    c = fire(write_path="/bind-only", reporter="ops", confirm=False)
    rows.append({"id": "fire_requires_confirm", "ok": c.get("ok") is False, "got": c.get("ok")})
    passed = sum(1 for r in rows if r["ok"])
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "drills": rows,
        "passed": passed,
        "total": len(rows),
        "all_ok": passed == len(rows),
    }


def attach(plan: dict) -> dict:
    path = None
    sw = plan.get("spend_protocol", {}).get("write") if isinstance(plan.get("spend_protocol"), dict) else None
    if isinstance(sw, dict):
        path = f"{sw.get('method', 'POST')} {sw.get('path', '')}".strip()
    plan["bypass_canary"] = probe(write_path=path or "bind", job_id=plan.get("job_id"))
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Alarm when bind/write path is reachable without a Gate hop.",
        "probe": f"POST {base}/demo/pas/bypass-canary",
        "drills": f"GET {base}/demo/pas/bypass-canary/drills",
        "report": f"{base}/v1/canary/bypass",
        "well_known": f"{base}/.well-known/bypass-canary.json",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Production capture seed — never clearance.",
    }
