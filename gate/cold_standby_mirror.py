"""Cold Standby Mirror — HALT witness without resurrection power.

Fail-closed redeem makes availability the third engineer question.
The mirror proves last HALT + epoch during outage — it cannot mint LIVE or consume tickets.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import db
except ImportError:
    import db

SPEC = "gate-cold-standby-mirror-v1"
INVENTION = "Cold Standby Mirror"
FAMILY = "competitive-response"

FORBIDDEN = (
    "mint_live",
    "consume_ticket",
    "admin_resurrect",
    "fail_open_bind",
)


def witness(*, job_id: str | None = None, outage_simulated: bool = False) -> dict[str, Any]:
    jid = (job_id or "").strip()
    latest = db.latest_bind_event_for_job(jid) if jid else db.latest_bind_event_any()
    row = latest if isinstance(latest, dict) else {}
    dec = (row.get("decision") or "").upper()
    locked = dec in ("HALT", "BLOCK")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "mode": "read_only_witness",
        "outage_simulated": bool(outage_simulated),
        "may_mint_live": False,
        "may_consume_ticket": False,
        "may_admin_resurrect": False,
        "forbidden_capabilities": list(FORBIDDEN),
        "last_known": {
            "job_id": row.get("job_id"),
            "event_id": row.get("id"),
            "decision": dec or None,
            "epoch_locked": locked,
            "verify_url": row.get("verify_url"),
            "receipt_hash": row.get("receipt_hash"),
            "created_at": row.get("created_at"),
        },
        "bind_allowed_via_mirror": False,
        "rule": (
            "Mirror proves last HALT during outage. "
            "Availability without fail-open hole."
        ),
        "stavan_line": (
            "When primary redeem is down, mirror shows last HALT — "
            "it does not mint a ghost bind."
        ),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Read-only HALT witness for outage — cannot mint LIVE or burn tickets.",
        "demo": f"GET {base}/demo/pas/cold-standby-mirror",
        "demo_outage": f"GET {base}/demo/pas/cold-standby-mirror?outage=1",
        "well_known": f"{base}/.well-known/cold-standby-mirror.json",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
        "posture": "Roadmap artifact for production weld SLA — not fail-open bypass.",
    }
