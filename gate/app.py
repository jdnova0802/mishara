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
    Response,
    abort,
    flash,
    g,
    jsonify,
    make_response,
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

try:
    from gate import public_url as public_url_mod
except ImportError:
    import public_url as public_url_mod

try:
    from gate import listings as listings_mod
except ImportError:
    import listings as listings_mod

try:
    from gate import mcp_server
except ImportError:
    import mcp_server

try:
    from gate import fields
except ImportError:
    import fields

try:
    from gate import weld
except ImportError:
    import weld

try:
    from gate import bind_room as bind_room_mod
except ImportError:
    import bind_room as bind_room_mod

try:
    from gate import operator_invoice as operator_mod
except ImportError:
    import operator_invoice as operator_mod

try:
    from gate import register as register_mod
except ImportError:
    import register as register_mod

try:
    from gate import positioning as positioning_mod
except ImportError:
    import positioning as positioning_mod

try:
    from gate import action_os as action_os_mod
except ImportError:
    import action_os as action_os_mod

try:
    from gate import scorecard as scorecard_mod
except ImportError:
    import scorecard as scorecard_mod

try:
    from gate import production_skin as production_skin_mod
except ImportError:
    import production_skin as production_skin_mod

try:
    from gate import proof_suite as proof_suite_mod
except ImportError:
    import proof_suite as proof_suite_mod

try:
    from gate import science_pri as science_pri_mod
except ImportError:
    import science_pri as science_pri_mod

try:
    from gate import legal as legal_mod
except ImportError:
    import legal as legal_mod

try:
    from gate import runbook as runbook_mod
except ImportError:
    import runbook as runbook_mod

try:
    from gate import live as live_mod
except ImportError:
    import live as live_mod

try:
    from gate import canary as canary_mod
except ImportError:
    import canary as canary_mod

try:
    from gate import family_voices as family_voices_mod
except ImportError:
    import family_voices as family_voices_mod

try:
    from gate import bound
except ImportError:
    import bound

try:
    from gate import exclusive
except ImportError:
    import exclusive

try:
    from gate import floor
except ImportError:
    import floor

try:
    from gate import particular
except ImportError:
    import particular

try:
    from gate import liturgy as liturgy_mod
except ImportError:
    import liturgy as liturgy_mod

try:
    from gate import inhabitant as inhabitant_mod
except ImportError:
    import inhabitant as inhabitant_mod

try:
    from gate import ticket as ticket_mod
except ImportError:
    import ticket as ticket_mod

try:
    from gate import spend_protocol as spend_protocol_mod
except ImportError:
    import spend_protocol as spend_protocol_mod

try:
    from gate import command_radiation as command_radiation_mod
except ImportError:
    import command_radiation as command_radiation_mod

try:
    from gate import epoch as epoch_mod
except ImportError:
    import epoch as epoch_mod

try:
    from gate import counterpart as counterpart_mod
except ImportError:
    import counterpart as counterpart_mod

try:
    from gate import license_fuse as license_fuse_mod
except ImportError:
    import license_fuse as license_fuse_mod

try:
    from gate import restraint as restraint_mod
except ImportError:
    import restraint as restraint_mod

try:
    from gate import exclusion as exclusion_mod
except ImportError:
    import exclusion as exclusion_mod

try:
    from gate import evidence_log as evidence_log_mod
except ImportError:
    import evidence_log as evidence_log_mod

load_dotenv()

VELARU_BASE = os.getenv("VELARU_API_URL", "https://velaru.onrender.com").rstrip("/")
GATE_PUBLIC_URL = public_url_mod.resolve_public_url()
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
STRIPE_BIND_ROOM_PRICE_ID = os.getenv("STRIPE_BIND_ROOM_PRICE_ID", "")
STRIPE_REFUSAL_PRICE_ID = os.getenv("STRIPE_REFUSAL_PRICE_ID", "")
STRIPE_WELD_PRICE_ID = os.getenv("STRIPE_WELD_PRICE_ID", "")
STRIPE_FLOOR_PRICE_ID = os.getenv("STRIPE_FLOOR_PRICE_ID", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

PRO_PRICE_LABEL = os.getenv("GATE_PRO_PRICE_LABEL", "$99/mo")
INSTALL_PRICE_LABEL = os.getenv("GATE_INSTALL_PRICE_LABEL", "$2,500")
INSTALL_PRICE_CENTS = int(os.getenv("GATE_INSTALL_PRICE_CENTS", "250000"))
BIND_ROOM_PRICE_LABEL = os.getenv("GATE_BIND_ROOM_PRICE_LABEL", "$1,750")
BIND_ROOM_PRICE_CENTS = int(os.getenv("GATE_BIND_ROOM_PRICE_CENTS", "175000"))
REFUSAL_PRICE_LABEL = os.getenv("GATE_REFUSAL_PRICE_LABEL", "$7,500")
REFUSAL_PRICE_CENTS = int(os.getenv("GATE_REFUSAL_PRICE_CENTS", "750000"))
WELD_PRICE_LABEL = os.getenv("GATE_WELD_PRICE_LABEL", operator_mod.WELD_PRICE_LABEL)
WELD_PRICE_CENTS = int(os.getenv("GATE_WELD_PRICE_CENTS", str(operator_mod.WELD_PRICE_CENTS)))
FLOOR_PRICE_LABEL = os.getenv("GATE_FLOOR_PRICE_LABEL", operator_mod.FLOOR_PRICE_LABEL)
FLOOR_PRICE_CENTS = int(os.getenv("GATE_FLOOR_PRICE_CENTS", str(operator_mod.FLOOR_PRICE_CENTS)))
CONTACT_EMAIL = os.getenv("GATE_CONTACT_EMAIL", "hello@velaru.xyz")
META_PIXEL_ID = (os.getenv("GATE_META_PIXEL_ID") or "").strip()
GA_ID = (os.getenv("GATE_GA_ID") or "").strip()
OPERATOR_WRITES = frozenset(operator_mod.WRITES)
OCSP_TIMEOUT = float(os.getenv("GATE_OCSP_TIMEOUT", "5"))

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def init():
    db.init_db()


@app.before_request
def _ensure_db():
    if not getattr(app, "_db_ready", False):
        init()
        app._db_ready = True


def advertised_url() -> str:
    return public_url_mod.resolve_public_url()



def _ops_authorized() -> bool:
    """Dogfood/production attestation is not a public form."""
    import secrets as _secrets
    got = (
        (request.headers.get("X-Ops-Token") or "")
        or (request.form.get("ops_token") or "")
        or (request.args.get("token") or "")
    ).strip()
    if OPS_TOKEN:
        return bool(got) and _secrets.compare_digest(got, OPS_TOKEN)
    return GATE_DEV_MODE


ARCHIVE_NOINDEX_PREFIXES = (
    "/this", "/bound", "/only", "/floor", "/mass", "/tattoo", "/scanner", "/uplink",
    "/inhabitant", "/afterward", "/capture", "/refusal", "/positioning", "/science",
    "/production-skin", "/runbook", "/dogfood", "/production-weld", "/docs", "/install",
    "/action-os", "/family", "/scorecard", "/proof", "/stack", "/status", "/focus",
    "/signup", "/login", "/dashboard",
)
PUBLIC_WELLKNOWN = frozenset(
    {
        "/.well-known/gate.json",
        "/.well-known/operator.json",
        "/.well-known/register.json",
        "/.well-known/legal.json",
        "/.well-known/mcp.json",
        "/.well-known/opportunities.json",
        "/.well-known/live.json",
        "/.well-known/canary.json",
    }
)


@app.after_request
def _archive_noindex(resp):
    path = request.path or ""
    archive = any(path == p or path.startswith(p + "/") for p in ARCHIVE_NOINDEX_PREFIXES)
    wk = path.startswith("/.well-known/") and path not in PUBLIC_WELLKNOWN
    if archive or wk:
        resp.headers["X-Robots-Tag"] = "noindex, nofollow"
    return resp


@app.context_processor
def inject_globals():
    return {
        "gate_public_url": advertised_url(),
        "install_price": INSTALL_PRICE_LABEL,
        "bind_room_price": BIND_ROOM_PRICE_LABEL,
        "refusal_price": REFUSAL_PRICE_LABEL,
        "weld_price": WELD_PRICE_LABEL,
        "floor_price": FLOOR_PRICE_LABEL,
        "install_slots": db.install_slots_remaining(),
        "contact_email": CONTACT_EMAIL,
        "meta_pixel_id": META_PIXEL_ID,
        "ga_id": GA_ID,
    }


@app.after_request
def cors_discovery(resp):
    path = request.path or ""
    if (
        path.startswith("/.well-known/")
        or path.startswith("/listings/")
        or path.startswith("/bind-room")
        or path.startswith("/operator")
        or path.startswith("/register")
        or path.startswith("/focus")
        or path.startswith("/refusal")
        or path in (
            "/mcp",
            "/llms.txt",
            "/openapi.json",
            "/health",
            "/robots.txt",
            "/sitemap.xml",
            "/bound",
            "/only",
            "/floor",
            "/this",
            "/capture",
            "/scanner",
            "/uplink",
            "/mass",
            "/tattoo",
        )
        or path.startswith("/demo/")
    ):
        resp.headers.setdefault("Access-Control-Allow-Origin", "*")
        resp.headers.setdefault(
            "Access-Control-Allow-Headers",
            "Authorization, Content-Type, Mcp-Session-Id, X-Gate-Key, X-API-Key",
        )
        resp.headers.setdefault("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
    return resp


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
                    "message": "Lab hop budget exhausted. Production is the weld at /operator — not a Pro plan.",
                    "request_id": f"req_{uuid.uuid4().hex[:16]}",
                    "usage": usage,
                    "operator_url": f"{advertised_url()}/operator",
                    "economics_url": f"{advertised_url()}/pricing",
                    "x402Version": 2,
                }
            }
        ),
        402,
        {
            "X-Gate-Usage-Hops": str(usage["hops"]),
            "X-Gate-Usage-Limit": str(usage["hop_limit"]),
            "X-Payment-Required": "stripe",
        },
    )


def velaru_request(method: str, path: str, **kwargs):
    url = f"{VELARU_BASE}{path}"
    headers = kwargs.pop("headers", {})
    headers.setdefault("Content-Type", "application/json")
    headers.setdefault("User-Agent", "GateAPI/1.0")
    timeout = kwargs.pop("timeout", OCSP_TIMEOUT)
    return requests.request(method, url, headers=headers, timeout=timeout, **kwargs)


def fail_closed(reason: str, fuse_id=None):
    """OCSP-shaped: unreachable is HALT, never LIVE. Relying party must not act."""
    payload = {
        "ok": False,
        "halt": True,
        "fail_closed": True,
        "ocsp": True,
        "verdict": False,
        "state": "UNREACHABLE",
        "acted": False,
        "message": "Relying party MUST halt. Timeout or upstream failure is not LIVE.",
        "reason": reason,
        "fuse_id": fuse_id,
        "charge": "CHARGE webhook is the only DEAD→LIVE path on the engine.",
        "spec": "gate-ocsp-fuse-v1",
    }
    bound.attach(payload, 503)
    headers = {
        "Cache-Control": "no-store",
        "X-Gate-Fail-Closed": "1",
        "X-Gate-Halt": "1",
    }
    return payload, 503, headers


