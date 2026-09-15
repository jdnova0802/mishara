"""Local HTTP stranger-verify — fetch receipts without trusting actor UI.

Lab only. No auth. Binds to 127.0.0.1. Not a product dashboard.
"""

from __future__ import annotations

import json
import threading
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable, Iterator
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


Lookup = Callable[[str], dict[str, Any] | None]


def _lookups() -> dict[str, Lookup]:
    """Late-bind so proves can reset stores before starting the server."""
    from gate.sims import actus_fence as af
    from gate.sims import mouth_watch as mw
    from gate.sims import performative_seal as ps

    def actus(rid: str) -> dict[str, Any] | None:
        return af.get_receipt(rid)

    def performative(rid: str) -> dict[str, Any] | None:
        return ps.get_receipt(rid)

    def watch(rid: str) -> dict[str, Any] | None:
        return mw.get_receipt(rid)

    return {
        "/v1/actus/receipts/": actus,
        "/v1/performative/receipts/": performative,
        "/v1/mouth-watch/threats/": watch,
        "/v1/mouth-watch/receipts/": watch,
    }


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return  # quiet lab server

    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/health", "/v1/verify/health"):
            self._json(200, {"ok": True, "their_production": False, "role": "stranger_verify"})
            return

        for prefix, lookup in _lookups().items():
            if self.path.startswith(prefix):
                rid = self.path[len(prefix) :].strip("/")
                if not rid or "/" in rid:
                    self._json(400, {"error": "bad_receipt_id", "their_production": False})
                    return
                receipt = lookup(rid)
                if receipt is None:
                    self._json(404, {"error": "not_found", "receipt_id": rid, "their_production": False})
                    return
                self._json(200, receipt)
                return

        self._json(404, {"error": "unknown_route", "path": self.path, "their_production": False})

    def _json(self, code: int, body: dict[str, Any]) -> None:
        raw = json.dumps(body, sort_keys=True).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("X-Nisaba-Verify", "stranger")
        self.end_headers()
        self.wfile.write(raw)


class VerifyServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 0) -> None:
        self._httpd = ThreadingHTTPServer((host, port), _Handler)
        self.host, self.port = self._httpd.server_address[:2]
        self.base_url = f"http://{self.host}:{self.port}"
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)

    def start(self) -> "VerifyServer":
        self._thread.start()
        return self

    def stop(self) -> None:
        self._httpd.shutdown()
        self._httpd.server_close()
        self._thread.join(timeout=2)


@contextmanager
def stranger_verify(host: str = "127.0.0.1", port: int = 0) -> Iterator[VerifyServer]:
    srv = VerifyServer(host=host, port=port).start()
    try:
        yield srv
    finally:
        srv.stop()


def http_get_json(url: str, *, timeout: float = 2.0) -> tuple[int, dict[str, Any]]:
    req = Request(url, method="GET", headers={"Accept": "application/json"})
    try:
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310 — lab localhost only
            raw = resp.read().decode("utf-8")
            return int(resp.status), json.loads(raw)
    except HTTPError as e:
        raw = e.read().decode("utf-8") if e.fp else "{}"
        try:
            body = json.loads(raw) if raw else {"error": "http_error"}
        except json.JSONDecodeError:
            body = {"error": "http_error", "raw": raw}
        return int(e.code), body
    except URLError as e:
        raise AssertionError(f"stranger verify unreachable: {e}") from e


def stranger_fetch(base_url: str, receipt_url: str) -> dict[str, Any]:
    """Fetch a receipt_url path against a running verify server."""
    if not receipt_url.startswith("/"):
        raise AssertionError(f"receipt_url must be a path, got {receipt_url!r}")
    code, body = http_get_json(f"{base_url.rstrip('/')}{receipt_url}")
    if code != 200:
        raise AssertionError(f"stranger fetch {receipt_url} → {code} {body}")
    return body
