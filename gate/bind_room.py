"""Bind Room — two artifacts examiners actually take.

A) Officer pack (≤10 pages / SERFF-shaped) — titles on each Section 5 duty.
B) On-request appendix — each bind event → verify_url + hop. Not the SERFF filing.

Paid Bind Room redeems a production bind ticket (not /demo/) so the job_id
lands on the spend map. Second lookup is SPENT.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Any


SECTION_5 = [
    ("5.A.1", "Governing principles", "ECDIS/algorithms designed and monitored to prevent unfair discrimination."),
    ("5.A.2", "Roles and responsibilities", "FILL: title of the person who can stop bind-and-issue when the fuse is DEAD."),
    ("5.A.3", "Inventory and versioning", "List agent/bind automations. Gate is a control plane, not a rating model."),
    ("5.A.4", "Testing / validation", "DEAD drill: POST /demo/pas/bind-check → BLOCK + verify_url."),
    ("5.A.5", "Deployment / use controls", "PolicyCenter: hop before POST /job/v1/jobs/{id}/bind-and-issue."),
    ("5.A.6", "Ongoing monitoring", "Appendix B: bind events with verify permalinks. Timeout = HALT, never LIVE."),
    ("5.A.7", "Consumer complaints", "Use existing grievance procedures. Verify link is the independent proof."),
    ("5.A.8", "Risk prioritization", "Bind/issue and claims-pay are high-impact delegated action (AM Best Columbus 13 Aug 2026)."),
    ("5.A.9", "Model drift / performance", "Fuse state change is the drift that matters on the write path. CHARGE-only resurrect."),
    ("5.A.10", "Human-in-the-loop", "UW issue blocks bind. Approve without CHARGE does not resurrect."),
    ("5.A.11", "Vendor oversight", "Nisaba LLC / Gate. Control, not ECDIS. Audit rights in /listings/control-not-model.json."),
    ("5.A.12", "Third-party remains insurer duty", "Colorado 5.B / NAIC: carrier stays responsible. Do not file Gate as a rate model."),
    ("5.A.13", "Annual review", "Re-attest officer pack. Refresh appendix B from GET /v1/pas/bind-appendix."),
]


def officer_pack(public_url: str, contact_email: str) -> dict:
    return {
        "spec": "gate-bind-room-officer-pack-v1",
        "price": "$1,750",
        "filing": "Colorado Regulation 10-1-1 Section 6 — SERFF Annual Report, ≤10 pages, officer attestation",
        "not_the_filing": "Appendix B (verify permalinks) is on-request, not the SERFF body.",
        "also_maps": [
            "NYDFS Circular Letter 7 (2024) — board oversight, annual testing, vendor audit rights, 11 NYCRR 243",
            "NAIC AI Risk Evaluation Supplement Exhibit B 4h/4i — HITL consistently contributing; effectiveness of that HITL (not Exhibit C)",
            "AM Best @ NAIC BDAIWG 13 Aug 2026 (discussion only) — permissions, action logs, kill switch / rollback, person authority to override",
            "ASOP 56 — another actuary can reconstruct the bind-stop",
        ],
        "officer": {
            "attestation": "I attest this insurer can stop bind-and-issue when the fuse is DEAD, and a stranger can open the receipt.",
            "title_fill": "CUO / bind-desk / named Section 5 owner — FILL",
            "name_optional": "Colorado: names optional; titles required.",
        },
        "sections": [
            {"id": sid, "title": title, "guidance": guide} for sid, title, guide in SECTION_5
        ],
        "cta": {
            "book": f"{public_url}/bind-room",
            "install": f"{public_url}/install",
            "contact": contact_email,
            "demo": f"POST {public_url}/demo/pas/bind-check",
            "weld": f"POST {public_url}/v1/pas/policycenter/pre-bind",
        },
        "refuse": [
            "Do not lead with FRE 707 to a CUO.",
            "Do not sell model inventory (Monitaur's pile).",
            "Do not put PII on Gate.",
        ],
    }


def appendix_schema() -> dict:
    return {
        "spec": "gate-bind-room-appendix-v1",
        "use": "On-request examiner file. Not the SERFF 10-pager.",
        "item": {
            "id": "event id",
            "created_at": "ISO-8601 UTC",
            "fuse_id": "string",
            "job_id": "PAS job id only — no named insured",
            "decision": "ALLOW | BLOCK | HALT",
            "acted": False,
            "verify_url": "https://velaru.xyz/verify?...",
            "hop": "upstream hop object (no PII)",
        },
        "pull": "GET /v1/pas/bind-appendix",
    }


def exhibit_b_hitl(public_url: str) -> dict:
    """HITL maps to Exhibit B checklist 4h/4i — not Exhibit C (high-risk model details)."""
    return {
        "spec": "gate-exhibit-b-hitl-v1",
        "maps_to": {
            "exhibit": "B",
            "items": ["4h", "4i"],
            "not": "Exhibit C is AI Systems High-Risk Model Details — model fields, not HITL.",
            "source": "NAIC AI Risk Evaluation Supplement (former AI Systems Evaluation Tool)",
        },
        "when_review_happens": "Before POST bind-and-issue / issue. Timeout or DEAD → no write.",
        "who_can_override": "CHARGE webhook on Velaru only. PAS UW approve is not an override of DEAD.",
        "evidence_they_did": f"Appendix B verify_url per job_id from {public_url}/v1/pas/bind-appendix",
        "stop_the_system": (
            "AM Best presentation to NAIC BDAIWG Columbus 13 Aug 2026 — discussion only; "
            "does not change AM Best criteria/methodology/rating guidance. Agentic evidence: "
            "permissions tested, actions logged for reconstruction, kill switch to a safe state, "
            "person authority to override."
        ),
    }


def exhibit_c_hitl(public_url: str) -> dict:
    """Compat alias — old path name was wrong; payload is Exhibit B HITL."""
    out = exhibit_b_hitl(public_url)
    out["compat"] = {
        "old_path": "/bind-room/exhibit-c-hitl.json",
        "corrected_path": "/bind-room/exhibit-b-hitl.json",
        "reason": "HITL is Exhibit B 4h/4i; Exhibit C is high-risk model details.",
    }
    return out


PRODUCT = "bind_room"
FUSE_ID = "fuse_bind_room"
FIRST_JOB_ID = "br:bind-room"


def job_id_for_order(order: dict | None) -> str | None:
    if not isinstance(order, dict):
        return None
    if (order.get("product") or "").strip() != PRODUCT:
        return None
    oid = (order.get("id") or "").strip()
    if not oid:
        return None
    return f"br:{oid}"


def commit_spend(*, job_id: str, redeem_url: str, fuse_id: str = FUSE_ID) -> dict[str, Any]:
    """Issue + redeem on the production ticket path. Idempotent per job_id."""
    try:
        from gate import db
        from gate import spend_protocol
        from gate import ticket as ticket_mod
    except ImportError:
        import db
        import spend_protocol
        import ticket as ticket_mod

    jid = (job_id or "").strip()
    if not jid:
        return {"ok": False, "reason": "job_id_required", "demo": False}
    # Fast path — still not the lock. Enforcement is consume_bind_ticket BEGIN IMMEDIATE.
    if jid in db.consumed_spend_job_ids():
        return {
            "ok": True,
            "already": True,
            "job_id": jid,
            "spent": True,
            "demo": False,
            "word": "SPENT",
        }
    write = spend_protocol.write(job_id=jid)
    event_id = str(uuid.uuid4())
    issued = ticket_mod.issue(
        job_id=jid,
        fuse_id=(fuse_id or FUSE_ID),
        event_id=event_id,
        receipt_hash=None,
        redeem_url=redeem_url,
        spend_write=write,
    )
    if not issued or not isinstance(issued.get("bearer"), dict):
        return {"ok": False, "reason": "ticket_unissued", "job_id": jid, "demo": False}
    bearer = issued["bearer"]
    result = ticket_mod.redeem(
        ticket_id=str(bearer.get("ticket_id") or ""),
        token=str(bearer.get("token") or ""),
        job_id=jid,
        method=write["method"],
        path=write["path"],
        spend_fingerprint=str(bearer.get("spend_fingerprint") or ""),
        now=datetime.now(timezone.utc).isoformat(),
    )
    out = dict(result) if isinstance(result, dict) else {"ok": False, "reason": "redeem_failed"}
    out["demo"] = False
    out["job_id"] = jid
    if out.get("ok"):
        out["spent"] = True
        out["word"] = "SPENT"
        out["already"] = False
        return out
    # Concurrent commit_spend lost the job-level race — treat as already spent.
    if out.get("reason") == "job_already_spent":
        return {
            "ok": True,
            "already": True,
            "job_id": jid,
            "spent": True,
            "demo": False,
            "word": "SPENT",
            "prior_ticket_id": out.get("prior_ticket_id"),
        }
    return out


def commit_paid_order(order: dict | None, *, redeem_url: str) -> dict[str, Any] | None:
    if not isinstance(order, dict):
        return None
    if (order.get("status") or "").strip() != "paid":
        return None
    jid = job_id_for_order(order)
    if not jid:
        return None
    return commit_spend(job_id=jid, redeem_url=redeem_url)


def maybe_seed_first_job(*, redeem_url: str) -> dict[str, Any] | None:
    """First Bind Room leaf on Render when the map is still empty. Not a /demo/ call."""
    if os.getenv("RENDER") != "true":
        return None
    try:
        from gate import db
    except ImportError:
        import db

    if db.consumed_spend_job_ids():
        return None
    return commit_spend(job_id=FIRST_JOB_ID, redeem_url=redeem_url)