def velaru_fuse(method: str, path: str, fuse_id=None, **kwargs):
    try:
        r = velaru_request(method, path, timeout=OCSP_TIMEOUT, **kwargs)
    except requests.Timeout:
        return fail_closed("ocsp_timeout", fuse_id)
    except requests.RequestException as e:
        return fail_closed(f"upstream_unreachable:{e}", fuse_id)
    if r.status_code >= 500:
        return fail_closed(f"upstream_{r.status_code}", fuse_id)
    try:
        data = r.json()
    except ValueError:
        return fail_closed("upstream_non_json", fuse_id)
    return data, r.status_code, {}


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
        r = velaru_request("GET", "/health", timeout=10, params={"format": "json"})
        velaru_ok = r.status_code == 200
    except requests.RequestException:
        pass
    pub = advertised_url()
    local = public_url_mod.is_local_url(pub)
    https_ok = public_url_mod.public_ok(pub)
    db_path = os.getenv("GATE_DB_PATH", "./gate.db")
    ephemeral_db = public_url_mod.db_path_is_ephemeral(db_path)
    payload = {
        "status": "ok",
        "service": "gate-api",
        "velaru_reachable": velaru_ok,
        "velaru_base": VELARU_BASE,
        "public_url": pub,
        "local": local,
        "https": https_ok,
        "ephemeral_db": ephemeral_db,
        "dev_mode": GATE_DEV_MODE,
        "listings": f"{pub}/.well-known/listings.json",
        "mcp": f"{pub}/mcp",
        "bind_room": f"{pub}/bind-room",
        "operator": f"{pub}/operator",
        "bound": f"{pub}/bound",
        "only": f"{pub}/only",
        "floor": f"{pub}/floor",
        "this": f"{pub}/this",
        "capture": f"{pub}/capture",
        "scanner": f"{pub}/scanner",
        "uplink": f"{pub}/uplink",
        "inhabitant": f"{pub}/inhabitant",
        "afterward": f"{pub}/afterward",
        "mass": f"{pub}/mass",
        "refusal": f"{pub}/refusal",
        "tattoo": f"{pub}/tattoo",
    }
    prod_public = (not local) and https_ok
    if GATE_DEV_MODE:
        return jsonify(payload)
    if not prod_public:
        payload["status"] = "not_public"
        payload["message"] = "GATE_PUBLIC_URL is still local/http. Set https origin or rely on RENDER_EXTERNAL_URL."
        return jsonify(payload), 503
    payload["status"] = "ok" if velaru_ok and not ephemeral_db else "degraded"
    return jsonify(payload)


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
        public_url=advertised_url(),
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
        r = velaru_request("GET", "/health", timeout=10, params={"format": "json"})
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
        public_url=advertised_url(),
    )


@app.route("/trust")
def trust():
    return render_template("trust.html", velaru_base=VELARU_BASE, public_url=advertised_url())


@app.route("/start")
def start_hub():
    plates = audiences.plate_list()
    return render_template("start.html", plates=plates, public_url=advertised_url())


@app.route("/focus")
def focus_hub():
    core = audiences.core_gtm_plates()
    return render_template("focus.html", plates=core, public_url=advertised_url())


@app.route("/for/<slug>")
def audience_plate(slug):
    plate = audiences.get_plate(slug)
    if not plate:
        abort(404)
    return render_template(
        "audience.html",
        slug=slug,
        plate=plate,
        public_url=advertised_url(),
        contact_email=CONTACT_EMAIL,
    )


@app.route("/pitch/<slug>")
def audience_pitch(slug):
    if not audiences.get_plate(slug):
        abort(404)
    return redirect(url_for("audience_plate", slug=slug))


@app.route("/.well-known/opportunities.json")
def well_known_opportunities():
    return jsonify(audiences.opportunities_manifest(advertised_url(), CONTACT_EMAIL))


@app.route("/demo/hop", methods=["POST"])
def demo_hop():
    ok, msg = demo_limit.allow_demo(request)
    if not ok:
        return jsonify({"error": {"code": "rate_limited", "message": msg}}), 429
    body = request.get_json(silent=True) or {}
    fuse_id = (body.get("fuse_id") or "fuse_velaru_drill").strip()
    if not demo_limit.validate_demo_fuse(fuse_id):
        return jsonify({"error": {"code": "demo_fuse_only", "message": "Demo limited to public fuses."}}), 400
    data, status, extra = velaru_fuse(
        "POST", "/api/v1/fuse/hop", fuse_id=fuse_id, json={"fuse_id": fuse_id}
    )
    if isinstance(data, dict):
        data["demo"] = True
        data["signup_url"] = f"{advertised_url()}/signup"
        bound.attach(data, status, demo=True)
    return data, status, extra


@app.route("/demo/lookup")
def demo_lookup():
    ok, msg = demo_limit.allow_demo(request)
    if not ok:
        return jsonify({"error": {"code": "rate_limited", "message": msg}}), 429
    fuse_id = request.args.get("fuse_id", "fuse_velaru_drill").strip()
    if not demo_limit.validate_demo_fuse(fuse_id):
        return jsonify({"error": {"code": "demo_fuse_only", "message": "Demo limited to public fuses."}}), 400
    data, status, extra = velaru_fuse(
        "GET", "/api/v1/fuse/lookup", fuse_id=fuse_id, params={"fuse_id": fuse_id}
    )
    if isinstance(data, dict):
        data["demo"] = True
    return data, status, extra


def _demo_gate():
    ok, msg = demo_limit.allow_demo(request)
    if not ok:
        return None, (jsonify({"error": {"code": "rate_limited", "message": msg}}), 429)
    return True, None


def run_welded_act(fuse_id: str, action: str):
    """Clearance permit only. Gate never executes the irreversible write here.

    `acted` means clearance would allow the exclusive door to proceed — not that
    money left or a bind committed. `write_executed` is always false from Gate.
    """
    hop, status, extra = velaru_fuse("POST", "/api/v1/fuse/hop", fuse_id=fuse_id, json={"fuse_id": fuse_id})
    extra = dict(extra or {})
    extra["X-Gate-Closed-World"] = "1"
    extra["X-Gate-Write-Executed"] = "0"

    if status >= 500 or (isinstance(hop, dict) and hop.get("halt")):
        if isinstance(hop, dict):
            hop["acted"] = False
            hop["write_executed"] = False
            hop["side_effect"] = False
            hop["clearance_only"] = True
            hop["action"] = action
            hop["welded"] = True
            hop["closed_world"] = True
            bound.attach(hop, status, closed_world=True)
        return hop, status, extra

    allowed = bool(isinstance(hop, dict) and hop.get("verdict") is True)
    result = {
        "spec": "gate-welded-act-v2",
        "welded": True,
        "closed_world": True,
        "clearance_only": True,
        "side_effect": False,
        "write_executed": False,
        "action": action,
        "acted": allowed,
        "clearance_allows": allowed,
        "halt": not allowed,
        "fuse_id": fuse_id,
        "hop": hop,
        "message": (
            "Clearance permit — hop LIVE/verdict true. Gate did not execute the write. "
            "Exclusive door (worker/Gosu) must enforce; bypass is out of protocol."
            if allowed
            else "Clearance refuse — DEAD or verdict false. No side door. write_executed=false."
        ),
        "their_production": False,
    }
    extra["X-Gate-Acted"] = "1" if allowed else "0"
    bound.attach(result, 200, closed_world=True)
    return result, 200, extra


@app.route("/demo/act", methods=["POST"])
def demo_act():
    _, err = _demo_gate()
    if err:
        return err
    body = request.get_json(silent=True) or {}
    fuse_id = (body.get("fuse_id") or "fuse_velaru_drill").strip()
    action = (body.get("action") or "demo").strip()[:128]
    if not demo_limit.validate_demo_fuse(fuse_id):
        return jsonify({"error": {"code": "demo_fuse_only", "message": "Demo limited to public fuses."}}), 400
    data, status, extra = run_welded_act(fuse_id, action)
    if isinstance(data, dict):
        data["demo"] = True
        data["signup_url"] = f"{advertised_url()}/signup"
        bound.attach(data, status, demo=True, closed_world=True)
    return data, status, extra


def _pas_incoming():
    raw = request.get_json(silent=True) or {}
    blocked = fields.pii_error(raw)
    if blocked:
        return None, blocked, 400
    return fields.allowlist_pas(raw), None, 200


def _verify_from(hop):
    if not isinstance(hop, dict):
        return None
    return hop.get("verify_url") or hop.get("restraint_permalink")


def _redeem_url() -> str:
    return f"{advertised_url()}/v1/pas/bind-ticket/redeem"


def _finalize_spend_plan(
    plan: dict,
    *,
    fuse_id: str,
    job_id: str | None,
    hop_d: dict,
    status: int,
    extra: dict,
    account_id,
    charge_id: str | None,
    epoch_meta: dict | None,
    decision: str,
    acted: bool,
    spend_write: dict | None = None,
    license_id: str | None = None,
    counterpart: dict | None = None,
):
    jid = (job_id or "").strip() or None
    fp = spend_protocol_mod.fingerprint(spend_write)
    if acted and not jid:
        acted = False
        decision = "HALT"
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["reason"] = plan.get("reason") or "job_id_required_for_ticket"
    if acted and not fp:
        acted = False
        decision = "HALT"
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["reason"] = plan.get("reason") or spend_protocol_mod.REASON_NOT_IN_PROTOCOL
    cp = counterpart if isinstance(counterpart, dict) else counterpart_mod.parse({})
    if acted and not cp.get("ok"):
        acted = False
        decision = "HALT"
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["reason"] = cp.get("reason") or counterpart_mod.REASON_REQUIRED
    parent = license_fuse_mod.presented(license_id)
    plan["license_fuse"] = license_fuse_mod.snapshot(parent.get("license_id"))
    # License parent halt always wins as the named reason when fused+not LIVE,
    # even if epoch already halted — otherwise reason goes missing on polluted jobs.
    if parent.get("fused") and not parent.get("ok"):
        acted = False
        decision = "HALT"
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["reason"] = parent.get("reason") or license_fuse_mod.REASON_NOT_LIVE
    elif epoch_meta and epoch_meta.get("locked"):
        acted = False
        decision = "HALT"
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["reason"] = plan.get("reason") or epoch_meta.get("reason") or "prior_halt_requires_charge"
    if plan.get("halt") and plan.get("reason") and isinstance(hop_d, dict):
        hop_d.setdefault("reason", plan["reason"])
    cid = epoch_mod.normalize_charge_id(charge_id)
    event_id = db.record_bind_event(
        fuse_id=fuse_id,
        job_id=jid,
        account_id=account_id,
        decision=decision,
        acted=acted,
        verify_url=_verify_from(hop_d),
        hop=hop_d or None,
        charge_id=cid,
    )
    row = db.get_bind_event(event_id) or {}
    ticket_pack = None
    if acted:
        ticket_pack = ticket_mod.issue(
            job_id=jid,
            fuse_id=fuse_id,
            event_id=event_id,
            receipt_hash=row.get("receipt_hash"),
            redeem_url=_redeem_url(),
            spend_write=spend_write,
            license_id=parent.get("license_id"),
            counterpart=cp,
        )
        if ticket_pack:
            plan["bind_ticket"] = ticket_pack["bearer"]
    ticket_mod.stamp(
        plan,
        ticket_public=(ticket_pack or {}).get("public") if ticket_pack else None,
        epoch=epoch_meta,
        redeem_url=_redeem_url(),
    )
    plan["spend_protocol"] = {
        "spec": spend_protocol_mod.SPEC,
        "write": spend_write,
        "fingerprint": fp,
        "spec_url": f"{advertised_url()}/.well-known/spend-protocol.json",
    }
    plan["event_id"] = event_id
    letter = inhabitant_mod.for_event(row, advertised_url())
    plan["inhabitant"] = letter
    plan["inhabitant_url"] = letter["page"]
    extra["X-Gate-Allow-Bind"] = "1" if (plan.get("allow_bind") or plan.get("bind_allowed")) else "0"
    extra["X-Gate-Ticket-TTL"] = str(ticket_mod.ttl_seconds())
    extra["X-Gate-Event-Id"] = event_id
    extra["X-Gate-Inhabitant"] = letter["page"]
    out_status = status if status >= 500 else 200
    bound.attach(plan, out_status)
    return plan, out_status, extra


def _num(value):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def run_policycenter_pre_bind(body: dict, account_id=None):
    fuse_id = (body.get("fuse_id") or "fuse_velaru_drill").strip()
    job_id = (str(body.get("job_id") or "")).strip()
    hop, status, extra = velaru_fuse(
        "POST", "/api/v1/fuse/hop", fuse_id=fuse_id or None, json={"fuse_id": fuse_id}
    )
    extra = dict(extra or {})
    hop_d = hop if isinstance(hop, dict) else {}
    hop_d, epoch_meta = epoch_mod.apply(
        job_id=job_id, hop=hop_d, charge_id=body.get("charge_id")
    )
    plan = weld.policycenter_plan(job_id, hop_d, status, body.get("issue_type"))
    plan["fuse_id"] = fuse_id
    spend_write = spend_protocol_mod.intended_policycenter(
        job_id=job_id,
        action=body.get("action"),
        method=body.get("method"),
        path=body.get("path") or body.get("bind_path"),
        bind_path=body.get("bind_path"),
    )
    if plan.get("allow_bind") and spend_write is None:
        plan["allow_bind"] = False
        plan["halt"] = True
        plan["next"] = None
        plan["reason"] = spend_protocol_mod.REASON_NOT_IN_PROTOCOL
    decision = "ALLOW" if plan.get("allow_bind") else ("HALT" if hop_d.get("halt") else "BLOCK")
    return _finalize_spend_plan(
        plan,
        fuse_id=fuse_id,
        job_id=job_id,
        hop_d=hop_d,
        status=status,
        extra=extra,
        account_id=account_id,
        charge_id=body.get("charge_id"),
        epoch_meta=epoch_meta,
        decision=decision,
        acted=bool(plan.get("allow_bind")),
        spend_write=spend_write,
        license_id=body.get("license_id"),
        counterpart=counterpart_mod.parse(body),
    )


