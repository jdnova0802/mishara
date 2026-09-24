"""Gate finds its own bugs — SCVD preflight + mouth verdicts, not page 200s.

SCVD's free preflight (POST https://scvd.store/api/preflight/v1) GETs a URL
once and names checks: status-402, payment-required-header, x402-version,
accepts, bazaar-extension. This module is that battery pointed at ourselves,
plus one-word mouth verdicts. Run in CI before ship; run against live after
deploy. A 200 on /go would have missed tonight's 401-vs-402 miss.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import uuid
from typing import Any, Callable
from urllib.parse import urljoin

SPEC = "gate-internal-verify-v1"
SCVD_PREFLIGHT = "https://scvd.store/api/preflight/v1"
PREFLIGHT_VERSION = "v1"

# Same field set SCVD's till refuses to sign without (src/services/preflight.ts).
ACCEPT_REQUIRED_FIELDS = ("scheme", "network", "amount", "asset", "payTo")
KNOWN_TESTNETS = {
    "eip155:84532": "Base Sepolia",
    "eip155:11155111": "Ethereum Sepolia",
}
MAINNET = "eip155:8453"

# Corrections that were wrong once this night — pin them.
PAYTO_ENVS = (
    "GATE_X402_PAYTO",
    "GATE_X402_PAY_TO",
    "GATE_X402_DEMO_PAYTO",
)
PUCT = {
    "batch_zero_pgrr_145": "59142",
    "crusoe_ensign_sb6_net_metering": "59220",
}
CITATIONS = {
    "scenario_3": "FIN-2016-A003",
    "admt": "11 CCR § 7200(b)",
    "stair": "IBC sensor-release of electrically locked egress doors",
    "stair_source": "https://up.codes/s/sensor-release-of-electrically-locked-egress-doors",
}

MOUTH_PAGES = (
    "/clear",
    "/seal",
    "/go",
    "/never",
    "/positive-clear",
    "/scenario-3",
    "/uapa-seal",
    "/admt",
    "/trusted-contact",
    "/stair",
)

GO_OK = {
    "rail": "x402",
    "transfer": {
        "amount": "0.002",
        "currency": "USDC",
        "counterparty": "0x0000000000000000000000000000000000000001",
    },
    "mandate": {"agent_id": "internal-verify", "max_amount": "1.00"},
}
GO_NO = {
    "rail": "x402",
    "transfer": {
        "amount": "5.00",
        "currency": "USDC",
        "counterparty": "0x0000000000000000000000000000000000000001",
    },
    "mandate": {"agent_id": "internal-verify", "max_amount": "1.00"},
}


def _header(headers: Any, name: str) -> str | None:
    if headers is None:
        return None
    want = name.lower()
    if hasattr(headers, "get"):
        for key in (name, name.upper(), name.title(), "Payment-Required"):
            val = headers.get(key)
            if val:
                return val
        try:
            items = headers.items()
        except Exception:
            items = []
        for k, v in items:
            if str(k).lower() == want and v:
                return v
    if isinstance(headers, dict):
        for k, v in headers.items():
            if str(k).lower() == want and v:
                return v
    return None


def run_scvd_checks(*, status: int, headers: Any, body_over_limit: bool = False) -> dict[str, Any]:
    """Port of SCVD runChecks. Names must match their crawler."""
    checks: list[dict[str, Any]] = []
    advisories: list[dict[str, str]] = []

    if 300 <= int(status) < 400:
        checks.append(
            {
                "name": "status-402",
                "ok": False,
                "detail": f"answered {status}: a redirect. Payment clients will not follow it.",
            }
        )
        return _scvd_out(checks, advisories)

    if int(status) == 402:
        checks.append({"name": "status-402", "ok": True, "detail": "answered 402 Payment Required"})
    else:
        extra = (
            "A 200 here is the 'listed but functionally absent' shape."
            if int(status) == 200
            else "A buyer's payment client keys the entire flow off a 402."
        )
        checks.append(
            {
                "name": "status-402",
                "ok": False,
                "detail": f"answered {status} instead of 402. {extra}",
            }
        )
        return _scvd_out(checks, advisories)

    header = _header(headers, "PAYMENT-REQUIRED")
    if not header:
        checks.append(
            {
                "name": "payment-required-header",
                "ok": False,
                "detail": (
                    "the 402 carries no PAYMENT-REQUIRED header. x402 v2 clients "
                    "read the challenge from that header (base64 JSON), not from the body."
                ),
            }
        )
        return _scvd_out(checks, advisories)

    try:
        raw = header if isinstance(header, str) else header.decode("ascii")
        challenge = json.loads(base64.b64decode(raw).decode("utf-8"))
        if not isinstance(challenge, dict):
            raise ValueError("challenge not an object")
        checks.append(
            {
                "name": "payment-required-header",
                "ok": True,
                "detail": "PAYMENT-REQUIRED header present, base64 JSON parses",
            }
        )
    except Exception:
        checks.append(
            {
                "name": "payment-required-header",
                "ok": False,
                "detail": "PAYMENT-REQUIRED header present but not base64-encoded JSON.",
            }
        )
        return _scvd_out(checks, advisories)

    version_ok = challenge.get("x402Version") == 2
    checks.append(
        {
            "name": "x402-version",
            "ok": version_ok,
            "detail": "x402Version is 2"
            if version_ok
            else f"x402Version is {challenge.get('x402Version')!r}, expected 2.",
        }
    )

    accepts = challenge.get("accepts")
    if not isinstance(accepts, list) or not accepts:
        checks.append(
            {
                "name": "accepts",
                "ok": False,
                "detail": "accepts is missing or empty — the challenge offers a buyer nothing to sign against.",
            }
        )
        return _scvd_out(checks, advisories)

    holes: list[str] = []
    for index, entry in enumerate(accepts):
        row = entry if isinstance(entry, dict) else {}
        for field in ACCEPT_REQUIRED_FIELDS:
            if not isinstance(row.get(field), str):
                holes.append(f"accepts[{index}].{field}")
    checks.append(
        {
            "name": "accepts",
            "ok": not holes,
            "detail": (
                f"{len(accepts)} accepts entries, each carrying "
                + ", ".join(ACCEPT_REQUIRED_FIELDS)
                if not holes
                else "missing or non-string: " + ", ".join(holes)
            ),
        }
    )

    for entry in accepts:
        row = entry if isinstance(entry, dict) else {}
        scheme = str(row.get("scheme") or "")
        if scheme and scheme != "exact":
            advisories.append(
                {
                    "name": "nonstandard-scheme",
                    "detail": f'accepts offers scheme "{scheme}" rather than "exact".',
                }
            )
        network = str(row.get("network") or "")
        testnet = KNOWN_TESTNETS.get(network)
        if testnet:
            advisories.append(
                {
                    "name": "testnet-network",
                    "detail": f"accepts offers {network} ({testnet}). Base mainnet is {MAINNET}.",
                }
            )
        amount = str(row.get("amount") or "")
        if "." in amount:
            advisories.append(
                {
                    "name": "amount-not-atomic",
                    "detail": f'accepts amount "{amount}" contains a decimal point.',
                }
            )

    extensions = challenge.get("extensions") if isinstance(challenge.get("extensions"), dict) else {}
    if "bazaar" in extensions:
        bazaar = extensions.get("bazaar")
        info = bazaar.get("info") if isinstance(bazaar, dict) else None
        checks.append(
            {
                "name": "bazaar-extension",
                "ok": isinstance(info, dict),
                "detail": (
                    "extensions.bazaar carries a parseable info block"
                    if isinstance(info, dict)
                    else "extensions.bazaar is declared but carries no parseable info block."
                ),
            }
        )
    else:
        advisories.append(
            {
                "name": "no-bazaar-extension",
                "detail": "no extensions.bazaar block. Not a defect — directories that ingest bazaar will miss this URL.",
            }
        )

    if body_over_limit:
        advisories.append({"name": "large-body", "detail": "402 body exceeded the probe size ceiling."})

    return _scvd_out(checks, advisories)


def _scvd_out(checks: list[dict], advisories: list[dict]) -> dict[str, Any]:
    ok = bool(checks) and all(c.get("ok") for c in checks)
    return {
        "spec": SPEC,
        "version": PREFLIGHT_VERSION,
        "source": SCVD_PREFLIGHT,
        "verdict": "ready" if ok else "not_ready",
        "checks": checks,
        "advisories": advisories,
    }


def scvd_from_flask(response) -> dict[str, Any]:
    return run_scvd_checks(status=response.status_code, headers=response.headers)


def scvd_from_requests(response) -> dict[str, Any]:
    return run_scvd_checks(status=response.status_code, headers=response.headers)


def _fail(name: str, detail: str, **extra: Any) -> dict[str, Any]:
    body = {"name": name, "ok": False, "detail": detail}
    body.update(extra)
    return body


def _ok(name: str, detail: str = "", **extra: Any) -> dict[str, Any]:
    body = {"name": name, "ok": True, "detail": detail}
    body.update(extra)
    return body


def mouth_verdicts(get: Callable, post: Callable, page: Callable) -> list[dict[str, Any]]:
    """Hit every live mouth and assert the word, not HTTP 200."""
    out: list[dict[str, Any]] = []
    for path in MOUTH_PAGES:
        r = page(path)
        code = getattr(r, "status_code", None)
        if code != 200:
            out.append(_fail(f"page{path}", f"HTTP {code}, want 200"))
        else:
            out.append(_ok(f"page{path}", "HTTP 200 (page only — verdicts below)"))

    ach = get("/v1/clear?rail=ach")
    word = (ach.get("word") if isinstance(ach, dict) else None)
    out.append(
        _ok("clear-ach", word)
        if word == "REVERSIBLE"
        else _fail("clear-ach", f"word={word!r} want REVERSIBLE")
    )
    wire = get("/v1/clear?rail=wire")
    word = (wire.get("word") if isinstance(wire, dict) else None)
    out.append(
        _ok("clear-wire", word)
        if word == "FINAL"
        else _fail("clear-wire", f"word={word!r} want FINAL")
    )

    missing = get("/v1/seal?event_id=not-a-real-event")
    word = (missing.get("word") if isinstance(missing, dict) else None)
    out.append(
        _ok("seal-missing", word)
        if word == "MISSING"
        else _fail("seal-missing", f"word={word!r} want MISSING")
    )

    go = post("/v1/go", GO_OK)
    word = (go.get("word") if isinstance(go, dict) else None)
    out.append(_ok("go-yes", word) if word == "GO" else _fail("go-yes", f"word={word!r} want GO"))
    nogo = post("/v1/go", GO_NO)
    word = (nogo.get("word") if isinstance(nogo, dict) else None)
    out.append(
        _ok("go-no", word) if word == "NO GO" else _fail("go-no", f"word={word!r} want NO GO")
    )

    never = get(f"/v1/never?job_id=pc:INTERNAL-VERIFY-{uuid.uuid4().hex[:12]}")
    word = (never.get("word") if isinstance(never, dict) else None)
    out.append(
        _ok("never-fresh", word)
        if word == "NEVER"
        else _fail("never-fresh", f"word={word!r} want NEVER")
    )

    pc = post("/v1/positive-clear", {"kind": "payroll", "authority_live": "yes"})
    word = (pc.get("word") if isinstance(pc, dict) else None)
    out.append(
        _ok("positive-clear-proceed", word)
        if word == "PROCEED"
        else _fail("positive-clear-proceed", f"word={word!r} want PROCEED")
    )
    pc_no = post("/v1/positive-clear", {"kind": "payroll", "authority_live": "no"})
    word = (pc_no.get("word") if isinstance(pc_no, dict) else None)
    out.append(
        _ok("positive-clear-no", word)
        if word == "NO"
        else _fail("positive-clear-no", f"word={word!r} want NO")
    )

    s3 = post(
        "/v1/scenario-3",
        {"known_supplier": True, "email_only": True, "new_account": True},
    )
    word = (s3.get("word") if isinstance(s3, dict) else None)
    advisory = (s3.get("advisory") if isinstance(s3, dict) else None)
    if word == "MATCHES" and advisory == CITATIONS["scenario_3"]:
        out.append(_ok("scenario-3", f"{word} {advisory}"))
    else:
        out.append(_fail("scenario-3", f"word={word!r} advisory={advisory!r}"))

    uapa = post(
        "/v1/uapa-seal",
        {
            "already_sent": "yes",
            "authorized": "yes",
            "induced": "yes",
            "rtp_native": "yes",
        },
    )
    word = (uapa.get("word") if isinstance(uapa, dict) else None)
    out.append(
        _ok("uapa-seal", word)
        if word == "REPORTABLE"
        else _fail("uapa-seal", f"word={word!r} want REPORTABLE")
    )

    admt = post(
        "/v1/admt",
        {
            "decision_class": "financial",
            "uses_admt": "yes",
            "pre_use_notice": "no",
        },
    )
    word = (admt.get("word") if isinstance(admt, dict) else None)
    cite = (admt.get("cite") if isinstance(admt, dict) else None)
    if word == "NOTICE DUE" and cite == CITATIONS["admt"]:
        out.append(_ok("admt", f"{word} {cite}"))
    else:
        out.append(_fail("admt", f"word={word!r} cite={cite!r}"))

    hold_id = f"internal-verify-hold-{uuid.uuid4().hex[:12]}"
    miss = post("/v1/trusted-contact", {"account_id": hold_id})
    word = (miss.get("word") if isinstance(miss, dict) else None)
    out.append(
        _ok("trusted-no-hold", word)
        if word == "NO HOLD"
        else _fail("trusted-no-hold", f"word={word!r} want NO HOLD")
    )
    sealed = post(
        "/v1/trusted-contact",
        {"account_id": hold_id, "action": "seal"},
    )
    word = (sealed.get("word") if isinstance(sealed, dict) else None)
    out.append(
        _ok("trusted-hold", word)
        if word == "HOLD"
        else _fail("trusted-hold", f"word={word!r} want HOLD")
    )

    stair = post("/v1/stair", {"kind": "egress_lock"})
    word = (stair.get("word") if isinstance(stair, dict) else None)
    cite = (stair.get("cite") if isinstance(stair, dict) else None)
    src = (stair.get("source") if isinstance(stair, dict) else None)
    if (
        word == "NEVER"
        and cite == CITATIONS["stair"]
        and src == CITATIONS["stair_source"]
    ):
        out.append(_ok("stair-never", word))
    else:
        out.append(_fail("stair-never", f"word={word!r} cite={cite!r} source={src!r}"))
    not_this = post("/v1/stair", {"kind": "money_or_bind"})
    word = (not_this.get("word") if isinstance(not_this, dict) else None)
    out.append(
        _ok("stair-not-this", word)
        if word == "NOT THIS"
        else _fail("stair-not-this", f"word={word!r} want NOT THIS")
    )
    return out


def flask_transport(client):
    def page(path: str):
        return client.get(path)

    def get(path: str):
        r = client.get(path)
        try:
            return r.get_json()
        except Exception:
            return {"error": "non_json", "status": r.status_code}

    def post(path: str, body: dict):
        r = client.post(path, json=body)
        try:
            return r.get_json()
        except Exception:
            return {"error": "non_json", "status": r.status_code}

    return get, post, page


def live_transport(base: str, timeout: float = 20.0):
    import requests

    root = (base or "").rstrip("/") + "/"

    def page(path: str):
        return requests.get(urljoin(root, path.lstrip("/")), timeout=timeout, allow_redirects=False)

    def get(path: str):
        r = requests.get(urljoin(root, path.lstrip("/")), timeout=timeout, allow_redirects=False)
        try:
            return r.json()
        except Exception:
            return {"error": "non_json", "status": r.status_code}

    def post(path: str, body: dict):
        r = requests.post(
            urljoin(root, path.lstrip("/")),
            json=body,
            timeout=timeout,
            allow_redirects=False,
        )
        try:
            return r.json()
        except Exception:
            return {"error": "non_json", "status": r.status_code}

    return get, post, page


def live_scvd(base: str, timeout: float = 20.0) -> dict[str, Any]:
    import requests

    url = (base or "").rstrip("/") + "/v1/prefinality/evaluate"
    r = requests.get(url, timeout=timeout, allow_redirects=False, headers={"Accept": "application/json"})
    report = scvd_from_requests(r)
    report["url"] = url
    report["http_status"] = r.status_code
    return report


def report_ok(rows: list[dict[str, Any]]) -> bool:
    return all(r.get("ok") for r in rows)


def print_report(title: str, rows: list[dict[str, Any]]) -> None:
    print(title)
    for row in rows:
        mark = "OK  " if row.get("ok") else "FAIL"
        print(f"  {mark} {row.get('name')} — {row.get('detail')}")


def run_live(base: str, *, retries: int = 8, wait: float = 20.0) -> int:
    last_err = "unreachable"
    for attempt in range(1, retries + 1):
        try:
            scvd = live_scvd(base)
            get, post, page = live_transport(base)
            mouths = mouth_verdicts(get, post, page)
            print_report("SCVD battery (GET /v1/prefinality/evaluate)", scvd.get("checks") or [])
            print(f"  verdict={scvd.get('verdict')}")
            print_report("Mouth verdicts", mouths)
            if scvd.get("verdict") == "ready" and report_ok(mouths):
                print("internal-verify: ready")
                return 0
            last_err = f"scvd={scvd.get('verdict')} mouths_fail={sum(1 for r in mouths if not r.get('ok'))}"
        except Exception as exc:
            last_err = str(exc)
        if attempt < retries:
            print(f"attempt {attempt}/{retries} not ready ({last_err}); sleep {wait}s")
            time.sleep(wait)
    print(f"internal-verify: not ready — {last_err}")
    return 1


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    live = None
    if "--live" in args:
        i = args.index("--live")
        live = args[i + 1] if i + 1 < len(args) else os.getenv("GATE_PUBLIC_URL")
    if live:
        if "localhost" in live or "127.0.0.1" in live:
            print("FAIL: live URL must not be localhost")
            return 2
        return run_live(live)
    print("usage: python internal_verify.py --live https://gate.velaru.xyz")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
