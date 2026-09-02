"""Gate-path probes — /health must exercise real routes, not config flags.

If Bind Room converts and the path is down, we should know from probes,
not from the customer. Keep probes short so Render health checks do not
time out.
"""
from __future__ import annotations

from typing import Any, Callable

# Local routes that must not 5xx. No self-probe of /health.
LOCAL_GET_PROBES: tuple[tuple[str, str], ...] = (
    ("bind_room", "/bind-room"),
    ("officer_pack", "/bind-room/officer-pack.json"),
    ("evidence_head", "/.well-known/evidence-head.json"),
    ("prefinality_jwks", "/.well-known/prefinality-jwks.json"),
    ("trust", "/trust"),
)


def probe_local_routes(client) -> dict[str, Any]:
    """Hit gate-path routes via Flask test client (in-process)."""
    out: dict[str, Any] = {}
    for name, path in LOCAL_GET_PROBES:
        try:
            r = client.get(path)
            ok = 200 <= int(r.status_code) < 500
            out[name] = {"ok": ok, "status": int(r.status_code), "path": path}
        except Exception as exc:  # noqa: BLE001 — health must never raise
            out[name] = {"ok": False, "status": None, "path": path, "error": type(exc).__name__}
    return out


def probe_velaru_verify(velaru_get: Callable[[str], Any], path: str = "/verify") -> dict[str, Any]:
    """External verify surface (Velaru). Short timeout expected in caller."""
    try:
        r = velaru_get(path)
        status = int(getattr(r, "status_code", 0) or 0)
        # Verify page may be 200 HTML; API variants may differ. <500 = route alive.
        ok = 200 <= status < 500
        return {"ok": ok, "status": status, "path": path}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": None, "path": path, "error": type(exc).__name__}


def summarize(probes: dict[str, Any]) -> dict[str, Any]:
    critical = ("bind_room", "officer_pack", "evidence_head", "prefinality_jwks")
    local_ok = all(probes.get(k, {}).get("ok") for k in critical)
    return {
        "ok": local_ok,
        "critical_ok": local_ok,
        "routes": probes,
    }