def run_mga_authority(body: dict, account_id=None):
    fuse_id = (body.get("fuse_id") or "fuse_velaru_drill").strip()
    hop, status, extra = velaru_fuse(
        "POST", "/api/v1/fuse/hop", fuse_id=fuse_id or None, json={"fuse_id": fuse_id}
    )
    extra = dict(extra or {})
    hop_d = hop if isinstance(hop, dict) else {}
    job_id = (str(body.get("job_id") or "")).strip()
    hop_d, epoch_meta = epoch_mod.apply(
        job_id=job_id, hop=hop_d, charge_id=body.get("charge_id")
    )
    plan = weld.mga_authority(
        hop_d,
        status,
        premium=_num(body.get("premium")),
        authority_limit=_num(body.get("authority_limit")),
        line=body.get("line"),
        state=body.get("state"),
        allowed_lines=body.get("allowed_lines") if isinstance(body.get("allowed_lines"), list) else None,
        allowed_states=body.get("allowed_states") if isinstance(body.get("allowed_states"), list) else None,
    )
    plan["fuse_id"] = fuse_id
    plan["job_id"] = job_id or None
    if plan.get("reasons"):
        hop_d["constraint_reasons"] = plan["reasons"]
    spend_write = spend_protocol_mod.intended_mga(job_id=job_id)
    return _finalize_spend_plan(
        plan,
        fuse_id=fuse_id,
        job_id=job_id,
        hop_d=hop_d,
        status=status,
        extra=extra,
        account_id=account_id,
        charge_id=body.get("charge_id"),
        epoch_meta=epoch_meta,
        decision=plan.get("result") or "BLOCK",
        acted=bool(plan.get("bind_allowed")),
        spend_write=spend_write,
        license_id=body.get("license_id"),
        counterpart=counterpart_mod.parse(body),
    )


def run_duckcreek_pre_bind(body: dict, account_id=None):
    fuse_id = (body.get("fuse_id") or "fuse_velaru_drill").strip()
    job_id = (str(body.get("job_id") or "")).strip()
    hop, status, extra = velaru_fuse(
        "POST", "/api/v1/fuse/hop", fuse_id=fuse_id or None, json={"fuse_id": fuse_id}
    )
    extra = dict(extra or {})
    hop_d = hop if isinstance(hop, dict) else {}
    hop_d, epoch_meta = epoch_mod.apply(
        job_id=job_id, hop=hop_d, charge_id=body.get("charge_id")
    )
    plan = weld.duckcreek_plan(job_id, hop_d, status)
    plan["fuse_id"] = fuse_id
    spend_write = spend_protocol_mod.intended_duckcreek(job_id=job_id)
    decision = "ALLOW" if plan.get("allow_bind") else ("HALT" if hop_d.get("halt") else "BLOCK")
    return _finalize_spend_plan(
        plan,
        fuse_id=fuse_id,
        job_id=job_id,
        hop_d=hop_d,
        status=status,
        extra=extra,
        account_id=account_id,
        charge_id=body.get("charge_id"),
        epoch_meta=epoch_meta,
        decision=decision,
        acted=bool(plan.get("allow_bind")),
        spend_write=spend_write,
        license_id=body.get("license_id"),
        counterpart=counterpart_mod.parse(body),
    )


@app.route("/demo/pas/bind-check", methods=["POST"])
def demo_pas_bind_check():
    _, err = _demo_gate()
    if err:
        return err
    body, blocked, code = _pas_incoming()
    if blocked:
        return blocked, code
    data, status, extra = velaru_fuse("POST", "/pas/v1/bind-check/demo", json=body)
    if isinstance(data, dict):
        data["demo"] = True
        data["signup_url"] = f"{advertised_url()}/signup"
        data["listing"] = f"{advertised_url()}/.well-known/listings.json"
        data["bind_room"] = f"{advertised_url()}/bind-room"
        bound.attach(data, status, demo=True)
    return data, status, extra


@app.route("/demo/pas/policycenter/pre-bind", methods=["POST"])
def demo_pc_pre_bind():
    _, err = _demo_gate()
    if err:
        return err
    body, blocked, code = _pas_incoming()
    if blocked:
        return blocked, code
    fuse_id = (body.get("fuse_id") or "fuse_velaru_drill").strip()
    if not demo_limit.validate_demo_fuse(fuse_id):
        return {"error": {"code": "demo_fuse_only"}}, 400
    body["fuse_id"] = fuse_id
    data, status, extra = run_policycenter_pre_bind(body)
    if isinstance(data, dict):
        data["demo"] = True
        bound.attach(data, status, demo=True)
    return data, status, extra


def _redeem_ticket_view(*, demo: bool = False):
    raw = request.get_json(silent=True) or {}
    blocked = fields.pii_error(raw)
    if blocked:
        return blocked, 400
    body = fields.allowlist_pas(raw)
    result = ticket_mod.redeem(
        ticket_id=str(body.get("ticket_id") or ""),
        token=str(body.get("token") or ""),
        job_id=str(body.get("job_id") or ""),
        method=str(body.get("method") or ""),
        path=str(body.get("path") or ""),
        spend_fingerprint=str(body.get("spend_fingerprint") or ""),
        spend_kind=str(body.get("spend_kind") or "") or None,
        now=str(body.get("now") or ""),
        license_id=str(body.get("license_id") or "") or None,
        counterpart=counterpart_mod.parse(body),
    )
    if isinstance(result, dict):
        result["demo"] = demo
        bound.attach(result, 200 if result.get("ok") else 403, demo=demo)
    return result, 200 if result.get("ok") else 403


def _license_body():
    raw = request.get_json(silent=True) or {}
    blocked = fields.pii_error(raw)
    if blocked:
        return None, blocked, 400
    return fields.allowlist_pas(raw), None, 200


def _license_charge_view(license_id: str, *, demo: bool = False):
    body, blocked, code = _license_body()
    if blocked:
        return blocked, code
    result = license_fuse_mod.charge(
        license_id=license_id,
        charge_id=(body or {}).get("charge_id"),
    )
    if isinstance(result, dict):
        result["demo"] = demo
        bound.attach(result, 200 if result.get("ok") else 403, demo=demo)
    return result, 200 if result.get("ok") else 403


def _license_dead_view(license_id: str, *, demo: bool = False):
    raw = request.get_json(silent=True) or {}
    if raw:
        blocked = fields.pii_error(raw)
        if blocked:
            return blocked, 400
    result = license_fuse_mod.dead(license_id=license_id)
    if isinstance(result, dict):
        result["demo"] = demo
        bound.attach(result, 200 if result.get("ok") else 403, demo=demo)
    return result, 200 if result.get("ok") else 403


def _license_snapshot_view(license_id: str, *, demo: bool = False):
    lid = license_fuse_mod.normalize_id(license_id)
    if not lid:
        payload = {"ok": False, "halt": True, "reason": license_fuse_mod.REASON_INVALID, "demo": demo}
        bound.attach(payload, 400, demo=demo)
        return payload, 400
    snap = license_fuse_mod.snapshot(lid)
    snap["ok"] = True
    snap["demo"] = demo
    bound.attach(snap, 200, demo=demo)
    return snap, 200


@app.route("/demo/pas/licenses/<license_id>/charge", methods=["POST"])
def demo_license_charge(license_id):
    _, err = _demo_gate()
    if err:
        return err
    return _license_charge_view(license_id, demo=True)


@app.route("/demo/pas/licenses/<license_id>/dead", methods=["POST"])
def demo_license_dead(license_id):
    _, err = _demo_gate()
    if err:
        return err
    return _license_dead_view(license_id, demo=True)


@app.route("/demo/pas/licenses/<license_id>", methods=["GET"])
def demo_license_snapshot(license_id):
    _, err = _demo_gate()
    if err:
        return err
    return _license_snapshot_view(license_id, demo=True)


@app.route("/demo/pas/bind-ticket/redeem", methods=["POST"])
def demo_bind_ticket_redeem():
    _, err = _demo_gate()
    if err:
        return err
    return _redeem_ticket_view(demo=True)


@app.route("/demo/pas/mga-authority", methods=["POST"])
def demo_mga_authority():
    _, err = _demo_gate()
    if err:
        return err
    body, blocked, code = _pas_incoming()
    if blocked:
        return blocked, code
    fuse_id = (body.get("fuse_id") or "fuse_velaru_drill").strip()
    if not demo_limit.validate_demo_fuse(fuse_id):
        return {"error": {"code": "demo_fuse_only"}}, 400
    body["fuse_id"] = fuse_id
    data, status, extra = run_mga_authority(body)
    if isinstance(data, dict):
        data["demo"] = True
        bound.attach(data, status, demo=True)
    return data, status, extra


@app.route("/demo/pas/duckcreek/pre-bind", methods=["POST"])
def demo_dc_pre_bind():
    _, err = _demo_gate()
    if err:
        return err
    body, blocked, code = _pas_incoming()
    if blocked:
        return blocked, code
    fuse_id = (body.get("fuse_id") or "fuse_velaru_drill").strip()
    if not demo_limit.validate_demo_fuse(fuse_id):
        return {"error": {"code": "demo_fuse_only"}}, 400
    body["fuse_id"] = fuse_id
    data, status, extra = run_duckcreek_pre_bind(body)
    if isinstance(data, dict):
        data["demo"] = True
        bound.attach(data, status, demo=True)
    return data, status, extra


