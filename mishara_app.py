"""
Mishara — consumer AI rights enforcement app.
Powered by Velaru audit infrastructure (velaru.onrender.com).
"""
import hashlib
import json
import os
import sqlite3
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("MISHARA_SECRET_KEY", os.urandom(24).hex())

VELARU_BASE = os.getenv("VELARU_API_URL", "https://velaru.onrender.com").rstrip("/")
VELARU_VERIFY = f"{VELARU_BASE}/verify"
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DB_PATH = os.getenv("MISHARA_DB_PATH", os.path.join(os.path.dirname(__file__), "mishara.db"))

HARM_TYPES = {
    "hiring": {
        "label": "Hiring & Employment",
        "emoji": "🏢",
        "hint": "Job application rejected, interview denied, wrongful termination",
        "velaru_domain": "hiring",
    },
    "housing": {
        "label": "Housing & Tenant Screening",
        "emoji": "🏠",
        "hint": "Rental application denied, credit screening",
        "velaru_domain": "tenant_screening",
    },
    "financial": {
        "label": "Financial & Credit",
        "emoji": "💰",
        "hint": "Loan denied, insurance claim rejected, credit score harm",
        "velaru_domain": "insurance",
    },
    "social_media": {
        "label": "Social Media & Platforms",
        "emoji": "📱",
        "hint": "Shadowban, demonetization, account suspended, content removed",
        "velaru_domain": "content_moderation",
    },
    "gig_work": {
        "label": "Gig Work",
        "emoji": "🚗",
        "hint": "Account deactivated, unfair rating, pay suppression",
        "velaru_domain": "gig_worker",
    },
    "healthcare": {
        "label": "Healthcare",
        "emoji": "🏥",
        "hint": "Treatment denied, AI diagnosis concern, insurance claim",
        "velaru_domain": "healthcare",
    },
    "government": {
        "label": "Government & Benefits",
        "emoji": "⚖️",
        "hint": "Benefits denied, immigration, public services",
        "velaru_domain": "government_benefits",
    },
    "pricing": {
        "label": "Pricing & Consumer",
        "emoji": "💲",
        "hint": "Price gouging, discriminatory pricing",
        "velaru_domain": "price_discrimination",
    },
    "privacy": {
        "label": "Privacy & Data",
        "emoji": "🔒",
        "hint": "Unauthorized data use, profiling concern",
        "velaru_domain": "data_poisoning",
    },
    "education": {
        "label": "Education",
        "emoji": "📚",
        "hint": "Admissions denial, academic AI decision",
        "velaru_domain": "education",
    },
    "other": {
        "label": "Other",
        "emoji": "✳️",
        "hint": "Describe your situation in your own words",
        "velaru_domain": "companion",
    },
}

