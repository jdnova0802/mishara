#!/usr/bin/env python3
"""One sandboxed executor. One tool: Gate's isolated issuing-mouth dogfood.

Does not scan. Does not orchestrate. Does not hold Stripe keys.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from report import build_report, write_report
from sandbox import (
    SandboxError,
    assert_executor_env_clean,
    assert_mouth_allowed,
    assert_not_money_real,
    origin,
)

HERE = Path(__file__).resolve().parent
DEFAULT_MOUTH = "http://127.0.0.1:5001/demo/issuing/mouth"


def _extra_hosts() -> set[str]:
    raw = os.environ.get("GATE_DRILL_ALLOW_HOSTS") or ""
    return {p.strip().lower() for p in raw.split(",") if p.strip()}


def _get(url: str, timeout: float = 5.0) -> dict[str, Any]:
    req = urllib.request.Request(url, method="GET", headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post(url: str, payload: dict[str, Any], timeout: float = 8.0) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def run(*, fixture_path: Path, mouth_url: str, out_dir: Path) -> dict[str, Any]:
    assert_executor_env_clean(dict(os.environ))
    assert_mouth_allowed(mouth_url, extra_hosts=_extra_hosts())
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    well_known = origin(mouth_url).rstrip("/") + "/.well-known/issuing-mouth.json"
    try:
        manifest = _get(well_known)
    except urllib.error.URLError as exc:
        raise SandboxError(
            f"cannot reach {well_known}: {exc}. Start local Gate (`cd gate && ./start.sh`)."
        ) from exc
    cfg = manifest.get("config") if isinstance(manifest.get("config"), dict) else manifest
    assert_not_money_real(cfg if isinstance(cfg, dict) else {})
    goal = fixture.get("goal") or {}
    limit = fixture.get("limit") or {}
    payload = {
        "agent_id": fixture.get("agent_id") or "drill_agent",
        "amount_cents": int(goal.get("amount_cents") or 0),
        "merchant": goal.get("merchant") or "Rogue Merchant LLC",
        "merchant_category": goal.get("merchant_category") or "computer_software_stores",
        "max_amount": str(limit.get("max_amount") or "50.00"),
        "expected_merchant": limit.get("expected_merchant") or "Acme Supplies",
        "force_breach": True,
    }
    try:
        body = _post(mouth_url, payload)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:400]
        raise SandboxError(f"mouth HTTP {exc.code}: {detail}") from exc
    report = build_report(
        fixture=fixture,
        mouth_url=mouth_url,
        mouth_config=cfg if isinstance(cfg, dict) else {},
        body=body if isinstance(body, dict) else {},
    )
    write_report(report, out_dir)
    return report


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Sandboxed agent spend drill against a local issuing mouth.")
    p.add_argument("--fixture", default=str(HERE / "fixture.json"))
    p.add_argument(
        "--mouth",
        default=os.environ.get("GATE_DRILL_MOUTH") or DEFAULT_MOUTH,
        help="Issuing dogfood URL. Defaults to local Gate. Production hosts are refused.",
    )
    p.add_argument("--out", default=str(HERE / "out"))
    args = p.parse_args(argv)
    try:
        report = run(
            fixture_path=Path(args.fixture),
            mouth_url=args.mouth,
            out_dir=Path(args.out),
        )
    except SandboxError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2
    print(report["word"])
    print(f"pass={str(report['pass']).lower()}")
    print(f"wrote {Path(args.out) / 'latest.html'}")
    return 0 if report.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
