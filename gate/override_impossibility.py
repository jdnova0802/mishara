"""Override Impossibility Packet — stranger proof admin cannot lift epoch lock.

Engineers grep for bypass after Parakhin + fail-closed. This packet names every
resurrection path and marks which are forged vs CHARGE-only.
"""
from __future__ import annotations

from typing import Any

SPEC = "gate-override-impossibility-v1"
INVENTION = "Override Impossibility Packet"
FAMILY = "competitive-response"

RESURRECTION_PATHS = (
    {
        "path": "velaru_charge_webhook",
        "forged": False,
        "lifts_epoch": True,
        "note": "Only verified CHARGE authority consumed for epoch purpose.",
    },
    {
        "path": "uw_approve_without_charge",
        "forged": True,
        "lifts_epoch": False,
        "note": "Charge Bride — forged resurrection.",
    },
    {
        "path": "admin_console_resurrect",
        "forged": True,
        "lifts_epoch": False,
        "note": "No admin resurrect API on bind path.",
    },
    {
        "path": "chat_yes_boss_said_yes",
        "forged": True,
        "lifts_epoch": False,
        "note": "Anti-charisma — soft yes does not lift HALT.",
    },
    {
        "path": "ttl_expiry_as_revocation",
        "forged": True,
        "lifts_epoch": False,
        "note": "TTL is freshness on ticket, not epoch unlock.",
    },
    {
        "path": "offline_ticket_spend",
        "forged": True,
        "lifts_epoch": False,
        "note": "Redeem is server-side; no bearer offline bind.",
    },
    {
        "path": "cold_standby_mirror",
        "forged": True,
        "lifts_epoch": False,
        "note": "Witness only — may_mint_live false.",
    },
    {
        "path": "fail_open_on_outage",
        "forged": True,
        "lifts_epoch": False,
        "note": "Redeem down means bind down — by design.",
    },
)


def packet(*, job_id: str | None = None, epoch_locked: bool | None = None) -> dict[str, Any]:
    jid = (job_id or "").strip() or None
    forged = [p for p in RESURRECTION_PATHS if p["forged"]]
    real = [p for p in RESURRECTION_PATHS if not p["forged"]]
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "job_id": jid,
        "epoch_locked": bool(epoch_locked) if epoch_locked is not None else None,
        "impossibility_claim": (
            "No operator path lifts epoch lock without verified Velaru CHARGE."
        ),
        "forged_paths": forged,
        "real_paths": real,
        "forged_count": len(forged),
        "real_count": len(real),
        "patent_lane": "epoch_lock_non_resurrecting_halt",
        "grep_hints": [
            "admin_resurrect",
            "uw_approve_as_charge",
            "fail_open",
            "offline_grant",
        ],
        "rule": "Packet is diligence artifact — patent prose made auditable.",
    }


def attach(plan: dict) -> dict:
    ep = plan.get("epoch") if isinstance(plan.get("epoch"), dict) else {}
    if ep.get("locked") or plan.get("halt"):
        plan["override_impossibility"] = packet(
            job_id=str(plan.get("job_id") or ""),
            epoch_locked=bool(ep.get("locked") or plan.get("halt")),
        )
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Stranger-verifiable: no admin bypass of epoch lock — grep packet.",
        "demo": f"GET {base}/demo/pas/override-impossibility",
        "demo_job": f"GET {base}/demo/pas/override-impossibility?job_id={{job_id}}",
        "well_known": f"{base}/.well-known/override-impossibility.json",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
        "posture": "Weld deliverable for carrier security review.",
    }