RIGHTS_BY_DOMAIN = {
    "hiring": [
        "Under EEOC Title VII you have the right to request the reason for any AI-assisted hiring decision.",
        "Many states require employers to disclose when AI is used in hiring and allow you to opt out.",
        "You can file a charge with the EEOC at eeoc.gov within 180–300 days of the decision.",
    ],
    "tenant_screening": [
        "Under the Fair Housing Act, tenant screening cannot discriminate based on race, religion, sex, disability, or family status.",
        "You have the right to request a copy of your tenant screening report and dispute inaccurate information.",
        "HUD accepts fair housing complaints at hud.gov/fairhousing.",
    ],
    "insurance": [
        "Under the Fair Credit Reporting Act you can request adverse action notices explaining why credit or insurance was denied.",
        "Insurers using AI must often explain the principal reason for denial — request it in writing.",
        "Your state insurance commissioner may investigate unfair algorithmic denials.",
    ],
    "content_moderation": [
        "Platform terms must be applied consistently — document every moderation action with dates and screenshots.",
        "The Digital Services Act (EU) and emerging US state laws require appeal paths for automated moderation.",
        "EFF and digital rights groups at eff.org can help you understand platform accountability options.",
    ],
    "gig_worker": [
        "Gig platforms often must provide notice before deactivation — check your state's worker protection laws.",
        "The NLRB protects workers organizing for fair treatment regardless of contractor status.",
        "Document your ratings, pay history, and deactivation notice — they are evidence.",
    ],
    "healthcare": [
        "HIPAA gives you the right to access your medical records and know how automated decisions affect care.",
        "Insurance denials must include a reason and an appeal process — request both in writing.",
        "Patient advocacy organizations can help you challenge AI-assisted coverage decisions.",
    ],
    "government_benefits": [
        "You have the right to a written explanation when benefits are denied and to appeal within stated deadlines.",
        "Legal aid societies provide free help for benefits and immigration AI decisions.",
        "Document every automated denial notice — missing deadlines is the most common harm.",
    ],
    "price_discrimination": [
        "Algorithmic pricing that discriminates by protected class may violate state consumer protection laws.",
        "The FTC investigates unfair or deceptive pricing algorithms.",
        "Save screenshots showing different prices offered to you vs. others for the same product.",
    ],
    "data_poisoning": [
        "Under GDPR (EU) and state privacy laws (CCPA/CPRA), you may request what data was used and opt out of profiling.",
        "Companies must disclose automated decision-making that significantly affects you.",
        "Your state attorney general accepts privacy complaints.",
    ],
    "education": [
        "Admissions decisions using AI may be challengeable under Title VI and state education equity laws.",
        "You can request your admissions file and any AI-generated scores or flags.",
        "Document the timeline from application to denial for appeal deadlines.",
    ],
    "companion": [
        "You have the right to know when an automated system made a decision that affected you.",
        "Request a human review and written explanation from the company involved.",
        "Keep this cryptographic receipt — it proves what was recorded and when.",
    ],
}

HELP_RESOURCES = {
    "hiring": [
        {"name": "EEOC — Equal Employment Opportunity Commission", "url": "https://www.eeoc.gov", "note": "File employment discrimination charges"},
        {"name": "Workplace Fairness", "url": "https://www.workplacefairness.org", "note": "Worker rights resources and attorney referrals"},
    ],
    "tenant_screening": [
        {"name": "HUD Fair Housing", "url": "https://www.hud.gov/fairhousing", "note": "Report housing discrimination"},
        {"name": "National Fair Housing Alliance", "url": "https://nationalfairhousing.org", "note": "Fair housing advocacy"},
    ],
    "insurance": [
        {"name": "Consumer Financial Protection Bureau", "url": "https://www.consumerfinance.gov/complaint", "note": "Credit and lending complaints"},
        {"name": "NAIC — State Insurance Regulators", "url": "https://content.naic.org/consumer", "note": "Find your state insurance commissioner"},
    ],
    "content_moderation": [
        {"name": "Electronic Frontier Foundation", "url": "https://www.eff.org", "note": "Digital rights and platform accountability"},
        {"name": "Accountable Tech", "url": "https://accountabletech.org", "note": "Platform reform advocacy"},
    ],
    "gig_worker": [
        {"name": "National Labor Relations Board", "url": "https://www.nlrb.gov", "note": "Worker organizing and unfair labor practices"},
        {"name": "Gig Workers Rising", "url": "https://gigworkersrising.org", "note": "Gig worker advocacy"},
    ],
    "healthcare": [
        {"name": "Patient Advocate Foundation", "url": "https://www.patientadvocate.org", "note": "Insurance appeals and patient rights"},
        {"name": "Centers for Medicare & Medicaid", "url": "https://www.cms.gov", "note": "Medicare/Medicaid appeals"},
    ],
    "government_benefits": [
        {"name": "Legal Services Corporation", "url": "https://www.lsc.gov/find-legal-aid", "note": "Find free legal aid near you"},
        {"name": "USA.gov Benefits Appeals", "url": "https://www.usa.gov/benefits", "note": "Federal benefits guidance"},
    ],
    "price_discrimination": [
        {"name": "FTC Consumer Complaints", "url": "https://reportfraud.ftc.gov", "note": "Report unfair pricing practices"},
        {"name": "State Attorney General", "url": "https://www.naag.org/find-my-ag", "note": "Consumer protection in your state"},
    ],
    "data_poisoning": [
        {"name": "EFF Privacy Resources", "url": "https://www.eff.org/issues/privacy", "note": "Data privacy rights"},
        {"name": "EPIC — Electronic Privacy", "url": "https://epic.org", "note": "Privacy advocacy and policy"},
    ],
    "education": [
        {"name": "U.S. Department of Education OCR", "url": "https://www2.ed.gov/about/offices/list/ocr", "note": "Discrimination in education programs"},
        {"name": "ACLU Students' Rights", "url": "https://www.aclu.org/know-your-rights/students-rights", "note": "Education equity resources"},
    ],
    "companion": [
        {"name": "EFF", "url": "https://www.eff.org", "note": "Digital rights guidance"},
        {"name": "Legal Services Corporation", "url": "https://www.lsc.gov/find-legal-aid", "note": "Free legal aid directory"},
    ],
}


