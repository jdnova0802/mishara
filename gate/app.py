"""
Gate API — external commercial layer for Velaru fuse engine.
Metered proxy: identity, billing, docs, 402 on limit.
"""
import hashlib
import json
import os
import re
import secrets
import uuid
from functools import wraps

import bcrypt
import requests
import stripe
from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import demo_limit
except ImportError:
    import demo_limit

try:
    from gate import audiences
except ImportError:
    import audiences

try:
    from gate import notify
except ImportError:
    import notify

load_dotenv()

VELARU_BASE = os.getenv("VELARU_API_URL", "https://velaru.onrender.com").rstrip("/")
GATE_PUBLIC_URL = os.getenv("GATE_PUBLIC_URL", "http://localhost:5001").rstrip("/")
GATE_DEV_MODE = os.getenv("GATE_DEV_MODE", "0") == "1"
OPS_TOKEN = os.getenv("GATE_OPS_TOKEN", "")

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("GATE_SECRET_KEY", os.urandom(32).hex())
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
if not GATE_DEV_MODE and GATE_PUBLIC_URL.startswith("https"):
    app.config["SESSION_COOKIE_SECURE"] = True

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
STRIPE_INSTALL_PRICE_ID = os.getenv("STRIPE_INSTALL_PRICE_ID", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

PRO_PRICE_LABEL = os.getenv("GATE_PRO_PRICE_LABEL", "$99/mo")
INSTALL_PRICE_LABEL = os.getenv("GATE_INSTALL_PRICE_LABEL", "$2,500")
INSTALL_PRICE_CENTS = int(os.getenv("GATE_INSTALL_PRICE_CENTS", "250000"))
CONTACT_EMAIL = os.getenv("GATE_CONTACT_EMAIL", "hello@velaru.xyz")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def init():
    db.init_db()


@app.before_request
def _ensure_db():
    if not getattr(app, "_db_ready", False):
        init()
        app._db_ready = True


@app.context_processor
def inject_globals():
    return {
        "gate_public_url": GATE_PUBLIC_URL,
        "install_price": INSTALL_PRICE_LABEL,
        "install_slots": db.install_slots_remaining(),
        "contact_email": CONTACT_EMAIL,
    }


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("account_id"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped


def current_account():
    account_id = session.get("account_id")
    if not account_id:
        return None
    return db.get_account(account_id)


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode(), password_hash.encode())


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


def generate_api_key() -> tuple[str, str, str]:
    suffix = secrets.token_urlsafe(24)
    raw = f"gate_sk_live_{suffix}"
    prefix = raw[:20]
    return raw, prefix, hash_api_key(raw)


def extract_api_key():
    auth = request.headers.get("Authorization", "")
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return request.headers.get("X-Gate-Key", "").strip() or request.headers.get("X-API-Key", "").strip()


def authenticate_api_key():
    raw = extract_api_key()
    if not raw:
        return None
    row = db.get_api_key_by_hash(hash_api_key(raw))
    return row


def usage_payload(account_id: str, plan: str):
    usage = db.get_usage(account_id)
    limit = db.hop_limit(plan)
    return {
        "period": usage["period"],
        "hops": usage["hops"],
        "checks": usage["checks"],
        "hop_limit": limit,
        "remaining_hops": max(0, limit - usage["hops"]),
        "plan": plan,
    }


def payment_required_response(account_id: str, plan: str):
    usage = usage_payload(account_id, plan)
    return (
        jsonify(
            {
                "error": {
                    "type": "payment_required",
                    "code": "hop_limit_exceeded",
                    "message": "Monthly hop limit reached. Upgrade to Pro for 1M hops/mo.",
                    "request_id": f"req_{uuid.uuid4().hex[:16]}",
                    "usage": usage,
                    "upgrade_url": f"{GATE_PUBLIC_URL}/pricing",
                }
            }
        ),
        402,
        {"X-Gate-Usage-Hops": str(usage["hops"]), "X-Gate-Usage-Limit": str(usage["hop_limit"])},
    )


def velaru_request(method: str, path: str, **kwargs):
    url = f"{VELARU_BASE}{path}"
    headers = kwargs.pop("headers", {})
    headers.setdefault("Content-Type", "application/json")
    headers.setdefault("User-Agent", "GateAPI/1.0")
    timeout = kwargs.pop("timeout", 30)
    return requests.request(method, url, headers=headers, timeout=timeout, **kwargs)


def metered_api(view=None, *, count_usage=True):
    def decorator(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            row = authenticate_api_key()
            if not row:
                return (
                    jsonify(
                        {
                            "error": {
                                "type": "authentication_error",
                                "code": "invalid_api_key",
                                "message": "Missing or invalid Gate API key. Create one at /dashboard.",
                                "request_id": f"req_{uuid.uuid4().hex[:16]}",
                            }
                        }
                    ),
                    401,
                )

            g.api_account = row
            g.plan = row["plan"]
            g.account_id = row["account_id"]

            usage = db.get_usage(g.account_id)
            if usage["hops"] >= db.hop_limit(g.plan):
                return payment_required_response(g.account_id, g.plan)

            response = fn(*args, **kwargs)
            if isinstance(response, tuple):
                payload, status = response[0], response[1]
                extra_headers = response[2] if len(response) > 2 else {}
            else:
                payload, status, extra_headers = response, 200, {}

            if count_usage and 200 <= status < 300:
                updated = db.increment_usage(g.account_id, "hops")
                extra_headers = dict(extra_headers or {})
                extra_headers["X-Gate-Usage-Hops"] = str(updated["hops"])
                extra_headers["X-Gate-Usage-Limit"] = str(db.hop_limit(g.plan))
                extra_headers["X-Gate-Plan"] = g.plan
            elif 200 <= status < 300:
                extra_headers = dict(extra_headers or {})
                usage = usage_payload(g.account_id, g.plan)
                extra_headers["X-Gate-Usage-Hops"] = str(usage["hops"])
                extra_headers["X-Gate-Usage-Limit"] = str(usage["hop_limit"])
                extra_headers["X-Gate-Plan"] = g.plan

            if isinstance(payload, dict):
                return jsonify(payload), status, extra_headers
            return payload, status, extra_headers

        return wrapped

    if view is not None:
        return decorator(view)
    return decorator


# ── Web pages ────────────────────────────────────────────────────────────────


@app.route("/health")
def health():
    velaru_ok = False
    try:
        r = velaru_request("GET", "/health", timeout=10)
        velaru_ok = r.status_code == 200
    except requests.RequestException:
        pass
    return jsonify(
        {
            "status": "ok",
            "service": "gate-api",
            "velaru_reachable": velaru_ok,
            "velaru_base": VELARU_BASE,
            "public_url": GATE_PUBLIC_URL,
        }
    )


@app.route("/ops/orders")
def ops_orders():
    token = request.args.get("token") or request.headers.get("X-Ops-Token", "")
    if not OPS_TOKEN or token != OPS_TOKEN:
        return jsonify({"error": "unauthorized"}), 401
    rows = db.list_paid_installs()
    return jsonify(
        {
            "paid_installs": [dict(r) for r in rows],
            "slots_remaining": db.install_slots_remaining(),
            "hops_month": db.total_hops_period(),
            "accounts": db.count_accounts(),
        }
    )


@app.route("/")
def index():
    return render_template(
        "index.html",
        public_url=GATE_PUBLIC_URL,
        velaru_base=VELARU_BASE,
        pro_price=PRO_PRICE_LABEL,
        install_price=INSTALL_PRICE_LABEL,
        install_slots=db.install_slots_remaining(),
    )


@app.route("/status")
def status_page():
    velaru_ok = False
    velaru_data = {}
    try:
        r = velaru_request("GET", "/health", timeout=10)
        velaru_ok = r.status_code == 200
        velaru_data = r.json() if velaru_ok else {}
    except requests.RequestException:
        pass
    return render_template(
        "status.html",
        velaru_ok=velaru_ok,
        velaru_data=velaru_data,
        velaru_base=VELARU_BASE,
        accounts=db.count_accounts(),
        hops_month=db.total_hops_period(),
        installs_month=db.paid_installs_period(),
        install_slots=db.install_slots_remaining(),
        public_url=GATE_PUBLIC_URL,
    )


@app.route("/trust")
def trust():
    return render_template("trust.html", velaru_base=VELARU_BASE, public_url=GATE_PUBLIC_URL)


@app.route("/start")
def start_hub():
    plates = audiences.plate_list()
    return render_template("start.html", plates=plates, public_url=GATE_PUBLIC_URL)


@app.route("/for/<slug>")
def audience_plate(slug):
    plate = audiences.get_plate(slug)
    if not plate:
        abort(404)
    return render_template(
        "audience.html",
        slug=slug,
        plate=plate,
        public_url=GATE_PUBLIC_URL,
        contact_email=CONTACT_EMAIL,
    )


@app.route("/pitch/<slug>")
def audience_pitch(slug):
    if not audiences.get_plate(slug):
        abort(404)
    return redirect(url_for("audience_plate", slug=slug))


@app.route("/.well-known/opportunities.json")
def well_known_opportunities():
    return jsonify(audiences.opportunities_manifest(GATE_PUBLIC_URL, CONTACT_EMAIL))


@app.route("/demo/hop", methods=["POST"])
def demo_hop():
    ok, msg = demo_limit.allow_demo(request)
    if not ok:
        return jsonify({"error": {"code": "rate_limited", "message": msg}}), 429
    body = request.get_json(silent=True) or {}
    fuse_id = (body.get("fuse_id") or "fuse_velaru_drill").strip()
    if not demo_limit.validate_demo_fuse(fuse_id):
        return jsonify({"error": {"code": "demo_fuse_only", "message": "Demo limited to public fuses."}}), 400
    try:
        r = velaru_request("POST", "/api/v1/fuse/hop", json={"fuse_id": fuse_id})
        data = r.json()
        data["demo"] = True
        data["signup_url"] = f"{GATE_PUBLIC_URL}/signup"
        return jsonify(data), r.status_code
    except requests.RequestException as e:
        return jsonify({"error": {"code": "upstream_error", "message": str(e)}}), 502


@app.route("/demo/lookup")
def demo_lookup():
    ok, msg = demo_limit.allow_demo(request)
    if not ok:
        return jsonify({"error": {"code": "rate_limited", "message": msg}}), 429
    fuse_id = request.args.get("fuse_id", "fuse_velaru_drill").strip()
    if not demo_limit.validate_demo_fuse(fuse_id):
        return jsonify({"error": {"code": "demo_fuse_only", "message": "Demo limited to public fuses."}}), 400
    try:
        r = velaru_request("GET", "/api/v1/fuse/lookup", params={"fuse_id": fuse_id})
        data = r.json()
        data["demo"] = True
        return jsonify(data), r.status_code
    except requests.RequestException as e:
        return jsonify({"error": {"code": "upstream_error", "message": str(e)}}), 502


@app.route("/.well-known/gate.json")
def well_known_gate():
    return jsonify(
        {
            "name": "Gate API",
            "description": "Can this agent still act right now? Metered fuse hop.",
            "version": "1.0.0",
            "openapi": f"{GATE_PUBLIC_URL}/openapi.json",
            "signup": f"{GATE_PUBLIC_URL}/signup",
            "install": f"{GATE_PUBLIC_URL}/install",
            "verify_engine": "https://velaru.xyz/verify",
            "demo_hop": f"{GATE_PUBLIC_URL}/demo/hop",
            "sdk": {
                "python": "from gate.sdk import GateClient",
                "pip": "pip install -r requirements.txt  # sdk in-repo",
            },
            "patent": "64/124,027",
            "operator": "Nisaba LLC",
        }
    )


@app.route("/docs")
def docs():
    return render_template(
        "docs.html",
        public_url=GATE_PUBLIC_URL,
        velaru_base=VELARU_BASE,
    )


@app.route("/pricing")
def pricing():
    return render_template(
        "pricing.html",
        public_url=GATE_PUBLIC_URL,
        pro_price=PRO_PRICE_LABEL,
        install_price=INSTALL_PRICE_LABEL,
        install_slots=db.install_slots_remaining(),
        stripe_publishable=STRIPE_PUBLISHABLE_KEY,
    )


@app.route("/install")
def install():
    slots = db.install_slots_remaining()
    return render_template(
        "install.html",
        public_url=GATE_PUBLIC_URL,
        install_price=INSTALL_PRICE_LABEL,
        install_slots=slots,
        sold_out=slots <= 0,
        contact_email=CONTACT_EMAIL,
    )


@app.route("/install/checkout", methods=["POST"])
def install_checkout():
    slots = db.install_slots_remaining()
    if slots <= 0:
        flash("Install slots are full this month. Email us for the waitlist.", "error")
        return redirect(url_for("install"))

    email = (request.form.get("email") or "").strip()
    if not EMAIL_RE.match(email):
        flash("Enter a valid email for project contact.", "error")
        return redirect(url_for("install"))

    if GATE_DEV_MODE:
        fake_session = f"dev_{uuid.uuid4().hex}"
        db.create_install_order(email, fake_session, INSTALL_PRICE_CENTS)
        db.mark_install_paid(fake_session)
        notify.money(
            "Install booked (dev)",
            f"{email} paid {INSTALL_PRICE_LABEL}",
            {"email": email, "session": fake_session},
        )
        return redirect(url_for("install_success", session_id=fake_session))

    if not stripe.api_key or not STRIPE_INSTALL_PRICE_ID:
        flash(f"Checkout not configured yet. Email {CONTACT_EMAIL} with subject FUSE.", "error")
        return redirect(url_for("install"))

    checkout = stripe.checkout.Session.create(
        mode="payment",
        customer_email=email,
        line_items=[{"price": STRIPE_INSTALL_PRICE_ID, "quantity": 1}],
        success_url=f"{GATE_PUBLIC_URL}/install/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{GATE_PUBLIC_URL}/install?canceled=1",
        metadata={"product": "install_sprint", "contact_email": email},
    )
    db.create_install_order(email, checkout.id, INSTALL_PRICE_CENTS)
    return redirect(checkout.url, code=303)


@app.route("/install/success")
def install_success():
    session_id = request.args.get("session_id", "")
    order = db.get_install_order_by_session(session_id) if session_id else None
    return render_template(
        "install_success.html",
        order=order,
        contact_email=CONTACT_EMAIL,
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        account = db.get_account_by_email(email)
        if not account or not check_password(password, account["password_hash"]):
            flash("Invalid email or password.", "error")
        else:
            session["account_id"] = account["id"]
            nxt = request.args.get("next") or url_for("dashboard")
            return redirect(nxt)
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        if not EMAIL_RE.match(email):
            flash("Enter a valid email.", "error")
        elif len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
        elif db.get_account_by_email(email):
            flash("Account already exists. Log in instead.", "error")
        else:
            account_id = db.create_account(email, hash_password(password))
            raw_key, prefix, key_hash = generate_api_key()
            db.create_api_key(account_id, key_hash, prefix, "default")
            session["account_id"] = account_id
            session["new_api_key"] = raw_key
            return redirect(url_for("dashboard"))
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    account = current_account()
    keys = db.list_api_keys(account["id"])
    usage = usage_payload(account["id"], account["plan"])
    new_key = session.pop("new_api_key", None)
    return render_template(
        "dashboard.html",
        account=account,
        keys=keys,
        usage=usage,
        new_key=new_key,
        stripe_publishable=STRIPE_PUBLISHABLE_KEY,
        pro_price=PRO_PRICE_LABEL,
        dev_mode=GATE_DEV_MODE,
    )


@app.route("/dashboard/keys", methods=["POST"])
@login_required
def create_key():
    account = current_account()
    label = (request.form.get("label") or "default").strip()[:64]
    raw_key, prefix, key_hash = generate_api_key()
    db.create_api_key(account["id"], key_hash, prefix, label)
    session["new_api_key"] = raw_key
    flash("New API key created. Copy it now — it won't be shown again.", "success")
    return redirect(url_for("dashboard"))


@app.route("/billing/checkout", methods=["POST"])
@login_required
def billing_checkout():
    if GATE_DEV_MODE:
        account = current_account()
        db.set_plan(account["id"], "pro")
        flash("Dev mode: upgraded to Pro.", "success")
        return redirect(url_for("dashboard"))

    if not stripe.api_key or not STRIPE_PRICE_ID:
        flash("Billing is not configured yet. Contact hello@velaru.xyz.", "error")
        return redirect(url_for("pricing"))

    account = current_account()
    customer_id = account["stripe_customer_id"]
    if not customer_id:
        customer = stripe.Customer.create(email=account["email"], metadata={"gate_account_id": account["id"]})
        customer_id = customer.id
        db.set_plan(account["id"], account["plan"], stripe_customer_id=customer_id)

    checkout = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": STRIPE_PRICE_ID, "quantity": 1}],
        success_url=f"{GATE_PUBLIC_URL}/dashboard?upgraded=1",
        cancel_url=f"{GATE_PUBLIC_URL}/pricing?canceled=1",
        metadata={"gate_account_id": account["id"]},
    )
    return redirect(checkout.url, code=303)


@app.route("/billing/webhook", methods=["POST"])
def billing_webhook():
    payload = request.data
    sig = request.headers.get("Stripe-Signature", "")
    if not STRIPE_WEBHOOK_SECRET:
        return jsonify({"error": "webhook not configured"}), 500
    try:
        event = stripe.Webhook.construct_event(payload, sig, STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return jsonify({"error": "invalid signature"}), 400

    if event["type"] == "checkout.session.completed":
        sess = event["data"]["object"]
        product = (sess.get("metadata") or {}).get("product")
        if product == "install_sprint":
            db.mark_install_paid(sess["id"])
            email = (sess.get("metadata") or {}).get("contact_email") or sess.get("customer_email")
            notify.money(
                "CASH — 48hr install",
                f"{INSTALL_PRICE_LABEL} from {email}",
                {"email": email, "session": sess["id"]},
            )
        else:
            account_id = (sess.get("metadata") or {}).get("gate_account_id")
            sub_id = sess.get("subscription")
            if account_id:
                db.set_plan(account_id, "pro", stripe_subscription_id=sub_id)
                acct = db.get_account(account_id)
                notify.money(
                    "CASH — Gate Pro",
                    f"{PRO_PRICE_LABEL} from {acct['email'] if acct else account_id}",
                    {"account_id": account_id, "subscription": sub_id},
                )
    elif event["type"] in ("customer.subscription.deleted", "customer.subscription.paused"):
        sub = event["data"]["object"]
        customer_id = sub.get("customer")
        with db.db() as conn:
            row = conn.execute(
                "SELECT id FROM accounts WHERE stripe_customer_id = ?", (customer_id,)
            ).fetchone()
        if row:
            db.set_plan(row["id"], "free", stripe_subscription_id=None)

    return jsonify({"received": True})


# ── Metered API (proxies Velaru) ─────────────────────────────────────────────


@app.route("/v1/fuse/lookup")
@metered_api
def fuse_lookup():
    fuse_id = request.args.get("fuse_id", "").strip()
    if not fuse_id:
        return {"error": {"code": "fuse_id_required", "message": "fuse_id query param required"}}, 400
    try:
        r = velaru_request("GET", "/api/v1/fuse/lookup", params={"fuse_id": fuse_id})
        return r.json(), r.status_code
    except requests.RequestException as e:
        return {"error": {"code": "upstream_error", "message": str(e)}}, 502


@app.route("/v1/fuse/hop", methods=["POST"])
@metered_api
def fuse_hop():
    body = request.get_json(silent=True) or {}
    try:
        r = velaru_request("POST", "/api/v1/fuse/hop", json=body)
        return r.json(), r.status_code
    except requests.RequestException as e:
        return {"error": {"code": "upstream_error", "message": str(e)}}, 502


@app.route("/v1/execute-gate", methods=["POST"])
@app.route("/v1/execute-gate/demo", methods=["POST"])
@metered_api
def execute_gate():
    path = "/api/v1/execute-gate/demo" if request.path.endswith("/demo") else "/api/v1/execute-gate"
    body = request.get_json(silent=True) or {}
    headers = {}
    for h in ("Idempotency-Key", "AGENT-DECISION-OBJECT"):
        if request.headers.get(h):
            headers[h] = request.headers[h]
    try:
        r = velaru_request("POST", path, json=body, headers=headers)
        return r.json(), r.status_code
    except requests.RequestException as e:
        return {"error": {"code": "upstream_error", "message": str(e)}}, 502


@app.route("/v1/classify", methods=["POST"])
@metered_api
def classify():
    body = request.get_json(silent=True) or {}
    headers = {}
    if request.headers.get("Idempotency-Key"):
        headers["Idempotency-Key"] = request.headers["Idempotency-Key"]
    try:
        r = velaru_request("POST", "/api/v1/classify", json=body, headers=headers)
        return r.json(), r.status_code
    except requests.RequestException as e:
        return {"error": {"code": "upstream_error", "message": str(e)}}, 502


@app.route("/v1/me")
@metered_api(count_usage=False)
def api_me():
    usage = usage_payload(g.account_id, g.plan)
    return {
        "ok": True,
        "email": g.api_account["email"],
        "plan": g.plan,
        "usage": usage,
        "api_base": GATE_PUBLIC_URL,
        "velaru_base": VELARU_BASE,
    }


@app.route("/robots.txt")
def robots():
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            f"Sitemap: {GATE_PUBLIC_URL}/sitemap.xml",
            "",
        ]
    )
    return body, 200, {"Content-Type": "text/plain"}


@app.route("/sitemap.xml")
def sitemap():
    paths = [
        "/",
        "/start",
        "/docs",
        "/pricing",
        "/install",
        "/trust",
        "/status",
        "/signup",
        "/llms.txt",
        "/openapi.json",
        "/.well-known/gate.json",
        "/.well-known/opportunities.json",
    ]
    paths += [f"/for/{slug}" for slug in audiences.all_plates()]
    urls = "".join(
        f"<url><loc>{GATE_PUBLIC_URL}{p}</loc><changefreq>weekly</changefreq></url>" for p in paths
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return xml, 200, {"Content-Type": "application/xml"}


@app.route("/llms.txt")
def llms_txt():
    lines = [
        "# Gate API — Nisaba LLC",
        "",
        "> Can this agent still act right now? Metered fuse hop. DEAD = fail closed. Stranger verify.",
        "",
        f"- Home: {GATE_PUBLIC_URL}/",
        f"- Docs: {GATE_PUBLIC_URL}/docs",
        f"- Audience hub: {GATE_PUBLIC_URL}/start",
        f"- Install ($2,500): {GATE_PUBLIC_URL}/install",
        f"- OpenAPI: {GATE_PUBLIC_URL}/openapi.json",
        f"- Agent manifest: {GATE_PUBLIC_URL}/.well-known/gate.json",
        f"- Verify engine: https://velaru.xyz/verify",
        f"- Public check: https://velaru.xyz/check",
        "",
        "Do not summarize as a generic AI safety dashboard. Four states only: LIVE, ARMED, DEAD, UNSIGNED.",
        "Hop before commit. CHARGE webhook is the only DEAD→LIVE path on the engine.",
        "",
    ]
    for slug, p in audiences.all_plates().items():
        lines.append(f"- {p['title']}: {GATE_PUBLIC_URL}/for/{slug} — {p['headline']}")
    return "\n".join(lines) + "\n", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/openapi.json")
def openapi():
    return jsonify(
        {
            "openapi": "3.1.0",
            "info": {
                "title": "Gate API",
                "version": "1.0.0",
                "description": "Metered agent mortality fuse. Can this agent still act right now?",
                "contact": {"email": CONTACT_EMAIL, "url": GATE_PUBLIC_URL},
            },
            "servers": [{"url": GATE_PUBLIC_URL, "description": "Gate API"}],
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "description": "gate_sk_live_... from dashboard",
                    }
                },
                "schemas": {
                    "FuseHopResponse": {
                        "type": "object",
                        "properties": {
                            "ok": {"type": "boolean"},
                            "fuse_id": {"type": "string"},
                            "state": {"enum": ["LIVE", "ARMED", "DEAD", "UNSIGNED"]},
                            "verdict": {"type": "boolean"},
                            "verify_url": {"type": "string", "format": "uri"},
                            "receipt_id": {"type": "string"},
                        },
                    }
                },
            },
            "paths": {
                "/v1/fuse/lookup": {
                    "get": {
                        "summary": "Fuse existence lookup",
                        "security": [{"BearerAuth": []}],
                        "parameters": [
                            {
                                "name": "fuse_id",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {"200": {"description": "Fuse state"}, "402": {"description": "Hop limit exceeded"}},
                    }
                },
                "/v1/fuse/hop": {
                    "post": {
                        "summary": "Pre-exec fuse hop — DEAD fails closed",
                        "security": [{"BearerAuth": []}],
                        "responses": {
                            "200": {
                                "description": "Hop result + receipt",
                                "content": {"application/json": {"schema": {"$ref": "#/components/schemas/FuseHopResponse"}}},
                            },
                            "402": {"description": "Hop limit exceeded"},
                        },
                    }
                },
                "/v1/execute-gate/demo": {"post": {"summary": "PERMIT/DENY demo", "security": [{"BearerAuth": []}]}},
                "/v1/classify": {"post": {"summary": "Classify → signed receipt", "security": [{"BearerAuth": []}]}},
                "/v1/me": {"get": {"summary": "Key metadata + usage", "security": [{"BearerAuth": []}]}},
                "/demo/hop": {"post": {"summary": "Public demo hop (no key, rate limited)", "security": []}},
                "/demo/lookup": {"get": {"summary": "Public demo lookup", "security": []}},
                "/health": {"get": {"summary": "Service health"}},
                "/.well-known/gate.json": {"get": {"summary": "Agent discovery manifest"}},
            },
        }
    )


if __name__ == "__main__":
    init()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=GATE_DEV_MODE)
