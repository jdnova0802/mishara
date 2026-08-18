"""Resolve Gate's advertised URL. Production must never advertise localhost."""
from __future__ import annotations

import os

LOCAL_MARKERS = (
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "[::1]",
    "://10.",
    "://192.168.",
    "://172.16.",
    "://172.17.",
    "://172.18.",
    "://172.19.",
    "://172.2",
    "://172.30.",
    "://172.31.",
)


def is_local_url(url: str) -> bool:
    u = (url or "").strip().lower()
    if not u:
        return True
    return any(m in u for m in LOCAL_MARKERS)


def _render_url() -> str:
    explicit = (os.getenv("RENDER_EXTERNAL_URL") or "").strip().rstrip("/")
    if explicit:
        return explicit
    host = (os.getenv("RENDER_EXTERNAL_HOSTNAME") or "").strip()
    if host:
        return f"https://{host}"
    return ""


def resolve_public_url() -> str:
    """Prefer an explicit public URL; if that URL is local, lift to Render's hostname."""
    explicit = (os.getenv("GATE_PUBLIC_URL") or "").strip().rstrip("/")
    render = _render_url()
    if explicit and not is_local_url(explicit):
        return explicit
    if render and not is_local_url(render):
        return render
    if explicit:
        return explicit
    return "http://localhost:5001"


def is_dev_mode() -> bool:
    return os.getenv("GATE_DEV_MODE", "0") == "1"


def allow_local() -> bool:
    return os.getenv("GATE_ALLOW_LOCAL", "0") == "1" or is_dev_mode()


def db_path_is_ephemeral(path: str) -> bool:
    p = (path or "").replace("\\", "/")
    return p.startswith("/tmp") or "/tmp/" in p or p == ":memory:"


def public_ok(url: str | None = None) -> bool:
    u = url if url is not None else resolve_public_url()
    return (not is_local_url(u)) and u.startswith("https://")


def assert_prod_public() -> str:
    """Exit non-zero if production would advertise localhost. Call from run-prod.sh."""
    url = resolve_public_url()
    if allow_local():
        return url
    if not public_ok(url):
        raise SystemExit(
            "GATE_PUBLIC_URL is local/http. Set GATE_PUBLIC_URL to your https origin "
            "(Render sets RENDER_EXTERNAL_URL automatically). Refusing to start."
        )
    db_path = os.getenv("GATE_DB_PATH", "./gate.db")
    if db_path_is_ephemeral(db_path):
        raise SystemExit(
            f"GATE_DB_PATH={db_path} is ephemeral. Use /var/data/gate.db on Render."
        )
    return url