@app.route("/.well-known/gate.json")
def well_known_gate():
    return jsonify(
        {
            "name": "Gate API",
            "description": (
                "Clearance before irreversible withdraw, payout, and bind. "
                "Fail closed under uncertainty. Weld + management + bps. "
                "Licensed operators. Metered fuse hop. Independent verify."
            ),
            "formula": (
                "Own permission on irreversible acts for any power that needs it — "
                "clearance fails closed; the DENY is the product, not narrative."
            ),
            "version": "1.0.0",
            "openapi": f"{advertised_url()}/openapi.json",
            "signup": f"{advertised_url()}/signup",
            "install": f"{advertised_url()}/install",
            "bind_room": f"{advertised_url()}/bind-room",
            "operator": f"{advertised_url()}/operator",
            "register": f"{advertised_url()}/register",
            "register_manifest": f"{advertised_url()}/.well-known/register.json",
            "operator_invoice": f"{advertised_url()}/.well-known/operator.json",
            "bound": f"{advertised_url()}/bound",
            "only": f"{advertised_url()}/only",
            "floor": f"{advertised_url()}/floor",
            "this": f"{advertised_url()}/this",
            "capture": f"{advertised_url()}/capture",
            "scanner": f"{advertised_url()}/scanner",
            "uplink": f"{advertised_url()}/uplink",
            "inhabitant": f"{advertised_url()}/inhabitant",
            "afterward": f"{advertised_url()}/afterward",
            "bound_answer": f"{advertised_url()}/.well-known/bound-answer.json",
            "exclusive_timing": f"{advertised_url()}/.well-known/exclusive-timing.json",
            "stakes": f"{advertised_url()}/.well-known/floor.json",
            "particular": f"{advertised_url()}/.well-known/particular.json",
            "inhabitant_manifest": f"{advertised_url()}/.well-known/inhabitant.json",
            "afterward_manifest": f"{advertised_url()}/.well-known/afterward.json",
            "verify_engine": "https://velaru.xyz/verify",
            "demo_hop": f"{advertised_url()}/demo/hop",
            "demo_act": f"{advertised_url()}/demo/act",
            "demo_pas": f"{advertised_url()}/demo/pas/bind-check",
            "ocsp": f"{advertised_url()}/v1/fuse/lookup",
            "act": f"{advertised_url()}/v1/act",
            "pas_bind": f"{advertised_url()}/v1/pas/bind-check",
            "policycenter_pre_bind": f"{advertised_url()}/v1/pas/policycenter/pre-bind",
            "mga_authority": f"{advertised_url()}/v1/pas/mga-authority",
            "mcp": f"{advertised_url()}/mcp",
            "mcp_discovery": f"{advertised_url()}/.well-known/mcp.json",
            "x402": f"{advertised_url()}/.well-known/x402.json",
            "listings": f"{advertised_url()}/.well-known/listings.json",
            "counterfactual_spend": f"{advertised_url()}/.well-known/counterfactual-spend.json",
            "kappa_register": f"{advertised_url()}/.well-known/kappa.json",
            "schism": f"{advertised_url()}/.well-known/schism.json",
            "positioning": f"{advertised_url()}/.well-known/positioning.json",
            "action_os": f"{advertised_url()}/.well-known/action-os.json",
            "action_os_page": f"{advertised_url()}/action-os",
            "scorecard": f"{advertised_url()}/.well-known/scorecard.json",
            "scorecard_page": f"{advertised_url()}/scorecard",
            "family": f"{advertised_url()}/.well-known/family.json",
            "family_page": f"{advertised_url()}/family",
            "production_skin": f"{advertised_url()}/.well-known/production-skin.json",
            "proof_suite": f"{advertised_url()}/.well-known/proof-suite.json",
            "science_pri": f"{advertised_url()}/.well-known/science-pri.json",
            "science_page": f"{advertised_url()}/science",
            "legal": f"{advertised_url()}/.well-known/legal.json",
            "privacy": f"{advertised_url()}/privacy",
            "terms": f"{advertised_url()}/terms",
            "runbook": f"{advertised_url()}/.well-known/runbook.json",
            "runbook_page": f"{advertised_url()}/runbook",
            "dogfood": f"{advertised_url()}/dogfood",
            "production_weld": f"{advertised_url()}/production-weld",
            "live": f"{advertised_url()}/live",
            "live_json": f"{advertised_url()}/.well-known/live.json",
            "canary": f"{advertised_url()}/.well-known/canary.json",
            "canary_report": f"{advertised_url()}/v1/canary/bypass",
            "evidence_head": f"{advertised_url()}/.well-known/evidence-head.json",
            "receipt": f"{advertised_url()}/.well-known/receipt/{{event_id}}.json",
            "receipt_inclusion_proof": f"{advertised_url()}/.well-known/receipt/{{event_id}}/proof.json",
            "commit_auth": f"{advertised_url()}/.well-known/commit-auth.json",
            "spend_protocol": f"{advertised_url()}/.well-known/spend-protocol.json",
            "command_radiation": f"{advertised_url()}/.well-known/command-radiation.json",
            "license_fuse": f"{advertised_url()}/.well-known/license-fuse.json",
            "restraint": f"{advertised_url()}/.well-known/restraint.json",
            "exclusion": f"{advertised_url()}/.well-known/exclusion.json?job_id={{job_id}}",
            "evidence_consistency": f"{advertised_url()}/.well-known/evidence-consistency.json?old_size={{n}}",
            "bind_ticket_redeem": f"{advertised_url()}/v1/pas/bind-ticket/redeem",
            "fail_closed": "Timeout or 5xx → HTTP 503 halt. Never treat UNREACHABLE as LIVE.",
            "charge": "DEAD→LIVE only via Velaru CHARGE webhook.",
            "sdk": {
                "python": "from gate.sdk import GateClient",
                "pip": "pip install -r requirements.txt  # sdk in-repo",
            },
            "patent": "64/124,027",
            "operator": "Nisaba LLC",
        }
    )


@app.route("/.well-known/mcp.json")
def well_known_mcp():
    return jsonify(listings_mod.mcp_discovery(advertised_url()))


@app.route("/.well-known/x402.json")
def well_known_x402():
    return jsonify(listings_mod.x402_catalog(advertised_url()))


@app.route("/.well-known/listings.json")
def well_known_listings():
    return jsonify(listings_mod.listings_manifest(advertised_url(), CONTACT_EMAIL))


@app.route("/.well-known/operator.json")
def well_known_operator():
    return jsonify(operator_mod.manifest(advertised_url(), CONTACT_EMAIL))


@app.route("/.well-known/register.json")
def well_known_register():
    return jsonify(register_mod.manifest(advertised_url(), CONTACT_EMAIL))


@app.route("/.well-known/charge-authority.json")
def well_known_charge_authority():
    try:
        from gate import charge_authority as charge_mod
    except ImportError:
        import charge_authority as charge_mod

    return jsonify(
        {
            "spec": charge_mod.SPEC,
            "name": "CHARGE authority",
            "accepted": [
                "GATE_DEV_MODE chg_* drill tokens",
                "sig:{nonce}:{hmac} bound to purpose|subject|nonce",
                "paid install/operator checkout session id",
                "Stripe PaymentIntent pi_* with status=succeeded",
            ],
            "replay": "each charge_id consumed at most once",
            "license_charge": f"{advertised_url()}/v1/pas/licenses/{{license_id}}/charge",
            "their_production": False,
        }
    )


