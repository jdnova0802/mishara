"""Live clearance desk — civilizational clock, not a SaaS status page.

For each welded path (and canary alarms), expose:
  path · clock · state · authority · proof · non-event

Strangers can read /.well-known/live.json. Commanders read /live.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import production_skin as production_skin_mod
except ImportError:
    import production_skin as production_skin_mod

try:
    from gate import canary as canary_mod
except ImportError:
    import canary as canary_mod

SPEC = "gate-live-desk-v1"
INVENTOR = "Nisaba LLC · Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path_row_from_weld(weld: dict, *, public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    path = weld.get("write_path") or ""
    # Latest bind event loosely related by path substring is expensive; use
    # latest production/dogfood metadata + global latest event for clock pulse.
    latest = db.latest_bind_event_any()
    license_id = None
    auth = None
    state = "WELDED"
    if weld.get("exclusivity_attested"):
        state = "EXCLUSIVE"
    if not production_skin_mod.their_production() and not weld.get("exclusivity_attested"):
        state = "ATTESTED" if weld.get("id") else "UNKNOWN"
    clock = weld.get("created_at")
    verify = None
    event_id = None
    decision = None
    if latest:
        clock = latest.get("created_at") or clock
        verify = latest.get("verify_url")
        event_id = latest.get("id")
        decision = latest.get("decision")
        if latest.get("acted") is True:
            state = "SPENT"
        elif (decision or "").upper() in ("HALT", "BLOCK"):
            state = "HALTED"
    return {
        "write_path": path,
        "counterparty": weld.get("counterparty") or weld.get("operator"),
        "door_kind": weld.get("door_kind"),
        "exclusive_door_url": weld.get("exclusive_door_url"),
        "exclusivity_attested": bool(weld.get("exclusivity_attested")),
        "their_production": bool(weld.get("their_production") or production_skin_mod.their_production()),
        "state": state,
        "clock": clock,
        "decision": decision,
        "event_id": event_id,
        "verify_url": verify,
        "receipt": f"{base}/.well-known/receipt/{event_id}.json" if event_id else None,
        "authority": auth,
        "license_id": license_id,
        "kind": "production" if weld.get("counterparty") else "dogfood",
    }


def desk(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    prod = production_skin_mod.their_production()
    dogfood = production_skin_mod.has_dogfood_weld()
    latest_prod = db.latest_production_weld()
    latest_dog = db.latest_dogfood_weld()
    paths: list[dict[str, Any]] = []
    if latest_prod:
        row = _path_row_from_weld({**latest_prod, "their_production": True}, public_url=base)
        paths.append(row)
    if latest_dog:
        row = _path_row_from_weld({**latest_dog, "their_production": False}, public_url=base)
        # Don't duplicate if same path
        if not paths or paths[0].get("write_path") != row.get("write_path"):
            paths.append(row)

    canaries = db.list_bypass_canaries(limit=20)
    open_alarms = [c for c in canaries if c.get("bypass_suspected")]

    # Pulse: most recent clearance event anywhere (metronome)
    pulse = db.latest_bind_event_any()
    pulse_block = None
    if pulse:
        pulse_block = {
            "event_id": pulse.get("id"),
            "decision": pulse.get("decision"),
            "acted": pulse.get("acted"),
            "job_id": pulse.get("job_id"),
            "fuse_id": pulse.get("fuse_id"),
            "clock": pulse.get("created_at"),
            "verify_url": pulse.get("verify_url"),
            "receipt": f"{base}/.well-known/receipt/{pulse.get('id')}.json",
        }

    # License authority sample (if any LIVE/DEAD parents exist)
    authorities = db.list_license_parents(limit=12)

    return {
        "spec": SPEC,
        "name": "Gate Live",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "time_is_utc": True,
        "question": "Can this irreversible write still execute right now?",
        "not": [
            "SaaS status page",
            "uptime badge",
            "marketing ticker",
            "newsroom opinion",
        ],
        "their_production": prod,
        "dogfood_weld": dogfood,
        "pulse": pulse_block,
        "paths": paths,
        "authorities": [
            {
                "license_id": a.get("license_id"),
                "state": a.get("state"),
                "updated_at": a.get("updated_at"),
                "children_cannot_outlive_parent": True,
            }
            for a in authorities
        ],
        "canaries": {
            "open_alarms": len(open_alarms),
            "recent": canaries[:8],
            "spec": canary_mod.SPEC,
        },
        "fail_closed": "uncertain / timeout / unreachable → write does not run",
        "links": {
            "page": f"{base}/live",
            "json": f"{base}/.well-known/live.json",
            "canary": f"{base}/.well-known/canary.json",
            "operator": f"{base}/operator",
            "trust": f"{base}/trust",
            "verify": "https://velaru.xyz/verify",
        },
        "gatekeep": (
            "This desk shows clearance clock and bypass alarms. "
            "It is not a seat product. It is not permission to spend."
        ),
    }
