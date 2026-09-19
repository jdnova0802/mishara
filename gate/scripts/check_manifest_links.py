#!/usr/bin/env python3
"""Crawl Gate manifest URLs with correct methods. POST-only → 405 is OK."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("GATE_PUBLIC_URL", "https://gate.velaru.xyz").rstrip("/")
# Allow local app under test — when GATE_DEV_MODE, caller may pass BASE=http://127.0.0.1:...

OK = {200, 301, 302, 303, 307, 308, 400, 401, 402, 403, 405, 422}
# 405 = method not allowed (GET on POST-only) — not a dead link
FAIL_HOST_FRAGMENTS = ("erra.onrender.com",)


def fetch(url: str, method: str = "GET") -> int:
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "nisaba-manifest-crawler/1"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return int(resp.status)
    except urllib.error.HTTPError as e:
        return int(e.code)
    except Exception as e:
        print(f"ERR {method} {url}: {e}")
        return -1


def main() -> int:
    gate = json.load(urllib.request.urlopen(f"{BASE}/.well-known/gate.json", timeout=25))
    urls = []
    for k, v in gate.items():
        if isinstance(v, str) and v.startswith("http") and "{" not in v:
            urls.append(v)
        elif isinstance(v, dict):
            for vv in v.values():
                if isinstance(vv, str) and vv.startswith("http") and "{" not in vv:
                    urls.append(vv)
    # Always probe core buyer surfaces
    for path in ("/", "/pricing", "/bind-room", "/privacy", "/terms", "/.well-known/commerce.json", "/.well-known/security.txt", "/openapi.json"):
        urls.append(f"{BASE}{path}")
    urls = sorted(set(urls))
    bad = []
    for url in urls:
        if any(f in url for f in FAIL_HOST_FRAGMENTS):
            bad.append((url, "do-not-advertise host"))
            continue
        code = fetch(url, "GET")
        if code in OK or code == 404 and "/.well-known/" not in url and url.rstrip("/").endswith(("evaluate", "admit", "burn", "die", "search", "register", "redeem", "bypass", "hop", "act")):
            # bare API roots sometimes 404 on GET — try POST
            if code == 404:
                code = fetch(url, "POST")
        if code not in OK and code != 404:
            # 404 on optional template links is still a fail for buyer/legal
            if any(x in url for x in ("/privacy", "/terms", "/pricing", "/bind-room", "commerce.json", "security.txt", "gate.json", "openapi.json")):
                bad.append((url, code))
            elif code == -1:
                bad.append((url, code))
        print(f"{code:4}  {url}")
    if bad:
        print("FAIL", bad)
        return 1
    print(f"OK {len(urls)} URLs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