@app.route("/v1/register/cleared", methods=["POST"])
def register_cleared_flow():
    """Ops-only: record cleared cents against a paid weld/checkout (fee ledger)."""
    if not _ops_authorized():
        return jsonify({"ok": False, "error": {"code": "ops_token_required"}}), 401
    body = request.get_json(silent=True) or {}
    try:
        entry = db.record_cleared_flow(
            cleared_cents=int(body.get("cleared_cents") or 0),
            hop_count=int(body.get("hop_count") or 0),
            weld_order_id=(body.get("weld_order_id") or "").strip() or None,
            install_session_id=(body.get("install_session_id") or body.get("session_id") or "").strip()
            or None,
            note=(body.get("note") or "").strip(),
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": {"code": "invalid", "message": str(exc)}}), 400
    totals = db.cleared_flow_totals()
    return jsonify({"ok": True, "entry": entry, "totals": totals, "their_production": False})


@app.route("/.well-known/cleared-flow.json")
def well_known_cleared_flow():
    totals = db.cleared_flow_totals()
    return jsonify(
        {
            "spec": "gate-cleared-flow-v1",
            "totals": totals,
            "post": f"{advertised_url()}/v1/register/cleared",
            "note": "Ledger of cleared flow for fee register — not a production claim.",
            "their_production": False,
        }
    )


@app.route("/.well-known/settlement.json")
def well_known_settlement():
    try:
        from gate import settlement as settlement_mod
    except ImportError:
        import settlement as settlement_mod
    return jsonify(settlement_mod.spec(advertised_url()))


@app.route("/.well-known/settlement-members.json")
def well_known_settlement_members():
    import db as gate_db

    return jsonify(
        {
            "spec": "gate-settlement-members-v1",
            "their_production": False,
            "members": gate_db.list_settlement_members(limit=50),
        }
    )


@app.route("/.well-known/settlement-windows.json")
def well_known_settlement_windows():
    import db as gate_db

    return jsonify(
        {
            "spec": "gate-settlement-windows-v1",
            "their_production": False,
            "windows": gate_db.list_settlement_windows(limit=20),
        }
    )


@app.route("/.well-known/kappa.json")
def well_known_kappa():
    import db as gate_db

    try:
        from gate import kappa as kappa_mod
    except ImportError:
        import kappa as kappa_mod
    events = gate_db.list_bind_events_chronological(limit=10000)
    return jsonify(kappa_mod.register_from_events(events, public_url=advertised_url()))


@app.route("/.well-known/schism.json")
def well_known_schism():
    try:
        from gate import kappa as kappa_mod
    except ImportError:
        import kappa as kappa_mod
    return jsonify(kappa_mod.schism_manifest(advertised_url()))


@app.route("/.well-known/positioning.json")
def well_known_positioning():
    return jsonify(positioning_mod.manifest(advertised_url()))


@app.route("/.well-known/action-os.json")
def well_known_action_os():
    return jsonify(action_os_mod.manifest(advertised_url()))


@app.route("/.well-known/scorecard.json")
def well_known_scorecard():
    return jsonify(scorecard_mod.manifest(advertised_url()))


@app.route("/.well-known/live.json")
def well_known_live():
    return jsonify(live_mod.desk(advertised_url()))


@app.route("/.well-known/canary.json")
def well_known_canary():
    return jsonify(canary_mod.manifest(advertised_url()))


@app.route("/live")
def live_page():
    desk = live_mod.desk(advertised_url())
    return render_template("live.html", desk=desk, public_url=advertised_url())


@app.route("/v1/canary/bypass", methods=["POST"])
def canary_bypass_report():
    if not _ops_authorized():
        return jsonify({"ok": False, "error": {"code": "ops_token_required"}}), 401
    body = request.get_json(silent=True) or {}
    result = canary_mod.report(
        write_path=(body.get("write_path") or "").strip(),
        job_id=(body.get("job_id") or "").strip() or None,
        reporter=(body.get("reporter") or "").strip(),
        note=(body.get("note") or "").strip(),
        license_id=(body.get("license_id") or "").strip() or None,
        kill_parent=bool(body.get("kill_parent")),
        confirm=bool(body.get("confirm")),
    )
    code = 200 if result.get("ok") else 400
    return jsonify(result), code


@app.route("/.well-known/production-skin.json")
def well_known_production_skin():
    return jsonify(production_skin_mod.manifest(advertised_url()))


@app.route("/.well-known/proof-suite.json")
def well_known_proof_suite():
    return jsonify(proof_suite_mod.manifest(advertised_url()))


@app.route("/.well-known/science-pri.json")
def well_known_science_pri():
    return jsonify(science_pri_mod.manifest(advertised_url()))


@app.route("/science")
def science_page():
    m = science_pri_mod.manifest(advertised_url())
    return render_template(
        "science.html",
        manifest=m,
        blocks=science_pri_mod.page_blocks(),
        public_url=advertised_url(),
    )


@app.route("/.well-known/legal.json")
def well_known_legal():
    return jsonify(
        legal_mod.manifest(
            advertised_url(),
            CONTACT_EMAIL,
            meta_pixel_id=META_PIXEL_ID,
            ga_id=GA_ID,
        )
    )


@app.route("/privacy")
def privacy_page():
    return render_template(
        "legal.html",
        kind="privacy",
        doc=legal_mod.PRIVACY,
        contact_email=CONTACT_EMAIL,
        public_url=advertised_url(),
    )


@app.route("/terms")
def terms_page():
    return render_template(
        "legal.html",
        kind="terms",
        doc=legal_mod.TERMS,
        contact_email=CONTACT_EMAIL,
        public_url=advertised_url(),
    )


@app.route("/.well-known/family.json")
def well_known_family_voices():
    return jsonify(family_voices_mod.manifest(advertised_url()))


@app.route("/.well-known/family/<slug>.json")
def well_known_family_voice(slug: str):
    if slug not in family_voices_mod.VOICES:
        abort(404)
    return jsonify(family_voices_mod.voice(slug, advertised_url()))


@app.route("/family")
def family_hub():
    m = family_voices_mod.manifest(advertised_url())
    return render_template("family.html", manifest=m, public_url=advertised_url())


@app.route("/family/<slug>")
def family_voice_page(slug: str):
    if slug not in family_voices_mod.VOICES:
        abort(404)
    return render_template(
        "family_voice.html",
        voice=family_voices_mod.voice(slug, advertised_url()),
        public_url=advertised_url(),
    )


@app.route("/family/<slug>/paste.txt")
def family_paste(slug: str):
    if slug not in family_voices_mod.VOICES:
        abort(404)
    body = family_voices_mod.paste_pack(slug)
    return Response(
        body,
        mimetype="text/plain; charset=utf-8",
        headers={"Cache-Control": "public, max-age=300"},
    )


@app.route("/scorecard")
def scorecard_page():
    m = scorecard_mod.manifest(advertised_url())
    return render_template("scorecard.html", manifest=m, public_url=advertised_url())


@app.route("/production-skin")
def production_skin_page():
    m = production_skin_mod.manifest(advertised_url())
    return render_template("production_skin.html", manifest=m, public_url=advertised_url())


@app.route("/proof")
def proof_page():
    m = proof_suite_mod.manifest(advertised_url())
    return render_template("proof.html", manifest=m, public_url=advertised_url())


@app.route("/runbook")
def runbook_page():
    m = runbook_mod.manifest(advertised_url())
    return render_template("runbook.html", manifest=m, public_url=advertised_url())


@app.route("/dogfood", methods=["GET", "POST"])
def dogfood_page():
    """First-party dogfood weld record. Does not flip their_production."""
    error = None
    recorded = None
    if request.method == "POST":
        if not _ops_authorized():
            error = "Ops token required. Dogfood attestation is not a public form."
        write_path = (request.form.get("write_path") or "").strip()
        operator = (request.form.get("operator") or "").strip()
        note = (request.form.get("note") or "").strip()
        try:
            if error:
                raise ValueError(error)
            result = production_skin_mod.record_dogfood_weld(
                write_path=write_path,
                operator=operator,
                note=note,
            )
            if not result.get("ok"):
                error = result.get("error") or "Could not record dogfood weld"
            else:
                recorded = result.get("weld")
                flash(
                    "Dogfood weld recorded. their_production stays false until a third-party weld.",
                    "success",
                )
        except ValueError as exc:
            error = str(exc)
        except Exception as exc:  # noqa: BLE001 — surface honestly
            error = str(exc)
    m = production_skin_mod.manifest(advertised_url())
    latest = None
    try:
        import db as gate_db

        latest = gate_db.latest_dogfood_weld()
    except Exception:  # noqa: BLE001
        latest = None
    return render_template(
        "dogfood.html",
        manifest=m,
        latest=latest or recorded,
        error=error,
        public_url=advertised_url(),
    )


@app.route("/production-weld", methods=["GET", "POST"])
def production_weld_page():
    """Explicit third-party production weld. Never auto from demo/dev checkout."""
    error = None
    recorded = None
    if request.method == "POST":
        if not _ops_authorized():
            error = "Ops token required. Production attestation is not a public form."
        write_path = (request.form.get("write_path") or "").strip()
        counterparty = (request.form.get("counterparty") or "").strip()
        note = (request.form.get("note") or "").strip()
        exclusive_door_url = (request.form.get("exclusive_door_url") or "").strip()
        door_kind = (request.form.get("door_kind") or "").strip()
        worker_fingerprint = (request.form.get("worker_fingerprint") or "").strip()
        confirm = (request.form.get("confirm") or "").strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        exclusivity_confirm = (request.form.get("exclusivity_confirm") or "").strip().lower() in (
            "1",
            "true",
            "yes",
            "on",
        )
        # Refuse recording a first-party email as "third-party" theater
        first_party = {
            CONTACT_EMAIL.lower(),
            "hello@velaru.xyz",
            "hello@nisaba.io",
            "nisaba",
        }
        if not error and (counterparty.lower() in first_party or counterparty.lower().endswith("@nisaba.io")):
            # Allow nisaba only if they confirm it's on a customer write path
            if "their" not in note.lower() and "customer" not in note.lower() and "third" not in note.lower():
                error = (
                    "First-party counterparty needs note naming the customer write "
                    "(their/customer/third). Prefer dogfood for Nisaba-only welds."
                )
        if not error and not exclusivity_confirm:
            error = "Exclusivity confirm required — attest the exclusive door is the only mouth."
        if not error:
            try:
                result = production_skin_mod.record_production_weld(
                    write_path=write_path,
                    counterparty=counterparty,
                    note=note,
                    confirm=confirm,
                    exclusive_door_url=exclusive_door_url,
                    door_kind=door_kind,
                    worker_fingerprint=worker_fingerprint or None,
                )
                if not result.get("ok"):
                    error = result.get("error") or "Could not record production weld"
                else:
                    recorded = result.get("weld")
                    flash(
                        "Third-party production weld recorded with exclusivity attestation. their_production is now true.",
                        "success",
                    )
            except ValueError as exc:
                error = str(exc)
            except Exception as exc:  # noqa: BLE001
                error = str(exc)
    m = production_skin_mod.manifest(advertised_url())
    latest = None
    try:
        import db as gate_db

        latest = gate_db.latest_production_weld()
    except Exception:  # noqa: BLE001
        latest = None
    return render_template(
        "production_weld.html",
        manifest=m,
        latest=latest or recorded,
        error=error,
        public_url=advertised_url(),
    )


@app.route("/.well-known/runbook.json")
def well_known_runbook():
    return jsonify(runbook_mod.manifest(advertised_url()))


@app.route("/action-os")
def action_os_page():
    m = action_os_mod.manifest(advertised_url())
    return render_template(
        "action_os.html",
        manifest=m,
        blocks=action_os_mod.page_blocks(),
        public_url=advertised_url(),
    )


@app.route("/positioning")
def positioning_page():
    m = positioning_mod.manifest(advertised_url())
    return render_template(
        "positioning.html",
        headline=m["one_line"],
        focus_plain=m.get("focus_plain"),
        focus_for=m.get("focus_for") or [],
        next_steps=m.get("next_steps") or [],
        cards=positioning_mod.page_cards(),
    )


@app.route("/register")
def register_page():
    return render_template(
        "register.html",
        public_url=advertised_url(),
        weld_price=WELD_PRICE_LABEL,
        floor_price=FLOOR_PRICE_LABEL,
    )


@app.route("/stack")
def stack_page():
    return render_template(
        "stack.html",
        public_url=advertised_url(),
        weld_price=WELD_PRICE_LABEL,
        floor_price=FLOOR_PRICE_LABEL,
    )


@app.route("/export/operator-one-pager.txt")
def export_operator_one_pager():
    body = operator_mod.render_one_pager(advertised_url(), CONTACT_EMAIL)
    return Response(body, mimetype="text/plain; charset=utf-8", headers={"Cache-Control": "public, max-age=300"})


@app.route("/.well-known/bound-answer.json")
def well_known_bound_answer():
    return jsonify(bound.manifesto(advertised_url()))


@app.route("/bound")
def bound_page():
    return render_template("bound.html", public_url=advertised_url())


@app.route("/.well-known/exclusive-timing.json")
def well_known_exclusive():
    return jsonify(exclusive.manifesto(advertised_url()))


@app.route("/only")
def only_page():
    return render_template("only.html", public_url=advertised_url())


@app.route("/.well-known/floor.json")
def well_known_floor():
    return jsonify(floor.manifesto(advertised_url()))


@app.route("/floor")
def floor_page():
    return render_template("floor.html", public_url=advertised_url())


@app.route("/.well-known/particular.json")
def well_known_particular():
    return jsonify(particular.manifesto(advertised_url()))


@app.route("/this")
def this_page():
    return render_template("this.html", public_url=advertised_url())


@app.route("/.well-known/inhabitant.json")
def well_known_inhabitant():
    return jsonify(inhabitant_mod.manifest(advertised_url()))


@app.route("/.well-known/inhabitant/<event_id>.json")
def well_known_inhabitant_letter(event_id: str):
    row = db.get_bind_event(event_id)
    if not row:
        return jsonify(inhabitant_mod.missing(advertised_url(), event_id)), 404
    return jsonify(inhabitant_mod.for_event(row, advertised_url()))


@app.route("/inhabitant")
def inhabitant_page():
    return render_template("inhabitant.html", public_url=advertised_url(), letter=None, missing=False)


@app.route("/inhabitant/<event_id>")
def inhabitant_letter_page(event_id: str):
    row = db.get_bind_event(event_id)
    if not row:
        return (
            render_template(
                "inhabitant.html",
                public_url=advertised_url(),
                letter=None,
                missing=True,
            ),
            404,
        )
    letter = inhabitant_mod.for_event(row, advertised_url())
    return render_template(
        "inhabitant.html", public_url=advertised_url(), letter=letter, missing=False
    )


@app.route("/.well-known/afterward.json")
def well_known_afterward():
    return jsonify(inhabitant_mod.afterward_manifest(advertised_url()))


@app.route("/afterward")
def afterward_page():
    return render_template("afterward.html", public_url=advertised_url())


@app.route("/.well-known/capture.json")
def well_known_capture():
    return jsonify(weld.capture_manifest(advertised_url()))


@app.route("/.well-known/receipt/<event_id>.json")
def well_known_receipt(event_id: str):
    row = db.get_bind_event(event_id)
    if not row:
        abort(404)
    try:
        from gate import receipt as receipt_mod
    except ImportError:
        import receipt as receipt_mod
    return jsonify(receipt_mod.receipt_to_public_payload(receipt_row=row, public_url=advertised_url()))


@app.route("/.well-known/receipt/<event_id>/proof.json")
def well_known_receipt_proof(event_id: str):
    try:
        from gate import evidence_log as evidence_log_mod
    except ImportError:
        import evidence_log as evidence_log_mod

    rows = db.list_bind_events_chronological()
    bundle = evidence_log_mod.proof_bundle(rows, event_id)
    if not bundle:
        abort(404)
    return jsonify(bundle)


@app.route("/.well-known/evidence-packet/<event_id>.json")
def well_known_evidence_packet(event_id: str):
    """Operator/Risk-committee convenience: one object with receipt + inclusion proof.

    This is intentionally public (no PII) and is meant to be a single "evidence download"
    for each bind event id.
    """
    try:
        from gate import evidence_log as evidence_log_mod
    except ImportError:
        import evidence_log as evidence_log_mod

    try:
        from gate import receipt as receipt_mod
    except ImportError:
        import receipt as receipt_mod

    row = db.get_bind_event(event_id)
    if not row:
        abort(404)

    rows = db.list_bind_events_chronological()
    bundle = evidence_log_mod.proof_bundle(rows, event_id)
    if not bundle:
        abort(404)

    receipt_payload = receipt_mod.receipt_to_public_payload(
        receipt_row=row, public_url=advertised_url()
    )

    return jsonify(
        {
            "spec": "gate-evidence-packet-v1",
            "event_id": event_id,
            "their_production": False,
            "evidence_head": bundle.get("tree_head"),
            "receipt": receipt_payload,
            "receipt_inclusion_proof": bundle,
            "urls": {
                "receipt": f"{advertised_url()}/.well-known/receipt/{event_id}.json",
                "receipt_inclusion_proof": f"{advertised_url()}/.well-known/receipt/{event_id}/proof.json",
                "evidence_head": f"{advertised_url()}/.well-known/evidence-head.json",
            },
        }
    )


@app.route("/.well-known/evidence-head.json")
def well_known_evidence_head():
    try:
        from gate import evidence_log as evidence_log_mod
    except ImportError:
        import evidence_log as evidence_log_mod

    rows = db.list_bind_events_chronological()
    leaves = evidence_log_mod.log_from_rows(rows)
    return jsonify(evidence_log_mod.signed_tree_head(leaves))


@app.route("/.well-known/counterfactual-spend.json")
def well_known_counterfactual_spend():
    try:
        from gate import counterfactual as counterfactual_mod
    except ImportError:
        import counterfactual as counterfactual_mod
    return jsonify(counterfactual_mod.manifest(advertised_url()))


@app.route("/.well-known/commit-auth.json")
def well_known_commit_auth():
    return jsonify(
        {
            "spec": "gate-commit-auth-v1",
            "greater_than_ed25519": (
                "Signatures prove a hop occurred. Tickets, epoch lock, and exclusion "
                "prove the hop cannot spend stale, cannot resurrect without CHARGE, "
                "and that this job has no spend leaf."
            ),
            "bind_ticket": ticket_mod.manifest(advertised_url()),
            "spend_protocol": spend_protocol_mod.spec(advertised_url()),
            "command_radiation": command_radiation_mod.spec(advertised_url()),
            "epoch": {
                "spec": "gate-epoch-v1",
                "rule": "Latest HALT/BLOCK for a job_id stays HALT until charge_id is presented.",
                "not_admin_charge": True,
            },
            "license_fuse": license_fuse_mod.spec(advertised_url()),
            "counterpart": counterpart_mod.spec(advertised_url()),
            "restraint": f"{advertised_url()}/.well-known/restraint.json",
            "exclusion": exclusion_mod.manifest(advertised_url()),
            "ttl_seconds": ticket_mod.ttl_seconds(),
            "stale_hop_cannot_spend": True,
            "their_production": False,
        }
    )


@app.route("/.well-known/spend-protocol.json")
def well_known_spend_protocol():
    return jsonify(spend_protocol_mod.spec(advertised_url()))


@app.route("/.well-known/command-radiation.json")
def well_known_command_radiation():
    return jsonify(command_radiation_mod.spec(advertised_url()))


@app.route("/.well-known/license-fuse.json")
def well_known_license_fuse():
    spec = license_fuse_mod.spec(advertised_url())
    spec["counterpart"] = counterpart_mod.spec(advertised_url())
    return jsonify(spec)


@app.route("/.well-known/restraint.json")
def well_known_restraint():
    return jsonify(restraint_mod.inventory(advertised_url()))


@app.route("/scanner")
def scanner_page():
    return render_template(
        "scanner.html",
        public_url=advertised_url(),
        protocol=spend_protocol_mod.spec(advertised_url()),
    )


@app.route("/uplink")
def uplink_page():
    return render_template(
        "uplink.html",
        public_url=advertised_url(),
        protocol=command_radiation_mod.spec(advertised_url()),
    )


@app.route("/.well-known/exclusion.json")
def well_known_exclusion():
    job_id = (request.args.get("job_id") or "").strip()
    return jsonify(exclusion_mod.prove(job_id))


@app.route("/.well-known/evidence-consistency.json")
def well_known_evidence_consistency():
    try:
        old_size = int(request.args.get("old_size") or 0)
    except ValueError:
        old_size = 0
    rows = db.list_bind_events_chronological()
    leaves = evidence_log_mod.log_from_rows(rows)
    proof = evidence_log_mod.consistency_proof(old_size, leaves)
    proof["tree_head"] = evidence_log_mod.signed_tree_head(leaves)
    return jsonify(proof)


@app.route("/.well-known/evidence-leaves.json")
def well_known_evidence_leaves():
    rows = db.list_bind_events_chronological()
    leaves = evidence_log_mod.log_from_rows(rows)
    return jsonify(
        {
            "spec": "gate-evidence-leaves-v1",
            "tree_size": len(leaves),
            "receipt_hashes": leaves,
            "root_hash": evidence_log_mod.merkle_root(leaves),
            "note": "Hashes only. No PII. Recompute merkle root and compare to evidence-head.json.",
        }
    )


@app.route("/capture")
def capture_page():
    return render_template("capture.html", public_url=advertised_url())


def _public_bind_events(limit: int = 48) -> list:
    return db.list_bind_events(None, limit=limit)


@app.route("/.well-known/mass.json")
def well_known_mass():
    return jsonify(liturgy_mod.stranger_mass(advertised_url(), _public_bind_events()))


@app.route("/.well-known/relics.json")
def well_known_relics():
    return jsonify(liturgy_mod.relics_manifest(advertised_url(), _public_bind_events()))


@app.route("/mass")
def mass_page():
    events = _public_bind_events()
    mass = liturgy_mod.stranger_mass(advertised_url(), events)
    relics = liturgy_mod.relics_manifest(advertised_url(), events)
    return render_template("mass.html", mass=mass, relics=relics, public_url=advertised_url())


@app.route("/refusal")
def refusal_page():
    return render_template(
        "refusal.html",
        public_url=advertised_url(),
        refusal_price=REFUSAL_PRICE_LABEL,
        bind_room_price=BIND_ROOM_PRICE_LABEL,
        stripe_refusal=bool(STRIPE_REFUSAL_PRICE_ID or GATE_DEV_MODE),
        contact_email=CONTACT_EMAIL,
    )


@app.route("/refusal/certificate.schema.json")
def refusal_certificate_schema():
    return jsonify(liturgy_mod.refusal_certificate_schema())


@app.route("/refusal/checkout", methods=["POST"])
def refusal_checkout():
    email = (request.form.get("email") or "").strip()
    agent_name = (request.form.get("agent_name") or "").strip()[:128]
    if not EMAIL_RE.match(email):
        flash("Enter a valid email.", "error")
        return redirect(url_for("refusal_page"))
    if not agent_name:
        flash("Name the agent we refuse to build.", "error")
        return redirect(url_for("refusal_page"))
    if GATE_DEV_MODE:
        fake_session = f"dev_{uuid.uuid4().hex}"
        db.create_install_order(email, fake_session, REFUSAL_PRICE_CENTS, product="refusal")
        db.mark_install_paid(fake_session)
        notify.money(
            "Refusal booked (dev)",
            f"{email} refused agent {agent_name!r} — {REFUSAL_PRICE_LABEL}",
            {"email": email, "agent_name": agent_name, "session": fake_session},
        )
        return redirect(url_for("install_success", session_id=fake_session))
    if not stripe.api_key or not STRIPE_REFUSAL_PRICE_ID:
        flash(f"Checkout not configured. Email {CONTACT_EMAIL} with subject Refusal SKU.", "error")
        return redirect(url_for("refusal_page"))
    checkout = stripe.checkout.Session.create(
        mode="payment",
        customer_email=email,
        line_items=[{"price": STRIPE_REFUSAL_PRICE_ID, "quantity": 1}],
        success_url=f"{advertised_url()}/install/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{advertised_url()}/refusal?canceled=1",
        metadata={"product": "refusal", "contact_email": email, "agent_name": agent_name},
    )
    db.create_install_order(email, checkout.id, REFUSAL_PRICE_CENTS, product="refusal")
    return redirect(checkout.url, code=303)


@app.route("/.well-known/tattoo.json")
def well_known_tattoo():
    return jsonify(liturgy_mod.weld_tattoo_manifest(advertised_url()))


@app.route("/tattoo")
def tattoo_page():
    return render_template(
        "tattoo.html",
        public_url=advertised_url(),
        install_price=INSTALL_PRICE_LABEL,
    )


def _mcp_call_tool(name: str, arguments: dict):
    """MCP tools: metered if a key is present, else public demo fuses only."""
    row = authenticate_api_key()
    keyed = row is not None
    if keyed:
        usage = db.get_usage(row["account_id"])
        if usage["hops"] >= db.hop_limit(row["plan"]):
            return {
                "error": {
                    "type": "payment_required",
                    "code": "hop_limit_exceeded",
                    "operator_url": f"{advertised_url()}/operator",
                    "economics_url": f"{advertised_url()}/pricing",
                    "message": "Lab hop budget exhausted. Production is the weld — not a Pro plan.",
                }
            }
    else:
        ok, msg = demo_limit.allow_demo(request)
        if not ok:
            return {"error": {"code": "rate_limited", "message": msg}}
    if name == "fuse_lookup":
        fuse_id = (arguments.get("fuse_id") or "").strip()
        if not fuse_id:
            return {"error": {"code": "fuse_id_required"}}
        if not keyed and not demo_limit.validate_demo_fuse(fuse_id):
            return {"error": {"code": "demo_fuse_only", "message": "Public demo fuses only. Production is a weld at /operator — not a signup upsell."}}
        data, status, _ = velaru_fuse(
            "GET", "/api/v1/fuse/lookup", fuse_id=fuse_id, params={"fuse_id": fuse_id}
        )
        if isinstance(data, dict):
            data["http_status"] = status
        if keyed:
            db.increment_usage(row["account_id"], "hops")
        return data
    if name == "fuse_hop":
        fuse_id = (arguments.get("fuse_id") or "").strip()
        if not fuse_id:
            return {"error": {"code": "fuse_id_required"}}
        if not keyed and not demo_limit.validate_demo_fuse(fuse_id):
            return {"error": {"code": "demo_fuse_only"}}
        data, status, _ = velaru_fuse(
            "POST", "/api/v1/fuse/hop", fuse_id=fuse_id, json={"fuse_id": fuse_id}
        )
        if isinstance(data, dict):
            bound.attach(data, status, demo=not keyed)
            data["http_status"] = status
        if keyed:
            db.increment_usage(row["account_id"], "hops")
        return data
    if name == "welded_act":
        fuse_id = (arguments.get("fuse_id") or "fuse_velaru_drill").strip()
        action = (arguments.get("action") or "mcp").strip()[:128]
        if not keyed and not demo_limit.validate_demo_fuse(fuse_id):
            return {"error": {"code": "demo_fuse_only"}}
        data, status, _ = run_welded_act(fuse_id, action)
        if isinstance(data, dict):
            if not keyed:
                data["demo"] = True
                bound.attach(data, status, demo=True, closed_world=True)
            data["http_status"] = status
        if keyed:
            db.increment_usage(row["account_id"], "hops")
        return data
    if name == "pas_bind_check":
        blocked = fields.pii_error(arguments)
        if blocked:
            return blocked
        args = fields.allowlist_pas(arguments)
        data, status, _ = velaru_fuse("POST", "/pas/v1/bind-check/demo", json=args)
        if isinstance(data, dict):
            bound.attach(data, status)
            data["http_status"] = status
        if keyed:
            db.increment_usage(row["account_id"], "hops")
        return data
    if name == "policycenter_pre_bind":
        blocked = fields.pii_error(arguments)
        if blocked:
            return blocked
        args = fields.allowlist_pas(arguments)
        fuse_id = (args.get("fuse_id") or "").strip()
        if not fuse_id:
            return {"error": {"code": "fuse_id_required"}}
        if not keyed and not demo_limit.validate_demo_fuse(fuse_id):
            return {"error": {"code": "demo_fuse_only"}}
        args["fuse_id"] = fuse_id
        data, status, _ = run_policycenter_pre_bind(
            args, account_id=row["account_id"] if keyed else None
        )
        if isinstance(data, dict):
            data["http_status"] = status
        if keyed:
            db.increment_usage(row["account_id"], "hops")
        return data
    if name == "mga_authority":
        blocked = fields.pii_error(arguments)
        if blocked:
            return blocked
        args = fields.allowlist_pas(arguments)
        fuse_id = (args.get("fuse_id") or "").strip()
        if not fuse_id:
            return {"error": {"code": "fuse_id_required"}}
        if not keyed and not demo_limit.validate_demo_fuse(fuse_id):
            return {"error": {"code": "demo_fuse_only"}}
        args["fuse_id"] = fuse_id
        data, status, _ = run_mga_authority(args, account_id=row["account_id"] if keyed else None)
        if isinstance(data, dict):
            data["http_status"] = status
        if keyed:
            db.increment_usage(row["account_id"], "hops")
        return data
    return {"error": {"code": "unknown_tool"}}


@app.route("/mcp", methods=["GET", "POST", "DELETE", "OPTIONS"])
def mcp_endpoint():
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, DELETE, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = (
            "Authorization, Content-Type, Mcp-Session-Id, Accept, X-Gate-Key"
        )
        return resp
    if request.method == "DELETE":
        return "", 204
    if request.method == "GET":
        # Spec allows SSE GET. We are POST-primary; advertise the endpoint.
        body = "event: endpoint\ndata: /mcp\n\n"
        return body, 200, {"Content-Type": "text/event-stream", "Cache-Control": "no-cache"}

    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}}), 400

    def _dispatch(msg):
        return mcp_server.handle_message(
            msg, public_url=advertised_url(), call_tool=_mcp_call_tool
        )

    session_id = request.headers.get("Mcp-Session-Id") or mcp_server.new_session_id()

    if isinstance(payload, list):
        out = []
        status = 200
        for msg in payload:
            body, st = _dispatch(msg)
            if body is not None:
                out.append(body)
            if st > status:
                status = st
        resp = make_response(jsonify(out), 202 if not out else status)
    else:
        body, status = _dispatch(payload)
        if body is None:
            resp = make_response("", 202)
        else:
            resp = make_response(jsonify(body), status)

    resp.headers["Mcp-Session-Id"] = session_id
    resp.headers["Access-Control-Expose-Headers"] = "Mcp-Session-Id"
    return resp


