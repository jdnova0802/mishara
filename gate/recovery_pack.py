"""RTP / wire fraud recovery pack — camt.056 contingency side bet.

Post-settlement voluntary return (FRAD / UAPA). Gate assembles evidence;
fee is contingency on recovered funds only.
"""
from __future__ import annotations

SPEC = "gate-recovery-pack-v1"
CONTINGENCY_PCT_LOW = 25
CONTINGENCY_PCT_HIGH = 33

REASON_CODES = (
    {"code": "FRAD", "rail": "FedNow / wire / ISO 20022", "meaning": "Fraudulent origin — unauthorized transfer"},
    {"code": "UAPA", "rail": "RTP", "meaning": "Authorized but fraudulently induced (BEC / impersonation)"},
    {"code": "FR01", "rail": "FedNow return", "meaning": "Payment return after fraud determination (pacs.004)"},
)

PARTNER_TYPES = (
    "Corporate treasury / CFO office after BEC or misdirected RTP push",
    "Wire-fraud or insurance subrogation counsel with open recovery file",
    "Bank fraud ops needing structured camt.056 narrative + pre-loss clearance log",
)


def pack(public_url: str, contact_email: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "headline": "After the push settles, the only move is camt.056 — we pack the case.",
        "one_liner": (
            "RTP and FedNow are irrevocable. No UK-style mandatory reimbursement in the US. "
            "Voluntary return requests need evidence. Contingency fee on recovered funds only."
        ),
        "problem": {
            "irrevocable": "Credit-push instant rails settle in seconds — no clawback window.",
            "us_gap": "Unlike UK APP mandatory reimbursement (up to £85k), US recovery is voluntary and often refused.",
            "mechanism": "Sender FI submits camt.056 (FRAD/UAPA) → receiving FI may return via pacs.004 — not guaranteed.",
        },
        "offer": {
            "fee_model": "contingency",
            "fee_range": f"{CONTINGENCY_PCT_LOW}–{CONTINGENCY_PCT_HIGH}% of gross recovered funds",
            "upfront": "$0",
            "minimum_case": "$50,000 lost (typical BEC / vendor impersonation / payroll redirect)",
            "deliverables": [
                "ISO 20022 camt.056 narrative + reason code selection (FRAD / UAPA)",
                "Fraud Classifier mapping for FedNow FRAD submissions",
                "Timeline: pre-finality clearance log (if Gate welded) or third-party payment metadata",
                "Indemnity language options for receiving-bank cooperation (camt.029 INDM path)",
                "Partner counsel handoff package for litigation if return refused",
            ],
        },
        "reason_codes": list(REASON_CODES),
        "partner_with": list(PARTNER_TYPES),
        "rails": ("RTP", "FedNow", "Fedwire ISO 20022", "Same-day ACH credit (Nacha R17 path)"),
        "prefinality_link": {
            "prevention": f"{base}/operator?write=withdraw",
            "evaluate": f"POST {base}/v1/prefinality/evaluate",
            "note": "Welded pre-commit gate reduces cases; recovery pack is post-loss.",
        },
        "intake": {
            "email": contact_email,
            "subject": "Gate recovery pack — camt.056",
            "fields": [
                "amount_usd",
                "settlement_date",
                "rail (RTP/FedNow/wire)",
                "sender_fi",
                "receiving_fi if known",
                "camt.056 already filed (yes/no)",
                "gate_welded (yes/no)",
            ],
        },
        "contact": contact_email,
        "operator": "Nisaba LLC",
        "legal_note": "Not a law firm. Work with counsel of record. Contingency terms in writing per engagement.",
    }


def render_one_pager(public_url: str, contact_email: str) -> str:
    base = (public_url or "").rstrip("/")
    p = pack(public_url, contact_email)
    lines = [
        "GATE — RTP / WIRE RECOVERY PACK (camt.056)",
        "==========================================",
        f"Nisaba LLC · {contact_email} · {base}/recovery",
        "",
        "WHEN",
        "  After irrevocable RTP, FedNow, or wire fraud — funds already credited.",
        "  US has no mandatory APP reimbursement. camt.056 is voluntary; banks often refuse.",
        "",
        "FEE",
        f"  {CONTINGENCY_PCT_LOW}–{CONTINGENCY_PCT_HIGH}% contingency on recovered funds only. $0 upfront.",
        "  Typical floor: $50k+ loss file.",
        "",
        "WE DELIVER",
    ]
    for item in p["offer"]["deliverables"]:
        lines.append(f"  · {item}")
    lines.extend(
        [
            "",
            "REASON CODES",
        ]
    )
    for rc in REASON_CODES:
        lines.append(f"  {rc['code']} ({rc['rail']}): {rc['meaning']}")
    lines.extend(
        [
            "",
            "INTAKE",
            f"  Email {contact_email}",
            "  Subject: Gate recovery pack — camt.056",
            "  Include: amount, date, rail, FIs, whether camt.056 already filed",
            "",
            "PREVENTION (separate product)",
            f"  Pre-commit weld: {base}/operator — clearance before irreversible push",
            "",
            "Not legal advice. Counsel of record required.",
        ]
    )
    return "\n".join(lines) + "\n"
