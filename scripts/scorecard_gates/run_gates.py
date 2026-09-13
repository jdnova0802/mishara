#!/usr/bin/env python3
"""Zero-tolerance scorecard gates (Dims 11–14).

  python scripts/scorecard_gates/run_gates.py
  python scripts/scorecard_gates/run_gates.py --dim 14
  python scripts/scorecard_gates/run_gates.py --prove-fail 13
  python scripts/scorecard_gates/run_gates.py --live
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

REPO = Path(__file__).resolve().parents[2]
GATE = REPO / "gate"
SCORECARD = REPO / "docs" / "scorecard"
BANNED_LAB = SCORECARD / "banned_lab_terms.txt"
BORROWED = SCORECARD / "borrowed_cred_terms.txt"
LADDER = GATE / "commerce" / "ladder.json"

MANIFEST_PATHS = (
    "/.well-known/gate.json",
    "/llms.txt",
    "/.well-known/commerce.json",
    "/.well-known/opportunities.json",
)

SKIP_DIRS = {".git", "__pycache__", ".venv", "venv", "node_modules", "cwv", ".pytest_cache"}
ALLOWLIST_NAMES = {
    "banned_lab_terms.txt",
    "borrowed_cred_terms.txt",
    "run_gates.py",
    "test_zero_tolerance_gates.py",
    "NISABA_FLAWLESS_SCORECARD.md",
    "VERIFICATION_QUEUE.md",
    "STRANGER_TEST_DIM19.md",
}


def load_terms(path: Path) -> list[str]:
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            out.append(line)
    return out


def iter_scan_files(roots: list[Path]) -> list[Path]:
    exts = {".py", ".html", ".md", ".txt", ".json", ".yml", ".yaml", ".css", ".js"}
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            if root.name not in ALLOWLIST_NAMES and not root.name.startswith("test_"):
                files.append(root)
            continue
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.name in ALLOWLIST_NAMES:
                continue
            if path.name.startswith("test_") or path.name.endswith("_test.py"):
                continue
            if path.suffix.lower() not in exts:
                continue
            files.append(path)
    return files


def http_status(url: str, method: str = "GET") -> int:
    req = urllib.request.Request(
        url, method=method, headers={"User-Agent": "nisaba-scorecard-gate/1"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as e:
        return int(e.code)
    except Exception as e:
        print(f"ERR {method} {url}: {e}")
        return -1


# Dim 11 API liveness — NOT "anything except 404".
# Pages: final HTTP 200 only (redirects followed by urllib / Flask follow_redirects).
# API under /v1|/api|/demo may prove the route is mounted via a *documented* response:
#   GET 401/403  → auth challenge (endpoint exists, gated)
#   GET 405      → wrong method (endpoint exists)
#   GET 404 + POST in {200,400,401,403,405,415,422}
#                → POST-only rule that accepts/validates/auth-challenges
# Rejected: bare GET 404, POST 404, 5xx, connection errors (-1), or any other code.
API_GET_LIVE = frozenset({401, 403, 405})
API_POST_LIVE = frozenset({200, 400, 401, 403, 405, 415, 422})


def api_path_is_live(get_code: int, post_code: int | None = None) -> tuple[bool, int, str]:
    """Return (ok, reported_code, reason)."""
    if get_code == 200:
        return True, get_code, "GET 200"
    if get_code in API_GET_LIVE:
        return True, get_code, f"GET {get_code} auth/method challenge"
    if get_code == 404 and post_code is not None:
        if post_code in API_POST_LIVE:
            return True, post_code, f"POST-only live ({post_code})"
        return False, post_code if post_code != -1 else 404, f"POST not sensible ({post_code})"
    return False, get_code, f"not a live page/API response ({get_code})"


def extract_urls(obj, base: str, found: set[str]) -> None:
    if isinstance(obj, str):
        if obj.startswith("http") and "{" not in obj:
            found.add(obj)
        elif obj.startswith("/") and "{" not in obj and " " not in obj:
            found.add(base.rstrip("/") + obj)
    elif isinstance(obj, dict):
        for v in obj.values():
            extract_urls(v, base, found)
    elif isinstance(obj, list):
        for v in obj:
            extract_urls(v, base, found)


def check_dim11_live(base_url: str | None = None) -> int:
    base = (base_url or os.environ.get("GATE_PUBLIC_URL") or "https://gate.velaru.xyz").rstrip("/")
    print(f"Dim 11 — live manifest crawl ({base})")
    urls: set[str] = set()
    for path in MANIFEST_PATHS:
        url = f"{base}{path}"
        code = http_status(url)
        print(f"  manifest {code:4}  {url}")
        if code != 200:
            print(f"FAIL Dim 11: {path} returned {code}")
            return 1
        if path.endswith(".json"):
            with urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "nisaba-scorecard-gate/1"}),
                timeout=20,
            ) as resp:
                extract_urls(json.loads(resp.read().decode()), base, urls)
        else:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": "nisaba-scorecard-gate/1"}),
                timeout=20,
            ) as resp:
                text = resp.read().decode("utf-8", errors="replace")
            for m in re.finditer(r"https?://[^\s)>\"']+", text):
                urls.add(m.group(0).rstrip(".,;"))
    for path in ("/", "/pricing", "/bind-room", "/privacy", "/terms"):
        urls.add(f"{base}{path}")
    bad: list[tuple[str, int, str]] = []
    for url in sorted(urls):
        path = urlparse(url).path or "/"
        get_code = http_status(url)
        post_code = None
        if (
            get_code != 200
            and get_code not in API_GET_LIVE
            and path.startswith(("/v1/", "/api/", "/demo/"))
        ):
            post_code = http_status(url, "POST")
        if path.startswith(("/v1/", "/api/", "/demo/")):
            ok, code, why = api_path_is_live(get_code, post_code)
        else:
            ok, code, why = (get_code == 200, get_code, "page GET 200" if get_code == 200 else f"page {get_code}")
        print(f"  {'OK' if ok else 'BAD'} {code:4}  {url}  ({why})")
        if not ok:
            bad.append((url, code, why))
    if bad:
        print(f"FAIL Dim 11: {bad[:12]}")
        return 1
    print(f"PASS Dim 11 — {len(urls)} URLs")
    return 0


def check_dim11_offline() -> int:
    print("Dim 11 — offline Flask crawl")
    os.environ.setdefault("GATE_DEV_MODE", "1")
    if str(GATE) not in sys.path:
        sys.path.insert(0, str(GATE))
    try:
        from app import app  # type: ignore
    except Exception as e:
        print(f"FAIL Dim 11 offline: import app: {e}")
        return 1
    client = app.test_client()
    # Strict set: manifests + URLs declared inside JSON manifests + buyer pages.
    path_set: set[str] = set(MANIFEST_PATHS)
    for path in MANIFEST_PATHS:
        r = client.get(path)
        print(f"  manifest {r.status_code:4}  {path}")
        if r.status_code != 200:
            print(f"FAIL Dim 11: {path} → {r.status_code}")
            return 1
        if path.endswith(".json"):
            tmp: set[str] = set()
            extract_urls(r.get_json(), "http://local", tmp)
            for u in tmp:
                if u.startswith("http://local"):
                    path_set.add(urlparse(u).path or "/")
                elif u.startswith("/") and "{" not in u:
                    path_set.add(u.split("?")[0])
        else:
            # llms.txt — only absolute http(s) links that point at this host's paths
            text = r.get_data(as_text=True)
            for m in re.finditer(r"https?://[^\s)>\"']+", text):
                parsed = urlparse(m.group(0).rstrip(".,;"))
                host = (parsed.hostname or "").lower()
                if host in {"localhost", "127.0.0.1", "gate.velaru.xyz", "gate.example"}:
                    if parsed.path:
                        path_set.add(parsed.path)
    for path in ("/", "/pricing", "/bind-room", "/privacy", "/terms"):
        path_set.add(path)
    check = sorted(
        p
        for p in path_set
        if p.startswith("/") and "{" not in p and " " not in p and not p.startswith("//")
    )
    bad: list[tuple[str, int, str]] = []
    for path in check:
        r = client.get(path, follow_redirects=True)
        get_code = r.status_code
        post_code = None
        if (
            get_code != 200
            and get_code not in API_GET_LIVE
            and path.startswith(("/v1/", "/api/", "/demo/"))
        ):
            post_code = client.post(path, json={}).status_code
        if path.startswith(("/v1/", "/api/", "/demo/")):
            ok, code, why = api_path_is_live(get_code, post_code)
        else:
            ok, code, why = (
                get_code == 200,
                get_code,
                "page GET 200" if get_code == 200 else f"page {get_code}",
            )
        print(f"  {'OK' if ok else 'BAD'} {code:4}  {path}  ({why})")
        if not ok:
            bad.append((path, code, why))
    if bad:
        print(f"FAIL Dim 11 offline: {bad[:20]}")
        return 1
    print(f"PASS Dim 11 offline — {len(check)} paths")
    return 0


def product_roots(extra: list[Path] | None) -> list[Path]:
    roots = [GATE, REPO / "templates", REPO / "mishara_app.py"]
    if extra:
        roots.extend(extra)
    return roots


def scan_terms(files: list[Path], terms: list[str], dim: int) -> int:
    hits: list[str] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        try:
            rel = path.relative_to(REPO)
        except ValueError:
            rel = path
        for term in terms:
            if re.search(rf"\b{re.escape(term)}\b", text):
                hits.append(f"{rel}: {term}")
        if dim == 13 and re.search(r"/api/v1/dtcc\b|/dtcc/", text, re.I):
            hits.append(f"{rel}: route path contains /dtcc")
    if hits:
        print(f"FAIL Dim {dim}:")
        for h in hits[:50]:
            print(f"  {h}")
        if len(hits) > 50:
            print(f"  … +{len(hits) - 50} more")
        return 1
    print(f"PASS Dim {dim} — {len(files)} files, {len(terms)} terms")
    return 0


def check_dim12(extra: list[Path] | None = None) -> int:
    print("Dim 12 — banned lab terms")
    return scan_terms(iter_scan_files(product_roots(extra)), load_terms(BANNED_LAB), 12)


def check_dim13_velaru_routes(velaru_root: Path) -> int:
    """Dim 13 path floor for a local Velaru checkout (optional local/dev use)."""
    print(f"Dim 13 — Velaru /dtcc route absence ({velaru_root})")
    if not velaru_root.exists():
        print(f"FAIL Dim 13 Velaru routes: missing root {velaru_root}")
        return 1
    hits: list[str] = []
    for path in sorted(velaru_root.rglob("*.py")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name.startswith("test_") or path.name.endswith("_test.py"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            if "/dtcc" not in line.lower():
                continue
            if "@app.route" in line or "@router." in line or ".add_url_rule" in line:
                hits.append(f"{path.relative_to(velaru_root)}:{i}: {line.strip()}")
    if hits:
        print("FAIL Dim 13 Velaru routes still registered:")
        for h in hits[:40]:
            print(f"  {h}")
        return 1
    print("PASS Dim 13 Velaru routes — no /dtcc registrations")
    return 0


# Production hosts that must not serve /dtcc (even as redirects).
VELARU_LIVE_BASES = (
    "https://velaru.xyz",
    "https://velaru.onrender.com",
)
VELARU_DTCC_PATHS = (
    "/dtcc",
    "/foundry/dtcc",
    "/api/v1/dtcc/events.json",
    "/api/v1/dtcc/attest",
    "/api/v1/dtcc/production/status.json",
)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


_NO_REDIRECT = urllib.request.build_opener(_NoRedirect)


def http_status_no_follow(url: str, method: str = "GET") -> int:
    """Return status without following redirects — 302/308 still advertise the path."""
    req = urllib.request.Request(
        url, method=method, headers={"User-Agent": "nisaba-scorecard-gate/1"}
    )
    try:
        with _NO_REDIRECT.open(req, timeout=20) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as e:
        return int(e.code)
    except Exception as e:
        print(f"ERR {method} {url}: {e}")
        return -1


def check_dim13_velaru_live(bases: tuple[str, ...] | None = None) -> int:
    """Dim 13 Velaru path floor via live HTTP — no checkout token required.

    Source ownership lives in Velaru CI (`scripts/dim13_dtcc_route_floor.py`).
    This probe proves production actually returns 404 (not 302/308).
    """
    print("Dim 13 — Velaru live /dtcc path floor")
    bad: list[str] = []
    for base in bases or VELARU_LIVE_BASES:
        for path in VELARU_DTCC_PATHS:
            url = f"{base.rstrip('/')}{path}"
            code = http_status_no_follow(url)
            ok = code == 404
            print(f"  {'OK' if ok else 'BAD'} {code:4}  {url}")
            if not ok:
                bad.append(f"{url} → {code} (need 404, not redirect/live)")
        # POST-only legacy webhook must also be gone
        post_url = f"{base.rstrip('/')}/api/v1/dtcc/production/webhook"
        post_code = http_status_no_follow(post_url, "POST")
        ok = post_code == 404
        print(f"  {'OK' if ok else 'BAD'} {post_code:4}  POST {post_url}")
        if not ok:
            bad.append(f"POST {post_url} → {post_code}")
    if bad:
        print("FAIL Dim 13 Velaru live:")
        for b in bad:
            print(f"  {b}")
        return 1
    print("PASS Dim 13 Velaru live — all /dtcc paths 404")
    return 0


def check_dim13(
    extra: list[Path] | None = None,
    *,
    velaru_routes_only: bool = False,
    velaru_live: bool = False,
) -> int:
    print("Dim 13 — borrowed credibility")
    if velaru_live:
        return check_dim13_velaru_live()
    if velaru_routes_only:
        if not extra:
            print("FAIL Dim 13: --velaru-routes-only requires --velaru-root")
            return 1
        return check_dim13_velaru_routes(extra[0])
    return scan_terms(iter_scan_files(product_roots(extra)), load_terms(BORROWED), 13)


def check_dim14() -> int:
    print("Dim 14 — price SSOT")
    if not LADDER.is_file():
        print(f"FAIL Dim 14: missing {LADDER}")
        return 1
    ladder = json.loads(LADDER.read_text(encoding="utf-8"))
    bind = next(r for r in ladder["public_ladder"] if r["id"] == "bind_room")
    if bind.get("price_label") != "$1,750" or int(bind.get("price_cents") or 0) != 175000:
        print("FAIL Dim 14: ladder bind_room price shape unexpected")
        return 1
    allowed = {
        LADDER.resolve(),
        (GATE / "test_commerce.py").resolve(),
        (GATE / "test_faces.py").resolve(),
        (GATE / "test_hustle_doors.py").resolve(),
        (GATE / "test_listings.py").resolve(),
        (GATE / "test_zero_tolerance_gates.py").resolve(),
        Path(__file__).resolve(),
    }
    pattern = re.compile(r"\$1,?750|175000")
    offenders: list[str] = []
    for path in iter_scan_files([GATE, REPO / "docs"]):
        if path.resolve() in allowed or path.name.startswith("test_"):
            continue
        if pattern.search(path.read_text(encoding="utf-8", errors="replace")):
            offenders.append(str(path.relative_to(REPO)))
    if offenders:
        print("FAIL Dim 14 — hand-typed Bind Room price:")
        for o in offenders:
            print(f"  {o}")
        return 1
    print("PASS Dim 14")
    return 0


def prove_fail(dim: int) -> int:
    print(f"PROVE-FAIL Dim {dim}")
    if dim == 11:
        rc = check_dim11_live("https://gate.velaru.xyz/dim11-prove-fail-path-must-404")
        if rc == 0:
            print("PROVE-FAIL Dim 11 inert")
            return 1
        print("PROVE-FAIL Dim 11 OK")
        return 0
    if dim == 12:
        poison = GATE / "templates" / "_dim12_poison_probe.html"
        poison.write_text("CHOKE\n", encoding="utf-8")
        try:
            rc = check_dim12()
        finally:
            poison.unlink(missing_ok=True)
        if rc == 0:
            print("PROVE-FAIL Dim 12 inert")
            return 1
        print("PROVE-FAIL Dim 12 OK")
        return 0
    if dim == 13:
        poison = GATE / "templates" / "_dim13_poison_probe.html"
        poison.write_text("DTCC\n", encoding="utf-8")
        try:
            rc = check_dim13()
        finally:
            poison.unlink(missing_ok=True)
        if rc == 0:
            print("PROVE-FAIL Dim 13 inert")
            return 1
        print("PROVE-FAIL Dim 13 OK")
        return 0
    if dim == 14:
        poison = GATE / "templates" / "_dim14_poison_probe.html"
        poison.write_text("$1,750\n", encoding="utf-8")
        try:
            rc = check_dim14()
        finally:
            poison.unlink(missing_ok=True)
        if rc == 0:
            print("PROVE-FAIL Dim 14 inert")
            return 1
        print("PROVE-FAIL Dim 14 OK")
        return 0
    return 1


def prove_fail_velaru_live() -> int:
    """Prove the live /dtcc probe fails loud on unreachable + non-404 responses.

    Live-network checks introduce an edge repo-scans don't: a hung/unreachable
    host must not silently pass. Same bar as Dim 11–14 prove-fail.
    """
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    print("PROVE-FAIL Dim 13 Velaru live")

    # 1) Unreachable — connection error must FAIL (not skip/pass).
    unreachable_rc = check_dim13_velaru_live(bases=("https://127.0.0.1:1",))
    if unreachable_rc == 0:
        print("PROVE-FAIL Velaru live inert: unreachable host silently passed")
        return 1
    print("PROVE-FAIL Velaru live — unreachable fails loud OK")

    # 2) Reachable but wrong — silent 308 redirect must FAIL (not count as gone).
    class _LegacyRedirect(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:  # noqa: A003
            return

        def do_GET(self) -> None:  # noqa: N802
            self.send_response(308)
            self.send_header("Location", "/api/v1/settlement/attest")
            self.end_headers()

        def do_POST(self) -> None:  # noqa: N802
            self.send_response(308)
            self.send_header("Location", "/api/v1/settlement/production/webhook")
            self.end_headers()

    server = ThreadingHTTPServer(("127.0.0.1", 0), _LegacyRedirect)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        redirect_rc = check_dim13_velaru_live(bases=(f"http://127.0.0.1:{port}",))
    finally:
        server.shutdown()
        server.server_close()
    if redirect_rc == 0:
        print("PROVE-FAIL Velaru live inert: 308 redirect silently passed")
        return 1
    print("PROVE-FAIL Velaru live — non-404/308 fails loud OK")
    print("PROVE-FAIL Dim 13 Velaru live OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dim", type=int, choices=(11, 12, 13, 14))
    ap.add_argument("--prove-fail", type=int, choices=(11, 12, 13, 14), dest="prove")
    ap.add_argument(
        "--prove-fail-velaru-live",
        action="store_true",
        help="Prove Dim 13 live probe fails on unreachable + non-404 (308) hosts.",
    )
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--velaru-root", type=Path)
    ap.add_argument(
        "--velaru-routes-only",
        action="store_true",
        help="Dim 13: local Velaru checkout route scan (dev only).",
    )
    ap.add_argument(
        "--velaru-live",
        action="store_true",
        help="Dim 13: live HTTP path floor against velaru.xyz (no token).",
    )
    args = ap.parse_args(argv)
    extra = [args.velaru_root] if args.velaru_root else None
    if args.prove_fail_velaru_live:
        return prove_fail_velaru_live()
    if args.prove:
        return prove_fail(args.prove)
    dims = (args.dim,) if args.dim else (11, 12, 13, 14)
    rc = 0
    for d in dims:
        if d == 11:
            rc |= check_dim11_live() if args.live else check_dim11_offline()
        elif d == 12:
            rc |= check_dim12(extra)
        elif d == 13:
            rc |= check_dim13(
                extra,
                velaru_routes_only=args.velaru_routes_only,
                velaru_live=args.velaru_live,
            )
        else:
            rc |= check_dim14()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