LISTING_FILES = {
    "kong-mcp.yaml": lambda: listings_mod.kong_mcp_yaml(advertised_url()),
    "truefoundry-mcp.yaml": lambda: listings_mod.truefoundry_mcp_yaml(advertised_url()),
    "aws-agentcore.json": lambda: listings_mod.aws_agentcore_json(advertised_url()),
    "guidewire-partnerconnect.json": lambda: listings_mod.guidewire_packet(advertised_url(), CONTACT_EMAIL),
    "duckcreek-partner.json": lambda: listings_mod.duckcreek_packet(advertised_url(), CONTACT_EMAIL),
    "wrangler.toml": lambda: listings_mod.wrangler_toml(advertised_url()),
    "wrangler-bind.toml": lambda: listings_mod.wrangler_bind_toml(advertised_url()),
    "control-not-model.json": lambda: listings_mod.control_not_model(advertised_url(), CONTACT_EMAIL),
    "operator.json": lambda: operator_mod.manifest(advertised_url(), CONTACT_EMAIL),
    "register.json": lambda: register_mod.manifest(advertised_url(), CONTACT_EMAIL),
}

LISTING_STATIC = {
    "cloudflare-worker.js": "application/javascript; charset=utf-8",
    "cloudflare-worker-bind.js": "application/javascript; charset=utf-8",
    "guidewire-gosu-prebind.gs": "text/plain; charset=utf-8",
    "guidewire-renewal-prebind.gs": "text/plain; charset=utf-8",
}


@app.route("/listings/<name>")
def listing_file(name):
    if name in LISTING_STATIC:
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(here, name)
        if not os.path.isfile(path):
            abort(404)
        with open(path, encoding="utf-8") as f:
            return f.read(), 200, {"Content-Type": LISTING_STATIC[name]}
    if name not in LISTING_FILES:
        abort(404)
    payload = LISTING_FILES[name]()
    if name.endswith(".json"):
        return jsonify(payload)
    ctype = "text/yaml; charset=utf-8" if name.endswith(".yaml") else "text/plain; charset=utf-8"
    return payload, 200, {"Content-Type": ctype}


