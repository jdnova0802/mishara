"""Public demo rate limiting — no API key, demo fuses only."""
import ipaddress
import os
import time
from collections import defaultdict

# Number of trusted reverse proxies that append to X-Forwarded-For in front of the
# app (Render's edge appends exactly one). The real client IP is that many entries
# from the RIGHT; anything a client prepends sits to the left and is ignored.
TRUSTED_PROXY_HOPS = max(1, int(os.getenv("GATE_TRUSTED_PROXY_HOPS", "1")))

DEMO_FUSES = frozenset(
    f.strip()
    for f in os.getenv(
        "GATE_DEMO_FUSES", "fuse_velaru_drill,fuse_demo_dead,fuse_demo_live"
    ).split(",")
    if f.strip()
)
DEMO_LIMIT = int(os.getenv("GATE_DEMO_LIMIT_PER_HOUR", "60"))
# The audit endpoint makes server-side fetches to caller-supplied URLs, so it is
# rate limited more tightly than ordinary demo calls (SSRF/port-scan amplification).
AUDIT_LIMIT = int(os.getenv("GATE_AUDIT_LIMIT_PER_HOUR", "30"))
_WINDOW = 3600
_hits: dict[str, list[float]] = defaultdict(list)
_audit_hits: dict[str, list[float]] = defaultdict(list)


def _valid_ip(value: str) -> bool:
    try:
        ipaddress.ip_address((value or "").strip())
        return True
    except ValueError:
        return False


def _client_ip(request) -> str:
    """Best-effort real client IP that a client cannot spoof by header injection.

    X-Forwarded-For is "client, proxy1, ..., lastProxy", where each trusted proxy
    APPENDS. Taking the leftmost value (the old behavior) let any caller forge a
    fresh rate-limit bucket per request by prepending a random IP. Instead we take
    the entry TRUSTED_PROXY_HOPS from the right — the address our own edge saw —
    and fall back to remote_addr when the header is absent or malformed."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        if parts:
            idx = len(parts) - TRUSTED_PROXY_HOPS
            if idx < 0:
                idx = 0
            candidate = parts[idx]
            if _valid_ip(candidate):
                return candidate
    return request.remote_addr or "unknown"


def allow_demo(request) -> tuple[bool, str]:
    ip = _client_ip(request)
    now = time.time()
    window_start = now - _WINDOW
    _hits[ip] = [t for t in _hits[ip] if t > window_start]
    if len(_hits[ip]) >= DEMO_LIMIT:
        return False, "Demo rate limit exceeded. Sign up for a free API key."
    _hits[ip].append(now)
    return True, ""


def allow_audit(request) -> tuple[bool, str]:
    """Per-client limit for the server-side URL auditor (tighter than demo)."""
    ip = _client_ip(request)
    now = time.time()
    window_start = now - _WINDOW
    _audit_hits[ip] = [t for t in _audit_hits[ip] if t > window_start]
    if len(_audit_hits[ip]) >= AUDIT_LIMIT:
        return False, "Audit rate limit exceeded. Try again later."
    _audit_hits[ip].append(now)
    return True, ""


def validate_demo_fuse(fuse_id: str) -> bool:
    return fuse_id in DEMO_FUSES
