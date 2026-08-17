"""Public demo rate limiting — no API key, demo fuses only."""
import os
import time
from collections import defaultdict

DEMO_FUSES = frozenset(
    f.strip()
    for f in os.getenv(
        "GATE_DEMO_FUSES", "fuse_velaru_drill,fuse_demo_dead,fuse_demo_live"
    ).split(",")
    if f.strip()
)
DEMO_LIMIT = int(os.getenv("GATE_DEMO_LIMIT_PER_HOUR", "60"))
_WINDOW = 3600
_hits: dict[str, list[float]] = defaultdict(list)


def _client_ip(request) -> str:
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
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


def validate_demo_fuse(fuse_id: str) -> bool:
    return fuse_id in DEMO_FUSES
