"""Bind Room — two artifacts examiners actually take.

A) Officer pack (≤10 pages / SERFF-shaped) — titles on each Section 5 duty.
B) On-request appendix — each bind event → verify_url + hop. Not the SERFF filing.
"""
from __future__ import annotations


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
            "NAIC AI Risk Evaluation Supplement Exhibit C — HITL, who can override, that they did",
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


def exhibit_c_hitl(public_url: str) -> dict:
    return {
        "spec": "gate-exhibit-c-hitl-v1",
        "when_review_happens": "Before POST bind-and-issue / issue. Timeout or DEAD → no write.",
        "who_can_override": "CHARGE webhook on Velaru only. PAS UW approve is not an override of DEAD.",
        "evidence_they_did": f"Appendix B verify_url per job_id from {public_url}/v1/pas/bind-appendix",
        "stop_the_system": "AM Best (NAIC 13 Aug 2026, discussion only): permissions, action logs, rollback, ability to stop.",
    }


def full_map(public_url: str, contact_email: str) -> dict:
    """One receipt model. Nine irreversible doors. Weld one at a time.

    Follow-up artifact for Bind Room replies — not a second homepage.
    """
    pub = (public_url or "").rstrip("/")
    return {
        "spec": "gate-bind-room-full-map-v1",
        "title": "Full map — one fuse, nine doors",
        "thesis": (
            "Gate is the fail-closed clearance layer for every irreversible insurance write — "
            "bind, renew, endorse, certify, pay — with one receipt a stranger can open."
        ),
        "same_everywhere": {
            "hop": "CLEARANCE before the write. Timeout or DEAD → HALT. Never treat UNREACHABLE as LIVE.",
            "receipt": "verify_url + fuse_id + job_id. No named insured. No PII on Gate.",
            "appendix": f"GET {pub}/v1/pas/bind-appendix — on-request examiner file",
            "override": "CHARGE on Velaru only. PAS UW approve is not an override of DEAD.",
            "not": "Not ECDIS. Not a rating model. Not a second PAS.",
        },
        "rule": "Date all doors. Marry one write path this quarter.",
        "doors": [
            {
                "id": 1,
                "door": "Cloud API bind-only",
                "pain": "POST bind-only → status Bound. Contract exists. Documents later.",
                "weld": "Worker hop before bind-only. DEAD → UW issue with blocksBind.",
                "status": "marry_first",
                "artifact": f"{pub}/capture",
            },
            {
                "id": 2,
                "door": "Cloud API bind-and-issue",
                "pain": "Portal/automation spends bind + issue in one call.",
                "weld": "Same hop. Same do_not_call_all. Same BlocksBind issue type.",
                "status": "same_weld_as_1",
                "artifact": f"{pub}/demo/pas/policycenter/pre-bind",
            },
            {
                "id": 3,
                "door": "PolicyCenter UI Bind",
                "pain": "Console Bind never hits Cloud API. Worker cannot see it.",
                "weld": "Gosu checking set + Bind PCF before JobProcess.bind().",
                "status": "paste_on_first_prod",
                "artifact": f"{pub}/listings/guidewire-gosu-prebind.gs",
            },
            {
                "id": 4,
                "door": "Renewal auto-bind (midnight)",
                "pain": "Some renewals bind with no API call and no UI click.",
                "weld": "RenewalWF step before Bind. continue-on-error off.",
                "status": "line_item_after_door_1",
                "artifact": f"{pub}/listings/guidewire-renewal-prebind.gs",
            },
            {
                "id": 5,
                "door": "COI / certificate issuance",
                "pain": "Cert issued before bind cleared — proof of cover that is not Bound.",
                "weld": "Same fuse hop on cert/DocOrigin write. HALT blocks issuance.",
                "status": "upsell_same_customer",
                "artifact": None,
            },
            {
                "id": 6,
                "door": "Endorsement / retrospective authority",
                "pain": "Mid-term change or backdated authority spends without a halt.",
                "weld": "Endorsement weld variant — hop before irreversible endorse write.",
                "status": "upsell_same_customer",
                "artifact": None,
            },
            {
                "id": 7,
                "door": "Payment authorized ≠ bind authorized",
                "pain": "Wire/RTP/x402 cleared while bind fuse is DEAD — money moved, risk not.",
                "weld": "Prefinality GO/NO_GO before irreversible commit. Same receipt model.",
                "status": "second_rail",
                "artifact": f"{pub}/.well-known/prefinality.json",
            },
            {
                "id": 8,
                "door": "Sub-delegation / API keys / bots",
                "pain": "A key or agent binds under someone else's authority limit.",
                "weld": "Key-scoped fuse + appendix audit. Authority check on every hop.",
                "status": "same_customer_hardening",
                "artifact": f"{pub}/demo/pas/mga-authority",
            },
            {
                "id": 9,
                "door": "Partial-failure orphan / post-bind remediation",
                "pain": "Halfway job states after a failed bind path — recovery is surgery.",
                "weld": "Recovery pack after they have a near-miss. Not the first weld.",
                "status": "sell_after_near_miss",
                "artifact": None,
            },
        ],
        "sequence": [
            "Bind Room $1,750 — officer pack + appendix schema (cash, not a weld).",
            "Marry door 1 (+2): one production Cloud API bind path.",
            "Close doors 3–4 on the same weld SOW (UI + renewal paste).",
            "Upsell 5–8 on the same customer once appendix B pulls.",
            "Door 9 only when they say they already have orphan jobs.",
        ],
        "followup_blurb": (
            "Same receipt everywhere: hop → ALLOW/BLOCK/HALT → verify_url a stranger can open. "
            "Nine doors. We weld one this quarter — usually Cloud API bind-only. "
            "UI Bind and midnight renewal are paste artifacts on that same weld. "
            "COI, endorsement, payment pre-finality, and key-scoped bots come after appendix B is live. "
            f"Map: {pub}/bind-room/full-map · Pack: {pub}/bind-room"
        ),
        "cta": {
            "page": f"{pub}/bind-room/full-map",
            "json": f"{pub}/bind-room/full-map.json",
            "bind_room": f"{pub}/bind-room",
            "demo": f"POST {pub}/demo/pas/bind-check",
            "contact": contact_email,
        },
        "refuse": [
            "Do not demo nine doors on a first call.",
            "Do not lead with recovery / orphan remediation.",
            "Do not sell this as an AI platform or second PAS.",
        ],
    }