def utc_now_iso():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH) or ".", exist_ok=True)
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
            """
        )


def normalize_platform(name):
    return (name or "unknown").strip().lower()[:120]


def velaru_classify(description, velaru_domain, session_id=None):
    payload = {
        "message": description,
        "domain": velaru_domain,
        "modality": "text",
        "communication_form": "form_submission",
        "language": "auto",
        "session_id": session_id or f"mishara-{uuid.uuid4().hex[:16]}",
    }
    req = urllib.request.Request(
        f"{VELARU_BASE}/classify",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "Mishara/1.0"},
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


def velaru_health_ok():
    try:
        with urllib.request.urlopen(f"{VELARU_BASE}/health", timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("status") in ("ok", "degraded")
    except Exception:
        return False


def fallback_explanation(classification, velaru_domain, reason=""):
    harm = next((v for v in HARM_TYPES.values() if v["velaru_domain"] == velaru_domain), HARM_TYPES["other"])
    cls = classification or "UNKNOWN"
    if cls == "VIOLATION":
        meaning = (
            f"Velaru's independent audit classified your experience as a potential policy or rights violation "
            f"in the {harm['label']} category. {reason}".strip()
        )
    elif cls == "CRISIS":
        meaning = (
            "Your experience was classified as high-severity — indicating serious harm that may warrant "
            "immediate legal or advocacy support."
        )
    else:
        meaning = (
            f"Your experience was documented and signed. Even when classified as lower severity, "
            f"you still have a verified record — essential if the situation escalates or patterns emerge."
        )
    return (
        f"{meaning} "
        "Here is what you should know: you now have cryptographic proof that this event was recorded at a specific time. "
        "Next step: download your receipt and send a written request to the platform for a human review."
    )


def claude_text(system_prompt, user_prompt, max_tokens=800):
    if not ANTHROPIC_API_KEY:
        return None
    try:
        import anthropic

        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        parts = [b.text for b in msg.content if hasattr(b, "text")]
        return "\n".join(parts).strip() if parts else None
    except Exception:
        return None


def plain_english_explanation(classification, velaru_domain, description, reason=""):
    system = (
        "You are Mishara's plain-English AI rights advisor. Given a classification result and domain, "
        "explain in 2-3 sentences what this means for a non-lawyer. Be warm, clear, and empowering. "
        "Never say 'I cannot provide legal advice' — instead say 'Here is what you should know.' "
        "Always end with one concrete next step they can take today."
    )
    user = (
        f"Domain: {velaru_domain}\nClassification: {classification}\nReason: {reason}\n"
        f"User description (summary only): {description[:500]}"
    )
    result = claude_text(system, user, max_tokens=350)
    return result or fallback_explanation(classification, velaru_domain, reason)


def generate_demand_letter(platform, description, classification, velaru_domain, receipt_hash, reason=""):
    system = (
        "You are a professional consumer rights advocate drafting a formal demand letter. "
        "Write in clear, firm, professional English. Include: date placeholder [DATE], "
        "recipient as the platform name, factual summary, relevant regulations for the domain, "
        "reference to Exhibit A (Velaru cryptographic receipt hash), and specific demands "
        "(written explanation, human review, preservation of records). "
        "Do not include markdown headers — plain letter format only."
    )
    user = (
        f"Platform: {platform}\nDomain: {velaru_domain}\nClassification: {classification}\n"
        f"Velaru receipt hash (Exhibit A): {receipt_hash}\nReason: {reason}\n\n"
        f"Consumer's account:\n{description}"
    )
    result = claude_text(system, user, max_tokens=1200)
    if result:
        return result
    rights = RIGHTS_BY_DOMAIN.get(velaru_domain, RIGHTS_BY_DOMAIN["companion"])
    return f"""[DATE]