@app.route("/docs")
def docs():
    return render_template(
        "docs.html",
        public_url=advertised_url(),
        velaru_base=VELARU_BASE,
    )


@app.route("/pricing")
def pricing():
    return render_template(
        "pricing.html",
        public_url=advertised_url(),
        pro_price=PRO_PRICE_LABEL,
        install_price=INSTALL_PRICE_LABEL,
        weld_price=WELD_PRICE_LABEL,
        floor_price=FLOOR_PRICE_LABEL,
        install_slots=db.install_slots_remaining(),
        stripe_publishable=STRIPE_PUBLISHABLE_KEY,
    )


@app.route("/install")
def install():
    slots = db.install_slots_remaining()
    return render_template(
        "install.html",
        public_url=advertised_url(),
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
        db.create_install_order(email, fake_session, INSTALL_PRICE_CENTS, product="install_sprint")
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
        success_url=f"{advertised_url()}/install/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{advertised_url()}/install?canceled=1",
        metadata={"product": "install_sprint", "contact_email": email},
    )
    db.create_install_order(email, checkout.id, INSTALL_PRICE_CENTS, product="install_sprint")
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


@app.route("/bind-room")
def bind_room():
    return render_template(
        "bind_room.html",
        public_url=advertised_url(),
        bind_room_price=BIND_ROOM_PRICE_LABEL,
        install_price=INSTALL_PRICE_LABEL,
        stripe_bind_room=bool(STRIPE_BIND_ROOM_PRICE_ID or GATE_DEV_MODE),
        contact_email=CONTACT_EMAIL,
    )


@app.route("/bind-room/officer-pack.json")
def bind_room_officer_pack():
    return jsonify(bind_room_mod.officer_pack(advertised_url(), CONTACT_EMAIL))


@app.route("/bind-room/appendix.schema.json")
def bind_room_appendix_schema():
    return jsonify(bind_room_mod.appendix_schema())


@app.route("/bind-room/exhibit-c-hitl.json")
def exhibit_c_hitl():
    return jsonify(bind_room_mod.exhibit_c_hitl(advertised_url()))


@app.route("/bind-room/checkout", methods=["POST"])
def bind_room_checkout():
    email = (request.form.get("email") or "").strip()
    if not EMAIL_RE.match(email):
        flash("Enter a valid email.", "error")
        return redirect(url_for("bind_room"))
    if GATE_DEV_MODE:
        fake_session = f"dev_{uuid.uuid4().hex}"
        db.create_install_order(email, fake_session, BIND_ROOM_PRICE_CENTS, product="bind_room")
        db.mark_install_paid(fake_session)
        notify.money(
            "Bind Room booked (dev)",
            f"{email} paid {BIND_ROOM_PRICE_LABEL}",
            {"email": email, "session": fake_session},
        )
        return redirect(url_for("install_success", session_id=fake_session))
    if not stripe.api_key or not STRIPE_BIND_ROOM_PRICE_ID:
        flash(f"Checkout not configured. Email {CONTACT_EMAIL} with subject Bind Room.", "error")
        return redirect(url_for("bind_room"))
    checkout = stripe.checkout.Session.create(
        mode="payment",
        customer_email=email,
        line_items=[{"price": STRIPE_BIND_ROOM_PRICE_ID, "quantity": 1}],
        success_url=f"{advertised_url()}/install/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{advertised_url()}/bind-room?canceled=1",
        metadata={"product": "bind_room", "contact_email": email},
    )
    db.create_install_order(email, checkout.id, BIND_ROOM_PRICE_CENTS, product="bind_room")
    return redirect(checkout.url, code=303)


def _operator_stripe_ready() -> bool:
    return bool(stripe.api_key and STRIPE_WELD_PRICE_ID)


@app.route("/operator")
def operator_page():
    return render_template(
        "operator.html",
        public_url=advertised_url(),
        weld_price=WELD_PRICE_LABEL,
        floor_price=FLOOR_PRICE_LABEL,
        stripe_operator=bool(_operator_stripe_ready() or GATE_DEV_MODE),
        stripe_floor=bool(STRIPE_FLOOR_PRICE_ID or GATE_DEV_MODE),
        contact_email=CONTACT_EMAIL,
        first_weld=science_pri_mod.FIRST_WELD,
        their_production=False,
    )


@app.route("/operator/checkout", methods=["POST"])
def operator_checkout():
    email = (request.form.get("email") or "").strip()
    write_kind = (request.form.get("write") or "").strip()
    include_floor = (request.form.get("include_floor") or "1").strip() == "1"
    if not EMAIL_RE.match(email):
        flash("Enter a valid work email.", "error")
        return redirect(url_for("operator_page"))
    if write_kind not in OPERATOR_WRITES:
        flash("Pick one write: withdraw or bind-only.", "error")
        return redirect(url_for("operator_page"))
    if not include_floor:
        flash("Weld requires monthly management. See the fee schedule.", "error")
        return redirect(url_for("operator_page"))
    if not (STRIPE_FLOOR_PRICE_ID or GATE_DEV_MODE):
        flash("Management checkout is not configured yet. Email us — weld requires management.", "error")
        return redirect(url_for("operator_page"))

    # DTCC-style immovability for ops: avoid duplicate checkout submissions.
    idempotency_key = (request.form.get("idempotency_key") or request.headers.get("Idempotency-Key") or "").strip()[:128]
    request_fingerprint = None
    if idempotency_key:
        import hashlib

        normalized_email = email.lower().strip()
        request_fingerprint = hashlib.sha256(
            f"{normalized_email}|{write_kind}|{int(include_floor)}|operator_weld_floor".encode("utf-8")
        ).hexdigest()
        existing = db.get_idempotency_record("operator_weld_floor", idempotency_key)
        if existing:
            if existing.get("request_fingerprint") != request_fingerprint:
                flash("Idempotency key reused with a different request.", "error")
                return redirect(url_for("operator_page"))
            if existing.get("redirect_url"):
                return redirect(existing["redirect_url"])
            # Fallback: safest is operator page.
            return redirect(url_for("operator_page"))

    product = "operator_weld_floor"
    amount = WELD_PRICE_CENTS + FLOOR_PRICE_CENTS
    if GATE_DEV_MODE:
        fake_session = f"dev_{uuid.uuid4().hex}"
        install_order_id = db.create_install_order(email, fake_session, amount, product=product)
        db.mark_install_paid(fake_session)
        notify.money(
            "Operator booked (dev)",
            f"{email} {product} write={write_kind} {WELD_PRICE_LABEL} + {FLOOR_PRICE_LABEL} management",
            {"email": email, "write": write_kind, "session": fake_session},
        )
        redirect_url = url_for("install_success", session_id=fake_session)
        if idempotency_key and request_fingerprint:
            db.create_idempotency_record(
                scope="operator_weld_floor",
                idempotency_key=idempotency_key,
                request_fingerprint=request_fingerprint,
                redirect_url=redirect_url,
                install_order_id=install_order_id,
            )
        return redirect(redirect_url)
    if not _operator_stripe_ready():
        flash(f"Checkout not configured. Email {CONTACT_EMAIL} with subject Operator weld.", "error")
        return redirect(url_for("operator_page"))
    line_items = [{"price": STRIPE_WELD_PRICE_ID, "quantity": 1}, {"price": STRIPE_FLOOR_PRICE_ID, "quantity": 1}]
    session_kwargs = {
        "mode": "subscription",
        "customer_email": email,
        "line_items": line_items,
        "success_url": f"{advertised_url()}/install/success?session_id={{CHECKOUT_SESSION_ID}}",
        "cancel_url": f"{advertised_url()}/operator?canceled=1",
        "metadata": {
            "product": product,
            "contact_email": email,
            "write": write_kind,
        },
        "subscription_data": {
            "metadata": {
                "product": "operator_floor",
                "contact_email": email,
                "write": write_kind,
            }
        },
    }
    checkout = stripe.checkout.Session.create(**session_kwargs)
    install_order_id = db.create_install_order(email, checkout.id, amount, product=product)
    if idempotency_key and request_fingerprint:
        db.create_idempotency_record(
            scope="operator_weld_floor",
            idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint,
            redirect_url=checkout.url,
            install_order_id=install_order_id,
        )
    return redirect(checkout.url, code=303)


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
        success_url=f"{advertised_url()}/dashboard?upgraded=1",
        cancel_url=f"{advertised_url()}/pricing?canceled=1",
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
        elif product == "bind_room":
            db.mark_install_paid(sess["id"])
            email = (sess.get("metadata") or {}).get("contact_email") or sess.get("customer_email")
            notify.money(
                "CASH — Bind Room",
                f"{BIND_ROOM_PRICE_LABEL} from {email}",
                {"email": email, "session": sess["id"]},
            )
        elif product == "refusal":
            db.mark_install_paid(sess["id"])
            email = (sess.get("metadata") or {}).get("contact_email") or sess.get("customer_email")
            agent_name = (sess.get("metadata") or {}).get("agent_name") or "unnamed"
            notify.money(
                "CASH — Refusal SKU",
                f"{REFUSAL_PRICE_LABEL} from {email} — refused {agent_name!r}",
                {"email": email, "agent_name": agent_name, "session": sess["id"]},
            )
        elif product in ("operator_weld", "operator_weld_floor"):
            db.mark_install_paid(sess["id"])
            email = (sess.get("metadata") or {}).get("contact_email") or sess.get("customer_email")
            write_kind = (sess.get("metadata") or {}).get("write") or ""
            notify.money(
                "CASH — Operator weld",
                f"{WELD_PRICE_LABEL}"
                + (f" + {FLOOR_PRICE_LABEL}" if product == "operator_weld_floor" else "")
                + f" from {email} write={write_kind}",
                {"email": email, "write": write_kind, "session": sess["id"], "product": product},
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
@app.route("/v1/ocsp")
@metered_api
def fuse_lookup():
    fuse_id = request.args.get("fuse_id", "").strip()
    if not fuse_id:
        return {"error": {"code": "fuse_id_required", "message": "fuse_id query param required"}}, 400
    return velaru_fuse("GET", "/api/v1/fuse/lookup", fuse_id=fuse_id, params={"fuse_id": fuse_id})


@app.route("/v1/fuse/hop", methods=["POST"])
@metered_api
def fuse_hop():
    body = request.get_json(silent=True) or {}
    fuse_id = (body.get("fuse_id") or "").strip()
    data, status, extra = velaru_fuse("POST", "/api/v1/fuse/hop", fuse_id=fuse_id or None, json=body)
    if isinstance(data, dict):
        bound.attach(data, status)
    return data, status, extra


@app.route("/v1/act", methods=["POST"])
@metered_api
def welded_act():
    """Closed world: the only Gate path that 'acts'. Hop first. DEAD/timeout never acts."""
    body = request.get_json(silent=True) or {}
    fuse_id = (body.get("fuse_id") or "").strip()
    action = (body.get("action") or "commit").strip()[:128]
    if not fuse_id:
        return {"error": {"code": "fuse_id_required", "message": "fuse_id required"}}, 400
    return run_welded_act(fuse_id, action)


@app.route("/v1/pas/bind-check", methods=["POST"])
@metered_api
def pas_bind_check():
    body, blocked, code = _pas_incoming()
    if blocked:
        return blocked, code
    data, status, extra = velaru_fuse("POST", "/pas/v1/bind-check/demo", json=body)
    if isinstance(data, dict):
        bound.attach(data, status)
    return data, status, extra


@app.route("/v1/pas/policycenter/pre-bind", methods=["POST"])
@metered_api
def pas_policycenter_pre_bind():
    body, blocked, code = _pas_incoming()
    if blocked:
        return blocked, code
    fuse_id = (body.get("fuse_id") or "").strip()
    if not fuse_id:
        return {"error": {"code": "fuse_id_required", "message": "fuse_id required"}}, 400
    body["fuse_id"] = fuse_id
    return run_policycenter_pre_bind(body, account_id=g.account_id)


@app.route("/v1/pas/mga-authority", methods=["POST"])
@metered_api
def pas_mga_authority():
    body, blocked, code = _pas_incoming()
    if blocked:
        return blocked, code
    fuse_id = (body.get("fuse_id") or "").strip()
    if not fuse_id:
        return {"error": {"code": "fuse_id_required", "message": "fuse_id required"}}, 400
    body["fuse_id"] = fuse_id
    return run_mga_authority(body, account_id=g.account_id)


@app.route("/v1/pas/duckcreek/pre-bind", methods=["POST"])
@metered_api
def pas_duckcreek_pre_bind():
    body, blocked, code = _pas_incoming()
    if blocked:
        return blocked, code
    fuse_id = (body.get("fuse_id") or "").strip()
    if not fuse_id:
        return {"error": {"code": "fuse_id_required", "message": "fuse_id required"}}, 400
    body["fuse_id"] = fuse_id
    return run_duckcreek_pre_bind(body, account_id=g.account_id)


@app.route("/v1/pas/bind-ticket/redeem", methods=["POST"])
@metered_api(count_usage=False)
def pas_bind_ticket_redeem():
    return _redeem_ticket_view(demo=False)


@app.route("/v1/pas/licenses/<license_id>/charge", methods=["POST"])
@metered_api(count_usage=False)
def pas_license_charge(license_id):
    return _license_charge_view(license_id, demo=False)


@app.route("/v1/pas/licenses/<license_id>/dead", methods=["POST"])
@metered_api(count_usage=False)
def pas_license_dead(license_id):
    return _license_dead_view(license_id, demo=False)


@app.route("/v1/pas/licenses/<license_id>", methods=["GET"])
@metered_api(count_usage=False)
def pas_license_snapshot(license_id):
    return _license_snapshot_view(license_id, demo=False)


@app.route("/v1/pas/bind-appendix")
@metered_api(count_usage=False)
def pas_bind_appendix():
    events = db.list_bind_events(g.account_id, limit=200)
    items = []
    for event in events:
        item = {
            "id": event["id"],
            "created_at": event["created_at"],
            "fuse_id": event["fuse_id"],
            "job_id": event["job_id"],
            "decision": event["decision"],
            "acted": event.get("acted"),
            "verify_url": event.get("verify_url"),
            "hop": event.get("hop"),
            "particular": particular.from_event(event),
        }
        items.append(item)
    return {
        "spec": "gate-bind-room-appendix-v1",
        "not_the_serff_filing": True,
        "not_a_prompt": True,
        "dated_instances": True,
        "items": items,
    }


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
    return velaru_fuse("POST", path, json=body, headers=headers)


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
        "api_base": advertised_url(),
        "velaru_base": VELARU_BASE,
    }


