#!/usr/bin/env python3
"""Clearance keeper bot — scan → liquidate → collect bounty.

Run against a live or local Gate (from gate/):

  GATE_API_URL=http://localhost:5001 python keeper_bot.py --keeper mine_01
  GATE_API_URL=http://localhost:5001 python keeper_bot.py --dogfood

Same lifestyle as a mining farm: ops loop, not outbound email.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


def _req(base: str, path: str, method: str = "GET", body: dict | None = None) -> dict:
    url = base.rstrip("/") + path
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"ok": False, "error": "http_error", "status": e.code, "body": raw}


def once(base: str, keeper_id: str) -> int:
    scan = _req(base, "/demo/keepers/scan")
    targets = scan.get("liquidatable") or []
    if not targets:
        print(json.dumps({"event": "empty_mempool", "count": 0}, indent=2))
        return 0
    wins = 0
    for t in targets:
        result = _req(
            base,
            "/demo/keepers/liquidate",
            method="POST",
            body={
                "position_id": t["position_id"],
                "keeper_id": keeper_id,
                "observation_id": t.get("observation_id"),
            },
        )
        print(json.dumps({"event": "liquidate_attempt", "target": t, "result": result}, indent=2))
        if result.get("ok"):
            wins += 1
    return wins


def main() -> int:
    p = argparse.ArgumentParser(description="Gate clearance keeper bot")
    p.add_argument("--base", default=os.getenv("GATE_API_URL", "http://localhost:5001"))
    p.add_argument("--keeper", default=os.getenv("GATE_KEEPER_ID", "keeper_local"))
    p.add_argument("--loop", type=float, default=0, help="Seconds between scans (0 = once)")
    p.add_argument("--dogfood", action="store_true", help="Run dogfood drill then exit")
    args = p.parse_args()

    if args.dogfood:
        out = _req(
            args.base,
            "/demo/keepers/dogfood",
            method="POST",
            body={"keeper_id": args.keeper},
        )
        print(json.dumps(out, indent=2))
        return 0 if (out.get("liquidate") or {}).get("ok") else 1

    if args.loop and args.loop > 0:
        while True:
            once(args.base, args.keeper)
            time.sleep(args.loop)
    else:
        once(args.base, args.keeper)
    return 0


if __name__ == "__main__":
    sys.exit(main())