{platform}
Attention: Customer Trust & Legal Department

RE: Formal Demand — AI-Assisted Decision Affecting My Rights
Exhibit A: Velaru Cryptographic Receipt {receipt_hash[:16]}...

To Whom It May Concern:

I am writing to formally document and challenge an AI-assisted decision made by {platform} that materially affected me.

SUMMARY OF EVENTS
{description}

INDEPENDENT AUDIT CLASSIFICATION
An independent audit infrastructure (Velaru, Nisaba LLC) classified this experience as: {classification}.
Reason recorded: {reason or 'See Exhibit A.'}

RELEVANT RIGHTS
{chr(10).join('- ' + r for r in rights[:2])}

DEMANDS
1. Provide a complete written explanation of the AI system's role in the decision affecting me.
2. Conduct a human review of my case within 15 business days.
3. Preserve all records, model outputs, and audit logs related to my account and this decision.

Exhibit A (cryptographic receipt) is independently verifiable at {VELARU_VERIFY}.

Sincerely,
[YOUR NAME]
[YOUR CONTACT INFORMATION]
"""


def record_submission(platform, velaru_domain, harm_type, classification, receipt_hash, incident_date=None):
    plat = normalize_platform(platform)
    now = utc_now_iso()
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO submissions (platform, domain, harm_type, classification, receipt_hash, incident_date, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (plat, velaru_domain, harm_type, classification, receipt_hash, incident_date, now),
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
    return count


def pattern_status(count):
    if count >= 100:
        return "systemic", "Systemic harm detected — Mishara is preparing a regulatory complaint."
    if count >= 25:
        return "class_action", "Pattern detected — this may qualify for class action. Leave your email to be notified."
    return "building", f"{count} people have reported similar experiences with this platform."


def hash_email(email):
    import bcrypt

    normalized = email.strip().lower().encode("utf-8")
    return bcrypt.hashpw(normalized, bcrypt.gensalt(rounds=12)).decode("utf-8")


def email_already_registered(email_hash, platform, domain):
    with get_db() as conn:
        rows = conn.execute(
            "SELECT email_hash FROM notifications WHERE platform = ? AND domain = ?",
            (normalize_platform(platform), domain),
        ).fetchall()
    for row in rows:
        import bcrypt

        if bcrypt.checkpw(email.strip().lower().encode("utf-8"), row["email_hash"].encode("utf-8")):
            return True
    return False


@app.route("/")
def index():
    return render_template(
        "mishara/index.html",
        harm_types=HARM_TYPES,
        velaru_verify=VELARU_VERIFY,
        velaru_base=VELARU_BASE,
    )


@app.route("/about")
def about():
    return render_template(
        "mishara/about.html",
        velaru_verify=VELARU_VERIFY,
        velaru_base=VELARU_BASE,
    )


@app.route("/receipt/<receipt_hash>")
def receipt_page(receipt_hash):
    return render_template(
        "mishara/receipt.html",
        receipt_hash=receipt_hash,
        velaru_verify=VELARU_VERIFY,
        velaru_base=VELARU_BASE,
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "ok",
            "service": "mishara",
            "velaru_reachable": velaru_health_ok(),
            "velaru_base": VELARU_BASE,
            "claude_configured": bool(ANTHROPIC_API_KEY),
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
        return jsonify({"error": True, "message": "Please describe what happened in at least a few sentences."}), 400
    if not platform:
        return jsonify({"error": True, "message": "Please enter the company or platform name."}), 400

    harm = HARM_TYPES.get(harm_type, HARM_TYPES["other"])
    velaru_domain = harm["velaru_domain"]

    velaru_data, err = velaru_classify(description, velaru_domain)
    if err:
        return jsonify({"error": True, "message": f"Could not generate receipt: {err}"}), 502

    user = velaru_data.get("user") or {}
    classification = user.get("classification", "UNKNOWN")
    reason = user.get("reason", "")
    receipt_hash = velaru_data.get("user_entry_hash", "")
    timestamp = velaru_data.get("user_timestamp", utc_now_iso())

    explanation = plain_english_explanation(classification, velaru_domain, description, reason)
    rights = RIGHTS_BY_DOMAIN.get(velaru_domain, RIGHTS_BY_DOMAIN["companion"])
    help_links = HELP_RESOURCES.get(velaru_domain, HELP_RESOURCES["companion"])

    pattern_count = 0
    pattern_level = "building"
    pattern_message = ""
    if contribute_pattern:
        pattern_count = record_submission(platform, velaru_domain, harm_type, classification, receipt_hash, incident_date)
        pattern_level, pattern_message = pattern_status(pattern_count)

    receipt = {
        "entry_id": receipt_hash,
        "hash": receipt_hash,
        "signature": velaru_data.get("user_signature"),
        "timestamp": timestamp,
        "domain": velaru_domain,
        "classification": classification,
        "confidence": user.get("confidence_display") or user.get("confidence"),
        "reason": reason,
        "platform": platform,
        "harm_type": harm_type,
        "harm_label": harm["label"],
        "incident_date": incident_date,
        "explanation": explanation,
        "rights": rights,
        "help_links": help_links,
        "verify_url": f"{VELARU_VERIFY}?entry_id={receipt_hash}",
        "rfc3161_authority": velaru_data.get("rfc3161_authority"),
        "anchor_status": velaru_data.get("anchor_status"),
    }

    return jsonify(
        {
            "ok": True,
            "receipt": receipt,
            "pattern": {
                "count": pattern_count,
                "level": pattern_level,
                "message": pattern_message,
            },
        }
    )


@app.route("/demand-letter", methods=["POST"])
def demand_letter():
    body = request.get_json(silent=True) or {}
    description = (body.get("description") or "").strip()
    platform = (body.get("platform") or "The Company").strip()
    classification = (body.get("classification") or "DOCUMENTED").strip()
    velaru_domain = (body.get("domain") or "companion").strip()
    receipt_hash = (body.get("receipt_hash") or "").strip()
    reason = (body.get("reason") or "").strip()

    if not description or not receipt_hash:
        return jsonify({"error": True, "message": "Description and receipt hash required."}), 400

    letter = generate_demand_letter(platform, description, classification, velaru_domain, receipt_hash, reason)
    return jsonify({"ok": True, "letter": letter})


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
    count = row["count"] if row else 0
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

    if not email or "@" not in email:
        return jsonify({"error": True, "message": "Valid email required."}), 400
    if not platform or not domain:
        return jsonify({"error": True, "message": "platform and domain required."}), 400

    if email_already_registered(email, platform, domain):
        return jsonify({"ok": True, "message": "You're already on the list for updates about this pattern."})

    email_h = hash_email(email)
    with get_db() as conn:
        conn.execute(
            "INSERT INTO notifications (email_hash, platform, domain, created_at) VALUES (?, ?, ?, ?)",
            (email_h, normalize_platform(platform), domain, utc_now_iso()),
        )
    return jsonify({"ok": True, "message": "Thank you. We'll notify you if a class action or regulatory action moves forward."})


init_db()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG") == "true")
