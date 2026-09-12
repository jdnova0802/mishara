"""
Mishara — consumer AI rights door (Nisaba LLC).
Powered by Velaru. Not Gate. Not Erra.

Products:
  1. Harm Receipt (free)
  2. Demand Pack ($99)
  3. Advocate Bundle ($499)
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request, url_for

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("MISHARA_SECRET_KEY", secrets.token_hex(24))

VELARU_BASE = os.getenv("VELARU_API_URL", "https://velaru.xyz").rstrip("/")
VELARU_VERIFY = os.getenv("VELARU_VERIFY_URL", "https://velaru.xyz/verify").rstrip("/")
DB_PATH = os.getenv("MISHARA_DB_PATH", os.path.join(os.path.dirname(__file__), "mishara.db"))
PAYMENTS_MODE = (os.getenv("MISHARA_PAYMENTS") or "stripe").strip().lower()
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "").strip()
PUBLIC_BASE = os.getenv("MISHARA_PUBLIC_URL", "").rstrip("/")
CONTACT_EMAIL = os.getenv("MISHARA_CONTACT_EMAIL", "hello@velaru.xyz")

PRODUCTS = {
    "harm_receipt": {
        "id": "harm_receipt",
        "name": "Harm Receipt",
        "price_cents": 0,
        "price_label": "Free",
        "blurb": "Describe the denial. Get a Velaru-signed receipt and verify URL.",
        "includes": ["Velaru-signed receipt", "Stranger verify URL", "Plain-English next step"],
    },
    "demand_pack": {
        "id": "demand_pack",
        "name": "Demand Pack",
        "price_cents": 9900,
        "price_label": "$99",
        "blurb": "Receipt + rights map + demand letter you can send.",
        "includes": [
            "Everything in Harm Receipt",
            "FCRA / ECOA / hiring-tool rights map",
            "Demand letter with Exhibit A = receipt hash",
        ],
    },
    "advocate_bundle": {
        "id": "advocate_bundle",
        "name": "Advocate Bundle",
        "price_cents": 49900,
        "price_label": "$499",
        "blurb": "Demand Pack plus pattern join and advocate export.",
        "includes": [
            "Everything in Demand Pack",
            "Anonymous pattern join + alert email",
            "Advocate export (JSON + TXT) for counsel",
        ],
    },
}

HARM_TYPES = {
    "hiring": {"label": "Hiring & Employment", "hint": "Application rejected, interview denied, wrongful termination", "velaru_domain": "hiring"},
    "housing": {"label": "Housing & Tenant Screening", "hint": "Rental denied, AI screening, credit report used", "velaru_domain": "tenant_screening"},
    "financial": {"label": "Financial & Credit", "hint": "Loan denied, insurance claim rejected, credit harm", "velaru_domain": "insurance"},
    "social_media": {"label": "Social Media & Platforms", "hint": "Shadowban, demonetization, account suspended", "velaru_domain": "content_moderation"},
    "gig_work": {"label": "Gig Work", "hint": "Deactivated, unfair rating, pay suppression", "velaru_domain": "gig_worker"},
    "healthcare": {"label": "Healthcare", "hint": "Treatment denied, AI coverage decision", "velaru_domain": "healthcare"},
    "government": {"label": "Government & Benefits", "hint": "Benefits denied, immigration, public services", "velaru_domain": "government_benefits"},
    "pricing": {"label": "Pricing & Consumer", "hint": "Discriminatory or opaque algorithmic pricing", "velaru_domain": "price_discrimination"},
    "privacy": {"label": "Privacy & Data", "hint": "Unauthorized profiling or data use", "velaru_domain": "data_poisoning"},
    "education": {"label": "Education", "hint": "Admissions denial, academic AI decision", "velaru_domain": "education"},
    "other": {"label": "Other", "hint": "Describe what happened in your own words", "velaru_domain": "companion"},
}

RIGHTS_BY_DOMAIN = {
    "hiring": [
        "Under Title VII / EEOC guidance you may request the reason for an AI-assisted hiring decision.",
        "NYC Local Law 144 and several states require notice when AEDTs are used — ask whether a tool was used.",
        "You can file with the EEOC (often within 180–300 days) and keep this receipt as your independent record.",
    ],
    "tenant_screening": [
        "FCRA requires an adverse action notice when a consumer report contributes to a housing denial.",
        "Fair Housing Act bars discrimination; request the screening report and dispute inaccuracies.",
        "HUD and local fair-housing groups take complaints — attach your verify URL.",
    ],
    "insurance": [
        "FCRA / ECOA-style adverse action rules often require specific principal reasons — request them in writing.",
        "State insurance commissioners investigate unfair algorithmic denials.",
        "Keep screenshots and this cryptographic receipt for any appeal.",
    ],
    "content_moderation": [
        "Document every moderation action with dates and screenshots.",
        "DSA (EU) and emerging state laws push for appeal paths on automated moderation.",
        "EFF and digital-rights groups can help you read platform accountability options.",
    ],
    "gig_worker": [
        "Many jurisdictions require notice before deactivation — check your state worker rules.",
        "Preserve ratings, pay history, and the deactivation notice as evidence.",
        "NLRB and gig-worker advocates track organizing and unfair practices.",
    ],
    "healthcare": [
        "HIPAA gives access to records that informed care decisions.",
        "Coverage denials must usually state a reason and an appeal path — demand both in writing.",
        "Patient advocates can help challenge AI-assisted utilization denials.",
    ],
    "government_benefits": [
        "You generally have a right to a written explanation and a deadline to appeal.",
        "Legal aid can help with benefits and immigration AI decisions.",
        "Missing appeal deadlines is the most common secondary harm — calendar them now.",
    ],
    "price_discrimination": [
        "Protected-class discrimination in pricing can violate state consumer laws.",
        "FTC and state AGs investigate unfair algorithmic pricing.",
        "Save screenshots of different prices for the same offer.",
    ],
    "data_poisoning": [
        "CCPA/CPRA and GDPR can support access and opt-out of profiling.",
        "Ask what data fed the automated decision that affected you.",
        "State AGs take privacy complaints; keep this receipt.",
    ],
    "education": [
        "Title VI and state equity rules can apply to admissions tools.",
        "Request your file and any AI scores or flags.",
        "Document the timeline from application to denial for appeals.",
    ],
    "companion": [
        "You can ask whether an automated system made the decision that affected you.",
        "Request a human review and a written explanation.",
        "This receipt is independent proof of what was recorded and when.",
    ],
}

HELP_RESOURCES = {
    "hiring": [
        {"name": "EEOC", "url": "https://www.eeoc.gov", "note": "Employment discrimination charges"},
        {"name": "Workplace Fairness", "url": "https://www.workplacefairness.org", "note": "Worker rights and referrals"},
    ],
    "tenant_screening": [
        {"name": "HUD Fair Housing", "url": "https://www.hud.gov/fairhousing", "note": "Housing discrimination"},
        {"name": "National Fair Housing Alliance", "url": "https://nationalfairhousing.org", "note": "Advocacy"},
    ],
    "insurance": [
        {"name": "CFPB complaints", "url": "https://www.consumerfinance.gov/complaint", "note": "Credit and lending"},
        {"name": "NAIC consumer map", "url": "https://content.naic.org/consumer", "note": "State insurance regulator"},
    ],
    "content_moderation": [
        {"name": "EFF", "url": "https://www.eff.org", "note": "Digital rights"},
        {"name": "Accountable Tech", "url": "https://accountabletech.org", "note": "Platform reform"},
    ],
    "gig_worker": [
        {"name": "NLRB", "url": "https://www.nlrb.gov", "note": "Worker organizing"},
        {"name": "Gig Workers Rising", "url": "https://gigworkersrising.org", "note": "Gig advocacy"},
    ],
    "healthcare": [
        {"name": "Patient Advocate Foundation", "url": "https://www.patientadvocate.org", "note": "Appeals help"},
        {"name": "CMS", "url": "https://www.cms.gov", "note": "Medicare/Medicaid appeals"},
    ],
    "government_benefits": [
        {"name": "Legal Services Corporation", "url": "https://www.lsc.gov/find-legal-aid", "note": "Free legal aid"},
        {"name": "USA.gov benefits", "url": "https://www.usa.gov/benefits", "note": "Federal benefits"},
    ],
    "price_discrimination": [
        {"name": "FTC ReportFraud", "url": "https://reportfraud.ftc.gov", "note": "Unfair pricing"},
        {"name": "Find your AG", "url": "https://www.naag.org/find-my-ag", "note": "State AG"},
    ],
    "data_poisoning": [
        {"name": "EFF Privacy", "url": "https://www.eff.org/issues/privacy", "note": "Privacy rights"},
        {"name": "EPIC", "url": "https://epic.org", "note": "Privacy advocacy"},
    ],
    "education": [
        {"name": "ED OCR", "url": "https://www2.ed.gov/about/offices/list/ocr", "note": "Education discrimination"},
        {"name": "ACLU students", "url": "https://www.aclu.org/know-your-rights/students-rights", "note": "Student rights"},
    ],
    "companion": [
        {"name": "EFF", "url": "https://www.eff.org", "note": "Digital rights"},
        {"name": "Legal aid finder", "url": "https://www.lsc.gov/find-legal-aid", "note": "Free legal aid"},
    ],
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    parent = os.path.dirname(DB_PATH)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with get_db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                domain TEXT NOT NULL,
                harm_type TEXT NOT NULL,
                classification TEXT NOT NULL,
                receipt_hash TEXT NOT NULL UNIQUE,
                incident_date TEXT,
                product_id TEXT NOT NULL DEFAULT 'harm_receipt',
                created_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_submissions_platform_domain
                ON submissions(platform, domain);
            CREATE TABLE IF NOT EXISTS patterns (
                platform TEXT NOT NULL,
                domain TEXT NOT NULL,
                count INTEGER NOT NULL DEFAULT 0,
                last_updated TEXT NOT NULL,
                PRIMARY KEY (platform, domain)
            );
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_hash TEXT NOT NULL,
                platform TEXT NOT NULL,
                domain TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS unlocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                unlock_token TEXT NOT NULL UNIQUE,
                receipt_hash TEXT NOT NULL,
                product_id TEXT NOT NULL,
                status TEXT NOT NULL,
                stripe_session_id TEXT,
                created_at TEXT NOT NULL,
                fulfilled_at TEXT
            );
            CREATE TABLE IF NOT EXISTS receipt_cache (
                receipt_hash TEXT PRIMARY KEY,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            """
        )


