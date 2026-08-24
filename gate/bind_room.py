"""Bind Room — two artifacts examiners actually take.

A) Officer pack (≤10 pages / SERFF-shaped) — titles on each Section 5 duty.
B) On-request appendix — each bind event → verify_url + hop. Not the SERFF filing.
"""
from __future__ import annotations


SECTION_5 = [
    ("5.A.1", "Governing principles", "ECDIS/algorithms designed and monitored to prevent unfair discrimination."),
    ("5.A.2", "Roles and responsibilities", "FILL: title of the person who can stop bind-and-issue when the fuse is DEAD."),
    ("5.A.3", "Inventory and versioning", "List agent/bind automations. Gate is a control plane, not a rating model."),
    ("5.A.4", "Testing / validation", "DEAD drill: POST /demo/pas/bind-check → BLOCK + verify_url. Throat CHOKE + Ghost Bind drills: /demo/pas/throat, /demo/pas/ghost-bind/drills. Stick Meter scoreboard + Charge Bride forged-resurrection drills."),
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
        "inventions": {
            "throat": f"{public_url}/bind-room/throat.json",
            "ghost_bind": f"{public_url}/bind-room/ghost-bind.json",
            "stick_meter": f"{public_url}/bind-room/stick-meter.json",
            "charge_bride": f"{public_url}/bind-room/charge-bride.json",
            "hop_tattoo": f"{public_url}/bind-room/hop-tattoo.json",
            "soft_yes_snare": f"{public_url}/bind-room/soft-yes-snare.json",
            "mass_tag": f"{public_url}/bind-room/mass-tag.json",
            "issue_bind_splitter": f"{public_url}/bind-room/issue-bind-splitter.json",
            "ticket_fuse_pack": f"{public_url}/bind-room/ticket-fuse-pack.json",
            "payout_throat": f"{public_url}/bind-room/payout-throat.json",
            "twin_diode": f"{public_url}/bind-room/twin-diode.json",
            "agent_passport_weld": f"{public_url}/bind-room/agent-passport-weld.json",
            "bypass_canary": f"{public_url}/bind-room/bypass-canary.json",
            "restraint_invoice": f"{public_url}/bind-room/restraint-invoice.json",
            "desk_quorum_fob": f"{public_url}/bind-room/desk-quorum-fob.json",
            "panic_latch": f"{public_url}/bind-room/panic-latch.json",
            "receipt_mirror": f"{public_url}/bind-room/receipt-mirror.json",
            "deadman_echo": f"{public_url}/bind-room/deadman-echo.json",
            "witness_seat": f"{public_url}/bind-room/witness-seat.json",
            "pardon_sunset": f"{public_url}/bind-room/pardon-sunset.json",
            "watchman_fuse": f"{public_url}/bind-room/watchman-fuse.json",
            "indulgence_trap": f"{public_url}/bind-room/indulgence-trap.json",
            "bind_path_compiler": f"{public_url}/bind-room/bind-path-compiler.json",
            "gate_od_skins": f"{public_url}/bind-room/gate-od-skins.json",
            "restraint_unit": f"{public_url}/bind-room/restraint-unit.json",
            "oath_compiler": f"{public_url}/bind-room/oath-compiler.json",
            "larp_gap_pack": f"{public_url}/.well-known/larp-gap-pack.json",
            "temporal_sheath": f"{public_url}/.well-known/temporal-sheath.json",
            "pair": "Action OS foothill — ρ restraint unit + Oath Compiler; Bind Path + Gate-C/D/O; Moral Throat on finalize.",
        },
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
