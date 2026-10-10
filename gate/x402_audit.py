"""Free x402 endpoint audit + paid wire bundle — inbound, no outreach."""
from __future__ import annotations

import hashlib
import ipaddress
import json
import os
import re
import secrets
import socket
import uuid
from typing import Any
from urllib.parse import urlparse

import requests

SPEC = "gate-x402-audit-v1"
WIRE_SPEC = "gate-x402-wire-v1"
_WIRE_PRICE_USD = "497.00"
_WIRE_PRICE_CENTS = 49700
_URL_RE = re.compile(r"^https?://", re.I)
_EVM_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
_MAX_PROBE_BYTES = 2_000_000  # cap body we parse, so a hostile target can't balloon memory


def _ssrf_allow_local() -> bool:
    """Only an explicit opt-in disables the SSRF guard (dev/test fixtures).

    Deliberately NOT tied to GATE_DEV_MODE: the test suite runs with dev mode on,
    and the guard must stay active there so its blocking is actually exercised.
    Production sets GATE_ALLOW_LOCAL=0, so the guard is always on in prod."""
    return os.getenv("GATE_ALLOW_LOCAL", "0") == "1"


def _ip_is_blocked(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local  # includes cloud metadata 169.254.169.254 / fe80::/10
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _host_is_public(host: str) -> tuple[bool, str]:
    """Resolve host and require EVERY A/AAAA address to be public and routable.

    Blocks SSRF to loopback, private, link-local (incl. the 169.254.169.254 cloud
    metadata endpoint), reserved, multicast, and unspecified ranges. A hostname
    that resolves to any blocked address is rejected whole."""
    h = (host or "").strip().strip("[]")
    if not h:
        return False, "no_host"
    try:
        infos = socket.getaddrinfo(h, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror:
        return False, "dns_unresolvable"
    except (UnicodeError, ValueError, OSError):
        return False, "bad_host"
    if not infos:
        return False, "dns_empty"
    for info in infos:
        addr = str(info[4][0]).split("%")[0]  # drop IPv6 scope id
        try:
            ip = ipaddress.ip_address(addr)
        except ValueError:
            return False, "bad_ip"
        if _ip_is_blocked(ip):
            return False, "private_or_reserved_ip"
    return True, ""


def wire_price_label() -> str:
    return f"${_WIRE_PRICE_USD}"


def wire_amount_atomic() -> str:
    return "497000000"  # $497 USDC, 6 decimals


def _normalize_url(raw: str) -> str | None:
    s = (raw or "").strip()
    if not s or not _URL_RE.match(s):
        return None
    parsed = urlparse(s)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    # Reject embedded credentials (user:pass@host) — a common SSRF/obfuscation vector.
    if parsed.username or parsed.password:
        return None
    if not parsed.hostname:
        return None
    return s.rstrip("/")


def _extract_pay_fields(payload: Any) -> dict:
    out: dict[str, Any] = {"pay_to": None, "amount": None, "network": None, "scheme": None}
    if not isinstance(payload, dict):
        return out
    accepts = payload.get("accepts")
    if isinstance(accepts, list) and accepts:
        first = accepts[0] if isinstance(accepts[0], dict) else {}
        out["pay_to"] = first.get("payTo") or first.get("pay_to")
        out["amount"] = first.get("amount") or first.get("maxAmountRequired")
        out["network"] = first.get("network")
        out["scheme"] = first.get("scheme")
    return out


def audit_endpoint(url: str, *, timeout: float = 12.0) -> dict:
    """Probe a URL; return structured audit (free — no payment)."""
    target = _normalize_url(url)
    if not target:
        return {
            "spec": SPEC,
            "ok": False,
            "url": url,
            "error": "invalid_url",
            "message": "Provide https:// origin or full endpoint URL.",
        }

    # SSRF guard: never let a caller point this server-side fetcher at an internal
    # address. Resolve the host and refuse any private/loopback/link-local target.
    if not _ssrf_allow_local():
        host = urlparse(target).hostname or ""
        host_ok, why = _host_is_public(host)
        if not host_ok:
            return {
                "spec": SPEC,
                "ok": False,
                "url": target,
                "reachable": False,
                "error": "blocked_target",
                "ssrf_reason": why,
                "findings": [
                    {
                        "code": "ssrf_blocked",
                        "detail": f"Target host is not a public address ({why}); refusing to probe.",
                    }
                ],
                "score": 0,
                "grade": "F",
                "message": "Refusing to probe a private, loopback, link-local, or unresolvable target.",
            }

    findings: list[dict] = []
    score = 100
    probe_status = None
    probe_body: Any = None
    pay_fields: dict = {}

    for method in ("GET", "POST"):
        try:
            # allow_redirects=False: a public URL must not be able to 3xx us into
            # an internal address (redirect-based SSRF). We never follow.
            if method == "GET":
                r = requests.get(target, timeout=timeout, allow_redirects=False)
            else:
                r = requests.post(
                    target,
                    json={},
                    headers={"Content-Type": "application/json"},
                    timeout=timeout,
                    allow_redirects=False,
                )
            probe_status = r.status_code
            if 300 <= probe_status < 400:
                findings.append(
                    {
                        "code": "redirect_not_followed",
                        "method": method,
                        "detail": (
                            f"{probe_status} redirect to "
                            f"{(r.headers.get('Location') or '?')[:200]}; not followed (SSRF guard)."
                        ),
                    }
                )
            ct = (r.headers.get("Content-Type") or "").lower()
            cl = r.headers.get("Content-Length")
            too_big = False
            try:
                too_big = cl is not None and int(cl) > _MAX_PROBE_BYTES
            except (TypeError, ValueError):
                too_big = False
            if "json" in ct and not too_big:
                try:
                    probe_body = r.json()
                except json.JSONDecodeError:
                    probe_body = None
            if probe_status == 402:
                pay_fields = _extract_pay_fields(probe_body)
                break
            if probe_status not in (402, 401, 403):
                continue
        except requests.RequestException as exc:
            findings.append({"code": "probe_failed", "method": method, "detail": str(exc)[:200]})
            score -= 40
            continue

    if probe_status is None:
        return {
            "spec": SPEC,
            "ok": False,
            "url": target,
            "reachable": False,
            "findings": findings or [{"code": "unreachable", "detail": "No response from GET or POST."}],
            "score": 0,
            "grade": "F",
            "fix": "Register on x402scan after the endpoint returns HTTP 402 with payTo.",
        }

    reachable = True
    if probe_status != 402:
        findings.append(
            {
                "code": "not_402",
                "detail": f"Expected HTTP 402; got {probe_status}. Paid x402 endpoints must challenge unpaid calls.",
            }
        )
        score -= 50

    pay_to = pay_fields.get("pay_to")
    if probe_status == 402 and not pay_to:
        findings.append({"code": "missing_payto", "detail": "402 body has no accepts[].payTo."})
        score -= 25
    elif pay_to and not _EVM_RE.match(str(pay_to)):
        findings.append({"code": "invalid_payto", "detail": f"payTo not valid EVM address: {pay_to!r}"})
        score -= 20

    if probe_status == 402 and not pay_fields.get("amount"):
        findings.append({"code": "missing_amount", "detail": "No amount in accepts[0]."})
        score -= 10

    pr_header = None
    # re-fetch headers only if we had a 402
    if probe_status == 402:
        try:
            r2 = requests.get(target, timeout=timeout, allow_redirects=False)
            for h in ("Payment-Required", "PAYMENT-REQUIRED", "payment-required"):
                if r2.headers.get(h):
                    pr_header = h
                    break
        except requests.RequestException:
            pass
        if not pr_header:
            findings.append(
                {
                    "code": "no_payment_required_header",
                    "detail": "Optional but helps clients: Payment-Required header with base64 challenge.",
                }
            )
            score -= 5

    score = max(0, min(100, score))
    grade = "A" if score >= 90 else "B" if score >= 75 else "C" if score >= 55 else "D" if score >= 35 else "F"

    return {
        "spec": SPEC,
        "ok": (
            probe_status == 402
            and bool(pay_to)
            and bool(_EVM_RE.match(str(pay_to or "")))
        ),
        "url": target,
        "reachable": reachable,
        "http_status": probe_status,
        "pay_to": pay_to,
        "amount_atomic": pay_fields.get("amount"),
        "network": pay_fields.get("network"),
        "scheme": pay_fields.get("scheme"),
        "payment_required_header": pr_header,
        "findings": findings,
        "score": score,
        "grade": grade,
        "wire": {
            "available": True,
            "price_usd": _WIRE_PRICE_USD,
            "endpoint": "/api/x402/wire",
            "note": "Paid wire delivers worker template + deploy checklist + bazaar listing steps. No email required.",
        },
        "install_fallback": {
            "price_usd": "2500.00",
            "path": "/install",
            "note": "Hands-on 48hr wiring if you want a human in the loop.",
        },
    }


def wire_bundle(
    *,
    domain: str,
    email: str,
    public_url: str,
    audit_url: str | None = None,
) -> dict:
    """Instant delivery after x402 pay — no human, no email thread."""
    dom = (domain or "").strip().lower().removeprefix("https://").removeprefix("http://").split("/")[0]
    em = (email or "").strip()
    bundle_id = hashlib.sha256(f"{dom}:{em}:{secrets.token_hex(8)}".encode()).hexdigest()[:24]
    base = (public_url or "").rstrip("/")
    audit_block = audit_endpoint(audit_url) if audit_url else None

    return {
        "spec": WIRE_SPEC,
        "paid": True,
        "bundle_id": bundle_id,
        "domain": dom,
        "email": em,
        "amount_usd": _WIRE_PRICE_USD,
        "deliverables": {
            "cloudflare_worker": f"{base}/listings/cloudflare-worker.js",
            "cloudflare_wrangler": f"{base}/listings/wrangler.toml",
            "slim_openapi_pattern": f"{base}/openapi.json",
            "x402_catalog": f"{base}/.well-known/x402.json",
            "prefinality_well_known": f"{base}/.well-known/prefinality.json",
            "x402scan_register": "https://www.x402scan.com/resources/register",
        },
        "deploy_checklist": [
            "Set GATE_X402_PAYTO (42-char 0x address) on your host — verify /health x402.configured true.",
            "Protect paid routes: return 402 when no Payment-Signature / X-Payment header.",
            "Publish /.well-known/x402 fan-out listing your paid resource URLs.",
            "Submit origin on x402scan (This URL only — not full openapi with dead routes).",
            "Optional: add AgentCash — npx agentcash add <your-origin>",
            "Optional: pre-finality — POST /v1/prefinality/evaluate before irreversible commits.",
        ],
        "audit_at_purchase": audit_block,
        "support": f"mailto:hello@velaru.xyz?subject=Wire%20{bundle_id}",
        "request_id": f"req_{uuid.uuid4().hex[:16]}",
    }