def normalize_platform(name: str) -> str:
    return (name or "unknown").strip().lower()[:120]


def public_url(path: str = "") -> str:
    if PUBLIC_BASE:
        return f"{PUBLIC_BASE}{path}"
    return f"{request.url_root.rstrip('/')}{path}"


def mint_unlock_token(receipt_hash: str, product_id: str) -> str:
    nonce = secrets.token_urlsafe(18)
    digest = hmac.new(
        app.config["SECRET_KEY"].encode("utf-8"),
        f"{receipt_hash}:{product_id}:{nonce}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:20]
    return f"msh_{nonce}_{digest}"


def velaru_classify(description: str, velaru_domain: str, session_id: str | None = None) -> tuple[dict | None, str | None]:
    payload = {
        "message": description,
        "domain": velaru_domain,
        "modality": "text",
        "communication_form": "form",
        "language": "auto",
        "session_id": session_id or f"mishara-{uuid.uuid4().hex[:16]}",
    }
    req = urllib.request.Request(
        f"{VELARU_BASE}/classify",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mishara/2.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        try:
            err = json.loads(body)
        except json.JSONDecodeError:
            err = {"message": body or str(e)}
        return None, err.get("message") or err.get("error") or f"Velaru error {e.code}"
    except Exception as e:
        return None, str(e)


def velaru_health_ok() -> bool:
    try:
        with urllib.request.urlopen(f"{VELARU_BASE}/health", timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("status") in ("ok", "degraded")
    except Exception:
        return False


def openai_text(system_prompt: str, user_prompt: str, max_tokens: int = 900) -> str | None:
    if not os.environ.get("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI

        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        resp = client.chat.completions.create(
            model=os.getenv("MISHARA_OPENAI_MODEL", "gpt-4o-mini"),
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return (resp.choices[0].message.content or "").strip() or None
    except Exception:
        return None


def fallback_explanation(classification: str, velaru_domain: str, reason: str = "") -> str:
    harm = next((v for v in HARM_TYPES.values() if v["velaru_domain"] == velaru_domain), HARM_TYPES["other"])
    cls = (classification or "UNKNOWN").upper()
    if cls in {"VIOLATION", "UNSAFE", "BLOCK", "DENY"}:
        lead = f"Independent audit marked elevated risk in {harm['label']}. {reason}".strip()
    else:
        lead = (
            f"Your experience in {harm['label']} is now on a signed record. "
            "Even a lower-severity label still matters if this escalates."
        )
    return (
        f"{lead} Here is what you should know: you have a stranger-verifiable receipt. "
        "Next step today: save it and ask the company for a human review in writing."
    )


def plain_english_explanation(classification: str, velaru_domain: str, description: str, reason: str = "") -> str:
    system = (
        "You are Mishara's plain-English AI rights advisor for a harmed person. "
        "Explain in 2-3 sentences what the classification means. Be warm and concrete. "
        "Never say you cannot give legal advice — say 'Here is what you should know.' "
        "End with one action they can take today."
    )
    user = (
        f"Domain: {velaru_domain}\nClassification: {classification}\nReason: {reason}\n"
        f"Description summary: {description[:500]}"
    )
    return openai_text(system, user, max_tokens=320) or fallback_explanation(classification, velaru_domain, reason)


def generate_demand_letter(
    platform: str,
    description: str,
    classification: str,
    velaru_domain: str,
    receipt_hash: str,
    reason: str = "",
) -> str:
    system = (
        "Draft a firm consumer demand letter. Plain text only. Include [DATE], platform as recipient, "
        "factual summary, relevant rights for the domain, Exhibit A = Velaru receipt hash, and demands: "
        "written explanation, human review in 15 business days, preservation of records."
    )
    user = (
        f"Platform: {platform}\nDomain: {velaru_domain}\nClassification: {classification}\n"
        f"Receipt hash: {receipt_hash}\nReason: {reason}\n\nAccount:\n{description}"
    )
    result = openai_text(system, user, max_tokens=1100)
    if result:
        return result
    rights = RIGHTS_BY_DOMAIN.get(velaru_domain, RIGHTS_BY_DOMAIN["companion"])
    return f"""[DATE]

{platform}
Attention: Customer Trust & Legal

RE: Formal demand — AI-assisted decision affecting my rights
Exhibit A: Velaru cryptographic receipt {receipt_hash}

To Whom It May Concern:

I am writing to document and challenge an AI-assisted decision by {platform} that materially affected me.

SUMMARY OF EVENTS
{description}

INDEPENDENT RECORD
Velaru (Nisaba LLC) recorded and signed this event as classification: {classification}.
Reason recorded: {reason or "See Exhibit A."}
Verify: {VELARU_VERIFY}?entry_id={receipt_hash}

RELEVANT RIGHTS
{chr(10).join("- " + r for r in rights[:3])}

DEMANDS
1. Provide a complete written explanation of any automated system's role in this decision.
2. Conduct a human review of my case within 15 business days.
3. Preserve all records, model outputs, and logs related to my account and this decision.

Sincerely,
[YOUR NAME]
[YOUR CONTACT]
"""


def record_submission(
    platform: str,
    velaru_domain: str,
    harm_type: str,
    classification: str,
    receipt_hash: str,
    incident_date: str | None = None,
    product_id: str = "harm_receipt",
) -> int:
    plat = normalize_platform(platform)
    now = utc_now_iso()
    with get_db() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO submissions
            (platform, domain, harm_type, classification, receipt_hash, incident_date, product_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (plat, velaru_domain, harm_type, classification, receipt_hash, incident_date, product_id, now),
        )
        row = conn.execute(
            "SELECT count FROM patterns WHERE platform = ? AND domain = ?",
            (plat, velaru_domain),
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE patterns SET count = count + 1, last_updated = ? WHERE platform = ? AND domain = ?",
                (now, plat, velaru_domain),
            )
        else:
            conn.execute(
                "INSERT INTO patterns (platform, domain, count, last_updated) VALUES (?, ?, 1, ?)",
                (plat, velaru_domain, now),
            )
        count = conn.execute(
            "SELECT count FROM patterns WHERE platform = ? AND domain = ?",
            (plat, velaru_domain),
        ).fetchone()[0]
    return int(count)


def pattern_status(count: int) -> tuple[str, str]:
    if count >= 100:
        return "systemic", "Systemic pattern — enough reports to support regulatory attention."
    if count >= 25:
        return "class_action", "Pattern rising — leave an email if you want class / advocate alerts."
    return "building", f"{count} similar report(s) recorded for this platform and domain."


def hash_email(email: str) -> str:
    import bcrypt

    return bcrypt.hashpw(email.strip().lower().encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")


def email_already_registered(email: str, platform: str, domain: str) -> bool:
    import bcrypt

    needle = email.strip().lower().encode("utf-8")
    with get_db() as conn:
        rows = conn.execute(
            "SELECT email_hash FROM notifications WHERE platform = ? AND domain = ?",
            (normalize_platform(platform), domain),
        ).fetchall()
    for row in rows:
        try:
            if bcrypt.checkpw(needle, row["email_hash"].encode("utf-8")):
                return True
        except Exception:
            continue
    return False


def cache_receipt(receipt: dict) -> None:
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO receipt_cache (receipt_hash, payload_json, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(receipt_hash) DO UPDATE SET payload_json = excluded.payload_json
            """,
            (receipt["hash"], json.dumps(receipt), utc_now_iso()),
        )


def load_receipt(receipt_hash: str) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT payload_json FROM receipt_cache WHERE receipt_hash = ?",
            (receipt_hash,),
        ).fetchone()
    if not row:
        return None
    return json.loads(row["payload_json"])


def store_unlock(
    token: str,
    receipt_hash: str,
    product_id: str,
    status: str,
    stripe_session_id: str | None = None,
) -> None:
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO unlocks
            (unlock_token, receipt_hash, product_id, status, stripe_session_id, created_at, fulfilled_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                token,
                receipt_hash,
                product_id,
                status,
                stripe_session_id,
                utc_now_iso(),
                utc_now_iso() if status == "paid" else None,
            ),
        )


def get_unlock(token: str) -> sqlite3.Row | None:
    with get_db() as conn:
        return conn.execute("SELECT * FROM unlocks WHERE unlock_token = ?", (token,)).fetchone()


def mark_unlock_paid(token: str, stripe_session_id: str | None = None) -> None:
    with get_db() as conn:
        conn.execute(
            """
            UPDATE unlocks
            SET status = 'paid', fulfilled_at = ?, stripe_session_id = COALESCE(?, stripe_session_id)
            WHERE unlock_token = ?
            """,
            (utc_now_iso(), stripe_session_id, token),
        )


def extract_velaru_receipt(
    velaru_data: dict,
    platform: str,
    harm_type: str,
    incident_date: str | None,
) -> dict:
    user = velaru_data.get("user") or {}
    ai = velaru_data.get("ai") or {}
    classification = (
        user.get("classification")
        or ai.get("classification")
        or velaru_data.get("classification")
        or "DOCUMENTED"
    )
    reason = user.get("reason") or ai.get("reason") or ""
    receipt_hash = (
        velaru_data.get("user_entry_hash")
        or velaru_data.get("ai_entry_hash")
        or velaru_data.get("entry_hash")
        or ""
    )
    if not receipt_hash:
        raise ValueError("Velaru response missing entry hash")
    harm = HARM_TYPES.get(harm_type, HARM_TYPES["other"])
    velaru_domain = harm["velaru_domain"]
    verify_base = velaru_data.get("verify_url") or VELARU_VERIFY
    return {
        "entry_id": receipt_hash,
        "hash": receipt_hash,
        "signature": velaru_data.get("user_signature") or velaru_data.get("ai_signature"),
        "timestamp": velaru_data.get("user_timestamp") or velaru_data.get("ai_timestamp") or utc_now_iso(),
        "domain": velaru_domain,
        "classification": classification,
        "confidence": user.get("confidence") or ai.get("confidence"),
        "reason": reason if reason not in {"N/A", "N/A - user input blocked upstream"} else "",
        "platform": platform,
        "harm_type": harm_type,
        "harm_label": harm["label"],
        "incident_date": incident_date,
        "verify_url": f"{verify_base}?entry_id={receipt_hash}",
        "permalink": velaru_data.get("permalink"),
        "rfc3161_authority": velaru_data.get("rfc3161_authority"),
        "anchor_status": velaru_data.get("anchor_status"),
        "crisis_action": velaru_data.get("crisis_action") or user.get("crisis_action"),
        "product": PRODUCTS["harm_receipt"],
    }


def build_advocate_export(receipt: dict, letter: str, pattern: dict, email_joined: bool) -> dict:
    return {
        "spec": "mishara-advocate-export-v1",
        "firm": "Nisaba LLC",
        "brand": "Mishara",
        "generated_at": utc_now_iso(),
        "not_legal_advice": True,
        "receipt": {
            "hash": receipt.get("hash"),
            "verify_url": receipt.get("verify_url"),
            "platform": receipt.get("platform"),
            "domain": receipt.get("domain"),
            "classification": receipt.get("classification"),
            "timestamp": receipt.get("timestamp"),
            "harm_label": receipt.get("harm_label"),
        },
        "rights": receipt.get("rights") or [],
        "help_links": receipt.get("help_links") or [],
        "pattern": pattern,
        "pattern_alert_email_joined": email_joined,
        "demand_letter": letter,
        "instructions_for_advocate": [
            "Verify the receipt URL as a stranger (no login).",
            "Treat the demand letter as a client-editable draft.",
            "Use pattern counts only as anonymous corroboration, not identity.",
        ],
    }


def advocate_export_txt(export: dict) -> str:
    r = export["receipt"]
    lines = [
        "MISHARA ADVOCATE EXPORT",
        f"Generated: {export['generated_at']}",
        "Not legal advice.",
        "",
        f"Platform: {r.get('platform')}",
        f"Domain: {r.get('domain')}",
        f"Harm: {r.get('harm_label')}",
        f"Classification: {r.get('classification')}",
        f"Receipt hash: {r.get('hash')}",
        f"Verify: {r.get('verify_url')}",
        "",
        "RIGHTS",
        *[f"- {x}" for x in export.get("rights") or []],
        "",
        f"PATTERN: {export.get('pattern')}",
        f"Alert email joined: {export.get('pattern_alert_email_joined')}",
        "",
        "DEMAND LETTER",
        export.get("demand_letter") or "",
        "",
        "ADVOCATE NOTES",
        *[f"- {x}" for x in export.get("instructions_for_advocate") or []],
    ]
    return "\n".join(lines)


def create_stripe_checkout(product_id: str, receipt_hash: str, unlock_token: str) -> tuple[str | None, str | None]:
    product = PRODUCTS[product_id]
    if not STRIPE_SECRET_KEY:
        return None, "Stripe is not configured"
    body = {
        "mode": "payment",
        "success_url": public_url(f"/unlock/{unlock_token}?paid=1"),
        "cancel_url": public_url(f"/receipt/{receipt_hash}?checkout=cancel"),
        "line_items[0][price_data][currency]": "usd",
        "line_items[0][price_data][product_data][name]": f"Mishara — {product['name']}",
        "line_items[0][price_data][product_data][description]": product["blurb"],
        "line_items[0][price_data][unit_amount]": str(product["price_cents"]),
        "line_items[0][quantity]": "1",
        "metadata[product_id]": product_id,
        "metadata[receipt_hash]": receipt_hash,
        "metadata[unlock_token]": unlock_token,
        "client_reference_id": unlock_token,
    }
    encoded = urllib.parse.urlencode(body).encode("utf-8")
    req = urllib.request.Request(
        "https://api.stripe.com/v1/checkout/sessions",
        data=encoded,
        headers={
            "Authorization": f"Bearer {STRIPE_SECRET_KEY}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("url"), data.get("id")
    except Exception as e:
        return None, str(e)


def fulfill_paid_pack(row: sqlite3.Row, description: str, email: str = "") -> dict[str, Any]:
    receipt = load_receipt(row["receipt_hash"])
    if not receipt:
        raise ValueError("Receipt missing")
    if not description:
        description = (
            f"AI-related harm involving {receipt.get('platform')} "
            f"({receipt.get('harm_label')}). Classification: {receipt.get('classification')}."
        )
    letter = generate_demand_letter(
        receipt.get("platform") or "The Company",
        description,
        receipt.get("classification") or "DOCUMENTED",
        receipt.get("domain") or "companion",
        receipt.get("hash") or row["receipt_hash"],
        receipt.get("reason") or "",
    )
    out: dict[str, Any] = {
        "ok": True,
        "product": PRODUCTS[row["product_id"]],
        "letter": letter,
        "receipt": receipt,
    }
    if row["product_id"] != "advocate_bundle":
        return out

    email_joined = False
    if email and "@" in email:
        if not email_already_registered(email, receipt.get("platform") or "", receipt.get("domain") or ""):
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO notifications (email_hash, platform, domain, created_at) VALUES (?, ?, ?, ?)",
                    (
                        hash_email(email),
                        normalize_platform(receipt.get("platform") or ""),
                        receipt.get("domain") or "",
                        utc_now_iso(),
                    ),
                )
        email_joined = True
    pattern = {"count": 0, "level": "building", "message": ""}
    with get_db() as conn:
        prow = conn.execute(
            "SELECT count FROM patterns WHERE platform = ? AND domain = ?",
            (normalize_platform(receipt.get("platform") or ""), receipt.get("domain") or ""),
        ).fetchone()
    if prow:
        pattern["count"] = int(prow["count"])
        pattern["level"], pattern["message"] = pattern_status(pattern["count"])
    export = build_advocate_export(receipt, letter, pattern, email_joined)
    out["export"] = export
    out["export_txt"] = advocate_export_txt(export)
    return out


@app.route("/")
def index():
    return render_template(
        "mishara/index.html",
        harm_types=HARM_TYPES,
        products=PRODUCTS,
        velaru_verify=VELARU_VERIFY,
        velaru_base=VELARU_BASE,
        contact_email=CONTACT_EMAIL,
    )


@app.route("/about")
def about():
    return render_template(
        "mishara/about.html",
        products=PRODUCTS,
        velaru_verify=VELARU_VERIFY,
        velaru_base=VELARU_BASE,
        contact_email=CONTACT_EMAIL,
    )


@app.route("/products.json")
def products_json():
    return jsonify(
        {
            "spec": "mishara-products-v1",
            "firm": "Nisaba LLC",
            "brand": "Mishara",
            "products": list(PRODUCTS.values()),
            "contact": CONTACT_EMAIL,
            "their_production": False,
        }
    )


def _public_base() -> str:
    if PUBLIC_BASE:
        return PUBLIC_BASE
    return (request.url_root or "").rstrip("/")


@app.route("/.well-known/mishara.json")
def well_known_mishara():
    base = _public_base()
    return jsonify(
        {
            "name": "Mishara",
            "firm": "Nisaba LLC",
            "description": "Consumer door when an AI decision already hurt you. Powered by Velaru.",
            "not": ["Gate", "Erra", "operator weld desk"],
            "home": f"{base}/",
            "about": f"{base}/about",
            "products": f"{base}/products.json",
            "health": f"{base}/health",
            "llms": f"{base}/llms.txt",
            "engine": VELARU_BASE,
            "verify": VELARU_VERIFY,
            "contact": CONTACT_EMAIL,
            "pricing": [
                {"id": p["id"], "name": p["name"], "price_label": p["price_label"], "price_cents": p["price_cents"]}
                for p in PRODUCTS.values()
            ],
            "their_production": False,
        }
    )


@app.route("/llms.txt")
def llms_txt():
    base = _public_base()
    lines = [
        "# Mishara — Nisaba LLC",
        "",
        "> When an AI decision already hurt you. Velaru-signed receipts. Not Gate. Not an operator weld desk.",
        "",
        f"- Home: {base}/",
        f"- About: {base}/about",
        f"- Products: {base}/products.json",
        f"- Discovery: {base}/.well-known/mishara.json",
        f"- Health: {base}/health",
        f"- Verify engine: {VELARU_VERIFY}",
        f"- Contact: {CONTACT_EMAIL}",
        "",
        "## Public ladder (this brand only)",
    ]
    for p in PRODUCTS.values():
        lines.append(f"- {p['name']}: {p['price_label']} — {p['blurb']}")
    lines.extend(
        [
            "",
            "Not Free/Pro seats. Not Gate Bind Room / operator weld pricing.",
            f"Sibling brands: Velaru ({VELARU_BASE}) · Gate (clearance before irreversible write).",
            "",
        ]
    )
    return "\n".join(lines), 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/robots.txt")
def robots_txt():
    base = _public_base()
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /unlock/",
            "Disallow: /checkout",
            f"Sitemap: {base}/sitemap.xml",
            "",
        ]
    )
    return body, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/sitemap.xml")
def sitemap_xml():
    base = _public_base()
    paths = ["/", "/about", "/products.json", "/.well-known/mishara.json", "/llms.txt", "/health"]
    urls = "".join(
        f"<url><loc>{base}{p}</loc><changefreq>weekly</changefreq></url>" for p in paths
    )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f"{urls}</urlset>"
    )
    return xml, 200, {"Content-Type": "application/xml; charset=utf-8"}


@app.route("/receipt/<receipt_hash>")
def receipt_page(receipt_hash: str):
    cached = load_receipt(receipt_hash)
    return render_template(
        "mishara/receipt.html",
        receipt_hash=receipt_hash,
        receipt=cached,
        products=PRODUCTS,
        velaru_verify=VELARU_VERIFY,
        velaru_base=VELARU_BASE,
        contact_email=CONTACT_EMAIL,
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "mishara",
            "products": list(PRODUCTS.keys()),
            "velaru_reachable": velaru_health_ok(),
            "velaru_base": VELARU_BASE,
            "payments": PAYMENTS_MODE,
            "stripe_configured": bool(STRIPE_SECRET_KEY),
            "openai_configured": bool(os.environ.get("OPENAI_API_KEY")),
        }
    )


@app.route("/submit", methods=["POST"])
def submit():
    body = request.get_json(silent=True) or {}
    description = (body.get("description") or "").strip()
    platform = (body.get("platform") or "").strip()
    harm_type = (body.get("harm_type") or "other").strip()
    incident_date = (body.get("incident_date") or "").strip() or None
    contribute_pattern = bool(body.get("contribute_pattern", True))

    if len(description) < 20:
        return jsonify({"error": True, "message": "Please describe what happened in a few sentences."}), 400
    if not platform:
        return jsonify({"error": True, "message": "Please enter the company or platform name."}), 400
    if harm_type not in HARM_TYPES:
        harm_type = "other"

    harm = HARM_TYPES[harm_type]
    velaru_domain = harm["velaru_domain"]
    velaru_data, err = velaru_classify(description, velaru_domain)
    if err:
        return jsonify({"error": True, "message": f"Could not generate receipt: {err}"}), 502

    try:
        receipt = extract_velaru_receipt(velaru_data, platform, harm_type, incident_date)
    except ValueError as e:
        return jsonify({"error": True, "message": str(e)}), 502

    receipt["explanation"] = plain_english_explanation(
        receipt["classification"], velaru_domain, description, receipt.get("reason") or ""
    )
    receipt["rights"] = RIGHTS_BY_DOMAIN.get(velaru_domain, RIGHTS_BY_DOMAIN["companion"])
    receipt["help_links"] = HELP_RESOURCES.get(velaru_domain, HELP_RESOURCES["companion"])
    receipt["description_fingerprint"] = hashlib.sha256(description.encode("utf-8")).hexdigest()[:16]

    pattern_count = 0
    pattern_level = "building"
    pattern_message = ""
    if contribute_pattern:
        pattern_count = record_submission(
            platform,
            velaru_domain,
            harm_type,
            receipt["classification"],
            receipt["hash"],
            incident_date,
        )
        pattern_level, pattern_message = pattern_status(pattern_count)

    cache_receipt(receipt)
    return jsonify(
        {
            "ok": True,
            "product": PRODUCTS["harm_receipt"],
            "receipt": receipt,
            "pattern": {"count": pattern_count, "level": pattern_level, "message": pattern_message},
            "upsells": [PRODUCTS["demand_pack"], PRODUCTS["advocate_bundle"]],
            "receipt_page": url_for("receipt_page", receipt_hash=receipt["hash"]),
        }
    )


@app.route("/checkout", methods=["POST"])
def checkout():
    body = request.get_json(silent=True) or {}
    product_id = (body.get("product_id") or "").strip()
    receipt_hash = (body.get("receipt_hash") or "").strip()
    if product_id not in {"demand_pack", "advocate_bundle"}:
        return jsonify({"error": True, "message": "Choose Demand Pack or Advocate Bundle."}), 400
    if not receipt_hash:
        return jsonify({"error": True, "message": "receipt_hash required."}), 400
    receipt = load_receipt(receipt_hash)
    if not receipt:
        return jsonify({"error": True, "message": "Unknown receipt — generate a Harm Receipt first."}), 404

    token = mint_unlock_token(receipt_hash, product_id)

    if PAYMENTS_MODE == "dev" or (
        PAYMENTS_MODE == "stripe" and not STRIPE_SECRET_KEY and os.getenv("MISHARA_ALLOW_DEV_PAY") == "1"
    ):
        store_unlock(token, receipt_hash, product_id, "paid")
        return jsonify(
            {
                "ok": True,
                "mode": "dev",
                "unlock_token": token,
                "unlock_url": url_for("unlock_page", token=token),
                "product": PRODUCTS[product_id],
            }
        )

    if PAYMENTS_MODE != "stripe" or not STRIPE_SECRET_KEY:
        store_unlock(token, receipt_hash, product_id, "invoice_pending")
        return jsonify(
            {
                "ok": True,
                "mode": "invoice",
                "unlock_token": token,
                "product": PRODUCTS[product_id],
                "ask": (
                    f"Email {CONTACT_EMAIL} with subject DEPOSIT {product_id} "
                    f"and receipt {receipt_hash[:12]}."
                ),
                "contact": CONTACT_EMAIL,
            }
        )

    url, session_id = create_stripe_checkout(product_id, receipt_hash, token)
    if not url:
        return jsonify({"error": True, "message": f"Checkout failed: {session_id}"}), 502
    store_unlock(token, receipt_hash, product_id, "checkout_open", stripe_session_id=session_id)
    return jsonify(
        {
            "ok": True,
            "mode": "stripe",
            "checkout_url": url,
            "unlock_token": token,
            "product": PRODUCTS[product_id],
        }
    )


@app.route("/unlock/<token>", methods=["GET", "POST"])
def unlock_page(token: str):
    row = get_unlock(token)
    if not row:
        return (
            render_template("mishara/unlock.html", error="Unknown unlock token.", contact_email=CONTACT_EMAIL),
            404,
        )

    if request.args.get("paid") == "1" and row["status"] != "paid":
        mark_unlock_paid(token)
        row = get_unlock(token)

    receipt = load_receipt(row["receipt_hash"])
    product = PRODUCTS.get(row["product_id"], PRODUCTS["demand_pack"])
    paid = row["status"] == "paid"
    letter = None
    export = None
    export_txt = None

    if paid and receipt and request.method == "POST":
        body = request.get_json(silent=True) or request.form.to_dict() or {}
        try:
            fulfilled = fulfill_paid_pack(
                row,
                (body.get("description") or "").strip(),
                (body.get("email") or "").strip(),
            )
        except ValueError as e:
            return jsonify({"error": True, "message": str(e)}), 404
        letter = fulfilled.get("letter")
        export = fulfilled.get("export")
        export_txt = fulfilled.get("export_txt")
        if request.is_json or "application/json" in (request.headers.get("Accept") or ""):
            return jsonify(fulfilled)

    return render_template(
        "mishara/unlock.html",
        error=None,
        paid=paid,
        product=product,
        receipt=receipt,
        unlock_token=token,
        status=row["status"],
        letter=letter,
        export=export,
        export_txt=export_txt,
        velaru_verify=VELARU_VERIFY,
        contact_email=CONTACT_EMAIL,
    )


@app.route("/demand-letter", methods=["POST"])
def demand_letter():
    body = request.get_json(silent=True) or {}
    token = (body.get("unlock_token") or "").strip()
    row = get_unlock(token) if token else None
    if not row or row["status"] != "paid":
        return jsonify({"error": True, "message": "Paid unlock_token required for Demand Pack."}), 402
    try:
        return jsonify(
            fulfill_paid_pack(
                row,
                (body.get("description") or "").strip(),
                (body.get("email") or "").strip(),
            )
        )
    except ValueError as e:
        return jsonify({"error": True, "message": str(e)}), 404


@app.route("/pattern")
def pattern():
    platform = normalize_platform(request.args.get("platform", ""))
    domain = (request.args.get("domain") or "").strip()
    if not platform or not domain:
        return jsonify({"error": True, "message": "platform and domain required"}), 400
    with get_db() as conn:
        row = conn.execute(
            "SELECT count, last_updated FROM patterns WHERE platform = ? AND domain = ?",
            (platform, domain),
        ).fetchone()
    count = int(row["count"]) if row else 0
    level, message = pattern_status(count)
    return jsonify(
        {
            "platform": platform,
            "domain": domain,
            "count": count,
            "level": level,
            "message": message,
            "last_updated": row["last_updated"] if row else None,
        }
    )


@app.route("/join-pattern", methods=["POST"])
def join_pattern():
    body = request.get_json(silent=True) or {}
    email = (body.get("email") or "").strip()
    platform = (body.get("platform") or "").strip()
    domain = (body.get("domain") or "").strip()
    token = (body.get("unlock_token") or "").strip()
    row = get_unlock(token) if token else None
    if not row or row["status"] != "paid" or row["product_id"] != "advocate_bundle":
        return jsonify({"error": True, "message": "Advocate Bundle unlock required to join pattern alerts."}), 402
    if not email or "@" not in email:
        return jsonify({"error": True, "message": "Valid email required."}), 400
    if not platform or not domain:
        return jsonify({"error": True, "message": "platform and domain required."}), 400
    if email_already_registered(email, platform, domain):
        return jsonify({"ok": True, "message": "Already on the alert list for this pattern."})
    with get_db() as conn:
        conn.execute(
            "INSERT INTO notifications (email_hash, platform, domain, created_at) VALUES (?, ?, ?, ?)",
            (hash_email(email), normalize_platform(platform), domain, utc_now_iso()),
        )
    return jsonify({"ok": True, "message": "Joined. We will notify you if advocate or regulatory action moves."})


init_db()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG") == "true")
