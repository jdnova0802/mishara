"""OpenAPI for agent discovery — x402 payables + Gate law stack."""


def _post(summary: str, *, description: str = "", paid: bool = False) -> dict:
    op = {
        "summary": summary,
        "responses": {
            "200": {"description": "OK"},
            "400": {"description": "Bad request / fail closed"},
        },
    }
    if description:
        op["description"] = description
    if paid:
        op["security"] = [{"BearerAuth": []}]
        op["responses"]["401"] = {"description": "API key required"}
        op["responses"]["402"] = {"description": "Hop limit / payment required"}
    return {"post": op}


def _get(summary: str, *, description: str = "") -> dict:
    op = {
        "summary": summary,
        "responses": {"200": {"description": "OK"}, "404": {"description": "Not found"}},
    }
    if description:
        op["description"] = description
    return {"get": op}


def spec(public_url: str, *, contact_email: str, payto: str | None) -> dict:
    base = (public_url or "").rstrip("/")
    x402_live = bool(payto)
    if x402_live:
        prefinal_post = {
            "summary": "Pre-finality GO/NO-GO + signed JWT receipt",
            "description": (
                "Rail-agnostic clearance before irreversible commit. "
                "Pay $0.002 USDC on Base via x402, or use Gate API key."
            ),
            "x-payment-info": {
                "protocols": ["x402"],
                "price": {"mode": "fixed", "currency": "USDC", "amount": "0.002"},
            },
            "responses": {
                "200": {"description": "GO + signed receipt JWT"},
                "402": {"description": "x402 USDC payment required on Base"},
                "403": {"description": "NO_GO — fail closed"},
            },
        }
        wire_get = {
            "summary": "Paid x402 deploy wire bundle ($497 USDC)",
            "description": (
                "Instant delivery after USDC pay: Cloudflare worker, wrangler, "
                "openapi pattern, bazaar listing checklist."
            ),
            "x-payment-info": {
                "protocols": ["x402"],
                "price": {"mode": "fixed", "currency": "USDC", "amount": "497.00"},
            },
            "responses": {
                "200": {"description": "Paid wire bundle JSON"},
                "402": {"description": "x402 USDC payment required on Base"},
            },
        }
        x402_note = "x402 payto configured — USDC prices are live."
    else:
        prefinal_post = {
            "summary": "Pre-finality GO/NO-GO + signed JWT receipt",
            "description": (
                "Rail-agnostic clearance before irreversible commit. "
                "x402 USDC is NOT configured on this host — use Gate API key "
                "or POST /demo/prefinality/evaluate. Do not send USDC."
            ),
            "responses": {
                "200": {"description": "GO + signed receipt JWT"},
                "401": {"description": "API key required when x402 offline"},
                "403": {"description": "NO_GO — fail closed"},
            },
        }
        wire_get = {
            "summary": "x402 wire bundle (OFFLINE until payto configured)",
            "description": (
                "Paid USDC wire is offline while GATE_X402_PAYTO is unset. "
                "Use Stripe /pricing or wait for payto."
            ),
            "responses": {
                "503": {"description": "x402 payto not configured"},
                "402": {"description": "Would require x402 when configured"},
            },
        }
        x402_note = (
            "x402.configured is false until GATE_X402_PAYTO is set. "
            "Paid USDC prices are not collectible; use API key or free demos."
        )

    paths = {
        "/v1/prefinality/evaluate": {"post": prefinal_post},
        "/demo/prefinality/evaluate": {
            "post": {
                "summary": "Free pre-finality demo (no payment)",
                "security": [],
                "responses": {"200": {"description": "Evaluate result"}},
            }
        },
        "/api/x402/wire": {"get": wire_get},
        # Law stack
        "/v1/right-to-act/evaluate": _post(
            "Right-to-Act evaluate",
            description="EXIST / NONEXIST / HOLD before effectuation.",
        ),
        "/demo/right-to-act/evaluate": _post("Right-to-Act demo"),
        "/v1/right-to-act/verify": _post("Right-to-Act verify receipt"),
        "/v1/right-to-act/burn": _post("Right-to-Act burn ticket"),
        "/v1/mandate/issue": _post("Issue human-rooted mandate"),
        "/v1/mandate/reconstruct": _post("Live reconstruct mandate"),
        "/v1/mandate/die": _post("Mint death certificate"),
        "/v1/mandate/death/verify": _post("Verify death certificate"),
        "/v1/mandate/deaths/export": {
            **_get("Export mortality federation"),
            **_post("Export mortality federation (POST)"),
        },
        "/v1/mandate/deaths/ingest": _post("Ingest mortality federation"),
        "/v1/sinks": _get("List sink registry"),
        "/v1/sinks/register": _post("Register sink"),
        "/v1/finder/search": {
            **_get("Finder search"),
            **_post("Finder search (POST)"),
        },
        "/v1/admittance/admit": _post(
            "Admittance — ADMITTED|REFUSED|HALTED|DEAD",
            description="Three civilizations compressed into one verb.",
        ),
        "/demo/admittance/admit": _post("Admittance demo"),
        "/v1/subject/clear": _post("Subject clearance (meterable)"),
        "/v1/subject/refuse": _post("Subject refusal (meterable)"),
        "/v1/subject/verify": _post("Subject refusal verify (meterable)"),
        "/v1/physical/evaluate": _post(
            "Physical Prefinality evaluate",
            description="Absolute physical → PARK without living root + mandate + subject clear. SKU gate.physical.park.",
        ),
        "/demo/physical/evaluate": _post("Physical Prefinality demo"),
        "/v1/physical/verify": _post("Verify park ticket (meterable)"),
        "/v1/physical/parks": _get("List recent parks"),
        # Fuse / PAS / act (also in openapi.full.json)
        "/v1/fuse/lookup": _get("Fuse existence lookup", description="Metered. API key."),
        "/v1/fuse/hop": _post("Pre-exec fuse hop — DEAD fails closed", paid=True),
        "/v1/act": _post("Welded closed-world act — hop first, DEAD never acts", paid=True),
        "/v1/pas/bind-check": _post("PAS bind ALLOW/BLOCK. fuse_id + job ids only.", paid=True),
        "/v1/pas/bind-ticket/redeem": _post("Redeem PAS bind ticket", paid=True),
        "/v1/pas/mga-authority": _post("MGA authority check", paid=True),
        "/v1/pas/policycenter/pre-bind": _post("PolicyCenter pre-bind clearance", paid=True),
        "/v1/canary/bypass": _post("Canary bypass probe", paid=True),
        "/demo/act": _post("Public act demo (no key)"),
        "/demo/hop": _post("Public hop demo (no key)"),
        "/demo/pas/bind-check": _post("Public PAS BIND/BLOCK demo (no key)"),
        "/.well-known/gate.json": _get("Agent discovery manifest"),
        "/.well-known/physical-prefinality.json": _get("Physical Prefinality manifest"),
        "/.well-known/subject.json": _get("Subject Sovereignty manifest"),
        "/.well-known/admittance.json": _get("Admittance manifest"),
        "/.well-known/right-to-act.json": _get("Right-to-Act manifest"),
        "/.well-known/mandate.json": _get("Mandate + mortality manifest"),
        "/.well-known/sinks.json": _get("Sink registry manifest"),
        "/.well-known/opportunities.json": _get("Audience opportunity surfaces"),
        "/health": _get("Health + durability flags"),
    }
    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Gate API",
            "version": "1.2.0",
            "description": (
                "Authority for consequence before irreversible writes. "
                "Law stack + fuse hop + PAS + x402 payables. Fail closed under uncertainty."
            ),
            "contact": {"email": contact_email, "url": base},
        },
        "servers": [{"url": base, "description": "Gate API"}],
        "x-discovery": {
            "ownershipProofs": [payto] if payto else [],
            "gate": f"{base}/.well-known/gate.json",
            "prefinality": f"{base}/.well-known/prefinality.json",
            "physical_park_sku": "gate.physical.park",
            "x402_configured": x402_live,
            "note": (
                "openapi.json includes law + fuse/PAS paths. "
                "openapi.full.json remains the broader catalog. "
                + x402_note
            ),
        },
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "description": "gate_sk_live_... from dashboard",
                }
            }
        },
        "paths": paths,
    }
