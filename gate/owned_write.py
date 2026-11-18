"""Caller-owned live write — not the 48-hour licensed-operator PAS weld.

Finding (read before treating this as "we removed friction"):

The 48-hour /operator weld exists because a halt on PolicyCenter / Guidewire /
Duck Creek is an exclusive door in *their* system. That needs a licensed
operator, exclusivity attestation, and a human delivery window. It is not a
statute, and patent 64/124,027 in-repo is the receipt engine, not a 48-hour
clock. Trust (/trust) withholds *their_production* until that exclusive-door
weld is recorded. Do not strip that path.

Self-serve keys only "drill" because POST /v1/act is clearance-only:
write_executed is always false; Gate is the meter, not the payout processor.
Hop-budget 402 ("Production is the weld") is a commercial funnel on top of that
protocol, not a compliance rule.

This module is the narrow exception: the caller already owns the write
(payout/withdraw function) end-to-end. They supply that HTTPS function as
write_url, attest it is the only mouth, and Gate hops then:

  deny / timeout / unreachable → do not POST write_url
  allow → POST write_url once, then sign the same bound receipt chain

PAS hostnames and PolicyCenter/Guidewire/Duck Creek paths are refused. This
never flips their_production. /v1/act without write_url stays clearance-only.
"""
from __future__ import annotations

import ipaddress
import socket
from typing import Any
from urllib.parse import urlparse

SPEC = "gate-owned-write-v1"
INVOKE_TIMEOUT_SECONDS = 5

BLOCKED_HOST_MARKERS = (
    "policycenter",
    "guidewire",
    "duckcreek",
    "duck-creek",
    "gwcloud",
    "gw-pc",
    "insurancesuite",
    "insurance-suite",
)

BLOCKED_PATH_MARKERS = (
    "/policycenter",
    "/duckcreek",
    "/pas/",
    "bind-and-issue",
    "guidewire",
    "policycenter",
)

_PRIVATE_NETS = (
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
)


def _host_blocked(host: str) -> bool:
    h = (host or "").strip().lower().rstrip(".")
    if not h:
        return True
    return any(m in h for m in BLOCKED_HOST_MARKERS)


def _path_blocked(path: str, query: str = "") -> bool:
    blob = f"{path or ''}?{query or ''}".lower()
    return any(m in blob for m in BLOCKED_PATH_MARKERS)


def _ip_blocked(ip: str) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return True
    if addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_multicast or addr.is_reserved:
        return True
    return any(addr in net for net in _PRIVATE_NETS)


def _resolve_ips(host: str) -> list[str]:
    found: list[str] = []
    try:
        for family, _type, _proto, _canon, sockaddr in socket.getaddrinfo(host, None):
            ip = sockaddr[0]
            if ip and ip not in found:
                found.append(ip)
    except socket.gaierror:
        return []
    return found


def classify_target(
    write_url: str | None,
    *,
    public_url: str | None = None,
    allow_loopback: bool = False,
) -> dict[str, Any]:
    """Refuse PAS / carrier systems and SSRF. Allow only a caller HTTPS function."""
    raw = (write_url or "").strip()
    if not raw:
        return {
            "ok": False,
            "code": "write_url_required",
            "message": "Caller-owned live mode needs write_url (your payout/withdraw function).",
        }
    parsed = urlparse(raw)
    scheme = (parsed.scheme or "").lower()
    host = (parsed.hostname or "").lower()
    path = parsed.path or "/"
    if scheme not in ("https", "http"):
        return {
            "ok": False,
            "code": "write_url_scheme",
            "message": "write_url must be http(s) pointing at your own function.",
        }
    if scheme != "https" and not allow_loopback:
        return {
            "ok": False,
            "code": "write_url_https",
            "message": "write_url must be https unless GATE_DEV_MODE loopback.",
        }
    if _host_blocked(host):
        return {
            "ok": False,
            "code": "pas_write_forbidden",
            "message": "write_url looks like PolicyCenter / Guidewire / Duck Creek. Licensed-operator weld only.",
        }
    if _path_blocked(path, parsed.query):
        return {
            "ok": False,
            "code": "pas_write_forbidden",
            "message": "write_url path is a PAS / bind door. Licensed-operator weld only.",
        }
    if public_url:
        ours = urlparse(public_url)
        our_host = (ours.hostname or "").lower()
        if host and our_host and host == our_host and _path_blocked(path, parsed.query):
            return {
                "ok": False,
                "code": "pas_write_forbidden",
                "message": "Cannot point owned-write at Gate PAS endpoints.",
            }
    ips = _resolve_ips(host) if host else []
    loopback_only = False
    if ips:
        try:
            loopback_only = all(ipaddress.ip_address(ip).is_loopback for ip in ips)
        except ValueError:
            loopback_only = False
    if allow_loopback and loopback_only:
        return {"ok": True, "write_url": raw, "host": host, "loopback": True}
    if scheme != "https":
        return {
            "ok": False,
            "code": "write_url_https",
            "message": "write_url must be https unless GATE_DEV_MODE loopback.",
        }
    if not ips:
        return {
            "ok": False,
            "code": "write_url_unresolved",
            "message": "write_url host did not resolve.",
        }
    for ip in ips:
        if _ip_blocked(ip):
            return {
                "ok": False,
                "code": "write_url_private",
                "message": "write_url resolves to a private or metadata address.",
            }
    return {"ok": True, "write_url": raw, "host": host, "loopback": False}


def truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in ("1", "true", "yes", "on")
    return False


def invoke(write_url: str, body: dict[str, Any], *, post=None) -> dict[str, Any]:
    """POST clearance to the caller function. Fail closed on timeout/non-2xx."""
    import requests as requests_lib

    post_fn = post or requests_lib.post
    try:
        r = post_fn(
            write_url,
            json=body,
            timeout=INVOKE_TIMEOUT_SECONDS,
            allow_redirects=False,
            headers={"Content-Type": "application/json", "X-Gate-Owned-Write": "1"},
        )
    except Exception as exc:  # noqa: BLE001 — surface to receipt
        return {
            "ok": False,
            "invoked": True,
            "status": None,
            "error": type(exc).__name__,
        }
    status = int(getattr(r, "status_code", 0) or 0)
    return {
        "ok": 200 <= status < 300,
        "invoked": True,
        "status": status,
        "error": None if 200 <= status < 300 else "write_url_non_2xx",
    }


def manifesto(public_url: str) -> dict[str, Any]:
    return {
        "spec": SPEC,
        "finding": (
            "48-hour licensed-operator weld stays for PolicyCenter/Guidewire/Duck Creek. "
            "Self-serve /v1/act is clearance-only. This path is only the caller's own "
            "payout/withdraw function as write_url."
        ),
        "their_production": False,
        "not": [
            "Not a PAS weld",
            "Not a new pricing tier",
            "Not an ops-token production attestation",
            "Does not flip their_production",
        ],
        "require": [
            "API key (same mint as today)",
            "write_url = caller-owned HTTPS function",
            "exclusive_owned=true (this function is the only mouth)",
        ],
        "endpoint": f"POST {public_url}/v1/act",
        "demo_refuses_invoke": True,
    }