@app.route("/robots.txt")
def robots():
    body = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /scorecard",
            "Disallow: /proof",
            "Disallow: /runbook",
            "Disallow: /dogfood",
            "Disallow: /production-weld",
            "Disallow: /production-skin",
            "Disallow: /family",
            "Disallow: /action-os",
            "Disallow: /science",
            "Disallow: /positioning",
            "Disallow: /focus",
            "Disallow: /stack",
            "Disallow: /status",
            "Disallow: /install",
            "Disallow: /docs",
            "Disallow: /this",
            "Disallow: /bound",
            "Disallow: /only",
            "Disallow: /floor",
            "Disallow: /mass",
            "Disallow: /tattoo",
            "Disallow: /scanner",
            "Disallow: /uplink",
            "Disallow: /inhabitant",
            "Disallow: /afterward",
            "Disallow: /capture",
            "Disallow: /refusal",
            "Disallow: /signup",
            "Disallow: /login",
            "Disallow: /dashboard",
            f"Sitemap: {advertised_url()}/sitemap.xml",
            "",
        ]
    )
    return body, 200, {"Content-Type": "text/plain"}


@app.route("/sitemap.xml")
def sitemap():
    paths = [
        "/",
        "/operator",
        "/live",
        "/register",
        "/pricing",
        "/trust",
        "/privacy",
        "/terms",
        "/bind-room",
        "/start",
        "/for/operators",
        "/for/carriers",
        "/for/compliance",
        "/for/defense",
        "/for/legal",
        "/for/enterprise",
        "/.well-known/gate.json",
        "/.well-known/operator.json",
        "/.well-known/register.json",
        "/.well-known/live.json",
        "/.well-known/legal.json",
        "/openapi.json",
    ]
    urls = "".join(
        f"<url><loc>{advertised_url()}{p}</loc><changefreq>weekly</changefreq></url>" for p in paths
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'
    return xml, 200, {"Content-Type": "application/xml"}


@app.route("/llms.txt")
def llms_txt():
    lines = [
        "# Gate — Nisaba LLC",
        "",
        "> Clearance before withdraw, payout, or bind. Fail closed under uncertainty. Independent verify.",
        "",
        f"- Home: {advertised_url()}/",
        f"- Weld (checkout): {advertised_url()}/operator",
        f"- Fee schedule: {advertised_url()}/register",
        f"- Pricing: {advertised_url()}/pricing",
        f"- Trust: {advertised_url()}/trust",
        f"- Bind Room: {advertised_url()}/bind-room",
        f"- Operator invoice: {advertised_url()}/.well-known/operator.json",
        f"- Fee schedule JSON: {advertised_url()}/.well-known/register.json",
        f"- OpenAPI: {advertised_url()}/openapi.json",
        f"- Verify: https://velaru.xyz/verify",
        "",
        "Not a seat product. Not Free/Pro. Weld + path management + bps on cleared flow.",
        "their_production stays false until a recorded third-party production weld.",
        "",
    ]
    for slug, plate in audiences.all_plates().items():
        lines.append(f"- {plate['title']}: {advertised_url()}/for/{slug} — {plate['headline']}")
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
                "contact": {"email": CONTACT_EMAIL, "url": advertised_url()},
            },
            "servers": [{"url": advertised_url(), "description": "Gate API"}],
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
                "/v1/act": {"post": {"summary": "Welded closed-world act — hop first, DEAD never acts", "security": [{"BearerAuth": []}]}},
                "/v1/pas/bind-check": {"post": {"summary": "PAS bind ALLOW/BLOCK demo. fuse_id + job ids only.", "security": [{"BearerAuth": []}]}},
                "/v1/pas/policycenter/pre-bind": {
                    "post": {
                        "summary": "Hop then PolicyCenter next step: bind-only ticket, or raise Manual UW issue. bind-and-issue is not granted.",
                        "security": [{"BearerAuth": []}],
                    }
                },
                "/v1/pas/mga-authority": {
                    "post": {
                        "summary": "Delegated-authority check: hop + premium/line/state limits",
                        "security": [{"BearerAuth": []}],
                    }
                },
                "/v1/pas/duckcreek/pre-bind": {
                    "post": {"summary": "Duck Creek issue wrap — do not call issue if halt", "security": [{"BearerAuth": []}]}
                },
                "/v1/pas/bind-ticket/redeem": {
                    "post": {
                        "summary": "Consume a single-use bind ticket bound to one spend fingerprint. Stale/replay/wrong write/dead parent → HALT.",
                        "security": [{"BearerAuth": []}],
                    }
                },
                "/v1/pas/licenses/{license_id}/charge": {
                    "post": {
                        "summary": "CHARGE-only resurrection of a license parent. UNSIGNED/DEAD → LIVE. Not admin CHARGE. Not a second bind-only write.",
                        "security": [{"BearerAuth": []}],
                    }
                },
                "/v1/pas/licenses/{license_id}/dead": {
                    "post": {
                        "summary": "Blow the license parent. Outstanding tickets cannot redeem until CHARGE.",
                        "security": [{"BearerAuth": []}],
                    }
                },
                "/v1/pas/licenses/{license_id}": {
                    "get": {
                        "summary": "License parent snapshot. UNSIGNED until CHARGE. ARMED = LIVE with unredeemed children.",
                        "security": [{"BearerAuth": []}],
                    }
                },
                "/v1/pas/bind-appendix": {
                    "get": {"summary": "On-request examiner appendix: job_id + verify_url. Not the SERFF filing.", "security": [{"BearerAuth": []}]}
                },
                "/v1/ocsp": {"get": {"summary": "OCSP alias for fuse lookup — 503 halt if unreachable", "security": [{"BearerAuth": []}]}},
                "/v1/execute-gate/demo": {"post": {"summary": "PERMIT/DENY demo", "security": [{"BearerAuth": []}]}},
                "/v1/classify": {"post": {"summary": "Classify → signed receipt", "security": [{"BearerAuth": []}]}},
                "/v1/me": {"get": {"summary": "Key metadata + usage", "security": [{"BearerAuth": []}]}},
                "/demo/hop": {"post": {"summary": "Public demo hop (no key, rate limited)", "security": []}},
                "/demo/lookup": {"get": {"summary": "Public demo lookup", "security": []}},
                "/demo/act": {"post": {"summary": "Public welded act on drill fuse (no key)", "security": []}},
                "/demo/pas/bind-check": {"post": {"summary": "Public PAS BIND/BLOCK demo (no key)", "security": []}},
                "/demo/pas/policycenter/pre-bind": {"post": {"summary": "Public PolicyCenter pre-bind weld (no key)", "security": []}},
                "/demo/pas/mga-authority": {"post": {"summary": "Public MGA authority check (no key)", "security": []}},
                "/bind-room": {"get": {"summary": "Officer pack + appendix + weld — $1,750"}},
                "/register": {"get": {"summary": "Infrastructure register. Mouth on irreversible spend. Not SaaS."}},
                "/operator": {"get": {"summary": "Weld checkout. One production write. Then max(floor, 10 bps, $0.10/hop)."}},
                "/.well-known/register.json": {"get": {"summary": "Infrastructure register. Mouth + scale. Not SaaS."}},
                "/.well-known/operator.json": {"get": {"summary": "Operator invoice contract. One write. Licensed only."}},
                "/bound": {"get": {"summary": "A no that holds — narrow, enforced, provable"}},
                "/only": {"get": {"summary": "Exclusive timing — the act that never happens"}},
                "/floor": {"get": {"summary": "The floor. Unrepeatable. Not only yours. No cleverer layer."}},
                "/this": {"get": {"summary": "A particular. Name one. Let it try to spend. Not a deeper idea."}},
                "/inhabitant": {"get": {"summary": "The someone who has to live there. They did not have to ask."}},
                "/afterward": {"get": {"summary": "Including later. Missing letter is a hole, not a spared world."}},
                "/capture": {"get": {"summary": "PolicyCenter spend writes. bind-only is already Bound."}},
                "/scanner": {"get": {"summary": "Spend protocol — the scanner. One write. Fingerprint or no print."}},
                "/uplink": {"get": {"summary": "Command radiation — may this CLTU still be radiated, in this now?"}},
                "/.well-known/spend-protocol.json": {"get": {"summary": "Public spend protocol. Implementors hash the write they forward."}},
                "/.well-known/command-radiation.json": {"get": {"summary": "Public command-radiation spec. Redeem must present UTC now."}},
                "/.well-known/license-fuse.json": {"get": {"summary": "License Fuse. Parent must be LIVE. Children cannot outlive it. CHARGE-only resurrection."}},
                "/.well-known/restraint.json": {"get": {"summary": "Inventory of production nos. HALT/BLOCK, no PII, not demo."}},
                "/.well-known/commit-auth.json": {"get": {"summary": "Bind tickets, epoch lock, license fuse, exclusion proofs"}},
                "/.well-known/exclusion.json": {"get": {"summary": "Sorted Merkle proof this job has no redeemed spend leaf"}},
                "/.well-known/bound-answer.json": {"get": {"summary": "Bound-answer manifesto"}},
                "/.well-known/exclusive-timing.json": {"get": {"summary": "Exclusive-timing manifesto. Receipt is not the product."}},
                "/.well-known/floor.json": {"get": {"summary": "The floor. cleverer_layer is null."}},
                "/.well-known/particular.json": {"get": {"summary": "Particular manifesto. An event, not a question."}},
                "/.well-known/capture.json": {"get": {"summary": "Complete Cloud API spend map. bind-only leak."}},
                "/mcp": {"post": {"summary": "Streamable HTTP MCP — Kong / TrueFoundry / AWS AgentCore", "security": []}},
                "/health": {"get": {"summary": "Service health. 503 if production still advertises localhost."}},
                "/.well-known/gate.json": {"get": {"summary": "Agent discovery manifest"}},
                "/.well-known/mcp.json": {"get": {"summary": "MCP tool discovery"}},
                "/.well-known/x402.json": {"get": {"summary": "x402 resource catalog"}},
                "/.well-known/listings.json": {"get": {"summary": "Date-all listing map (MCP, CF, x402, Guidewire, Duck Creek)"}},
            },
        }
    )


if __name__ == "__main__":
    init()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")), debug=GATE_DEV_MODE)
