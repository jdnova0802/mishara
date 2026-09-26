#!/usr/bin/env python3
"""Watch Gate's evidence head. Tree only grows. Stdlib only.

Usage:
  python3 gate/watch_evidence_head.py --url https://gate.velaru.xyz --cache /tmp/gate-head.json

Self-register as an independent unpaid watcher (no API key):
  python3 gate/watch_evidence_head.py --url https://gate.velaru.xyz \\
    --register --handle your-handle [--homepage https://example.com]

Exit 0 if ok (or first sample). Exit 2 if the tree shrank or the root was rewritten.
Exit 3 if --register failed.
"""
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def _fetch_json(url: str, timeout: int = 20) -> dict:
    req = urllib.request.Request(
        url, headers={"Accept": "application/json", "User-Agent": "gate-evidence-watch/1"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post_json(url: str, body: dict, timeout: int = 20) -> tuple[int, dict]:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "gate-evidence-watch/1",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw)
        except json.JSONDecodeError:
            return exc.code, {"ok": False, "error": "http_error", "body": raw[:500]}


def check_cached_head(current: dict, cached: dict | None) -> dict:
    size = int(current.get("tree_size") or 0)
    root = current.get("root_hash") or ""
    if not cached:
        return {"ok": True, "event": "first_sample", "tree_size": size, "root_hash": root}
    old_size = int(cached.get("tree_size") or 0)
    old_root = cached.get("root_hash") or ""
    if size < old_size:
        return {"ok": False, "event": "tree_shrunk", "old_size": old_size, "new_size": size}
    if size == old_size and root != old_root:
        return {
            "ok": False,
            "event": "root_rewritten_same_size",
            "tree_size": size,
            "old_root": old_root,
            "new_root": root,
        }
    if size == old_size:
        return {"ok": True, "event": "unchanged", "tree_size": size, "root_hash": root}
    return {
        "ok": True,
        "event": "grew",
        "old_size": old_size,
        "new_size": size,
        "old_root": old_root,
        "new_root": root,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Watch Gate evidence-head.json")
    parser.add_argument("--url", default="https://gate.velaru.xyz", help="Gate origin")
    parser.add_argument("--cache", default=".cache/evidence-head.json")
    parser.add_argument(
        "--register",
        action="store_true",
        help="POST this sample to /v1/evidence-watch/register (independent roster)",
    )
    parser.add_argument("--handle", default="", help="Public handle for --register")
    parser.add_argument("--homepage", default="", help="Optional https homepage")
    parser.add_argument("--note", default="", help="Optional short note (≤280 chars)")
    args = parser.parse_args(argv)
    origin = args.url.rstrip("/")
    head_url = origin + "/.well-known/evidence-head.json"
    try:
        current = _fetch_json(head_url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print("FAIL fetch", head_url, exc, file=sys.stderr)
        return 2
    cache_path = Path(args.cache)
    cached = None
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text())
        except json.JSONDecodeError:
            cached = None
    result = check_cached_head(current, cached)
    if cached and result.get("ok") and result.get("event") == "grew":
        cons_url = (
            origin
            + "/.well-known/evidence-consistency.json?"
            + urllib.parse.urlencode(
                {"old_size": cached.get("tree_size") or 0, "old_root": cached.get("root_hash") or ""}
            )
        )
        try:
            cons = _fetch_json(cons_url)
            result["consistency_valid"] = cons.get("valid")
            result["cached_old_root_matches"] = cons.get("cached_old_root_matches")
            if cons.get("valid") is False or cons.get("cached_old_root_matches") is False:
                result["ok"] = False
                result["event"] = "consistency_failed"
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            result["ok"] = False
            result["event"] = "consistency_fetch_failed"
            result["error"] = str(exc)

    register_out = None
    if args.register and result.get("ok"):
        handle = (args.handle or "").strip()
        if not handle:
            print("FAIL --register requires --handle", file=sys.stderr)
            return 3
        body = {
            "handle": handle,
            "tree_size": int(current.get("tree_size") or 0),
            "root_hash": current.get("root_hash") or "",
            "sampled_at": datetime.now(timezone.utc).isoformat(),
        }
        if args.homepage:
            body["homepage"] = args.homepage.strip()
        if args.note:
            body["note"] = args.note.strip()[:280]
        try:
            code, register_out = _post_json(origin + "/v1/evidence-watch/register", body)
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print("FAIL register", exc, file=sys.stderr)
            return 3
        if code >= 400 or not register_out.get("ok"):
            print(json.dumps({"check": result, "register": register_out}, indent=2))
            return 3

    print(
        json.dumps(
            {
                "check": result,
                "head": {
                    "tree_size": current.get("tree_size"),
                    "root_hash": current.get("root_hash"),
                },
                "register": register_out,
            },
            indent=2,
        )
    )
    if not result.get("ok"):
        return 2
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(
        json.dumps(
            {
                "tree_size": current.get("tree_size"),
                "root_hash": current.get("root_hash"),
                "timestamp": current.get("timestamp"),
            },
            indent=2,
        )
        + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
