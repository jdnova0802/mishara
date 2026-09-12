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
    bad: list[tuple[str, int]] = []
    for url in sorted(urls):
        code = http_status(url)
        ok = code == 200
        path = urlparse(url).path or "/"
        if not ok and code in {401, 403, 405} and path.startswith(("/v1/", "/api/", "/demo/")):
            ok = True
        if not ok and code == 404 and path.startswith(("/v1/", "/api/", "/demo/")):
            post_code = http_status(url, "POST")
            if post_code not in (-1, 404):
                ok = True
                code = post_code
        print(f"  {'OK' if ok else 'BAD'} {code:4}  {url}")
        if not ok:
            bad.append((url, code))
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
    bad: list[tuple[str, int]] = []
    for path in check:
        r = client.get(path, follow_redirects=True)
        code = r.status_code
        ok = code == 200
        if not ok and code in {401, 403, 405} and path.startswith(("/v1/", "/api/", "/demo/")):
            ok = True
        # Flask may 404 GET on POST-only rules; POST proving the route is mounted counts.
        if not ok and code == 404 and path.startswith(("/v1/", "/api/", "/demo/")):
            post = client.post(path, json={})
            if post.status_code != 404 and post.status_code != -1:
                ok = True
                code = post.status_code
        print(f"  {'OK' if ok else 'BAD'} {code:4}  {path}")
        if not ok:
            bad.append((path, code))
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


def check_dim13(extra: list[Path] | None = None) -> int:
    print("Dim 13 — borrowed credibility")
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dim", type=int, choices=(11, 12, 13, 14))
    ap.add_argument("--prove-fail", type=int, choices=(11, 12, 13, 14), dest="prove")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--velaru-root", type=Path)
    args = ap.parse_args(argv)
    extra = [args.velaru_root] if args.velaru_root else None
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
            rc |= check_dim13(extra)
        else:
            rc |= check_dim14()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
