"""Ops guards — foothill automation only (no mountain).

Protects strongest-start honesty:
  - live smoke (prod HTML ≠ stale copy)
  - promo last-proved auto
  - patent deadline alarm
  - buyer-surface lint (local templates)
  - Stripe SKU presence
  - Gate 1 counter (stranger paid?)

Run: python3 -m gate.ops_guards [--live]
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SPEC = "gate-ops-guards-v1"

DEFAULT_PATENT_FILED = os.getenv("GATE_PATENT_FILED_AT", "2026-06-01")

STALE_HOME = (r"Two artifacts", r"Weld a path\s*[·•]\s*\$25")
STALE_BIND = (r"Two artifacts", r"Book Bind Room")
GOOD_BIND = (r"We block the bind", r"block the bind", r"Pay Bind Room", r"Start:\s*Bind Room")
STALE_CHECK = (r"Next drill.*Aug\s*18", r"Tue Aug 18 2026")

BUYER_TEMPLATES = (
    "templates/index.html",
    "templates/bind_room.html",
    "templates/pricing.html",
    "templates/operator.html",
)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _parse_date(s: str | None) -> datetime | None:
    if not s or not str(s).strip():
        return None
    t = str(s).strip().replace("Z", "+00:00")
    if len(t) == 10 and t[4] == "-" and t[7] == "-":
        t += "T00:00:00+00:00"
    try:
        dt = datetime.fromisoformat(t)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _fetch(url: str, timeout: float = 12.0) -> tuple[int, str]:
    req = Request(url, headers={"User-Agent": "GateOpsGuards/1.0"})
    with urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return int(getattr(resp, "status", 200) or 200), body


def patent_alarm(now: datetime | None = None) -> dict[str, Any]:
    now = now or _now()
    filed = _parse_date(os.getenv("GATE_PATENT_FILED_AT", DEFAULT_PATENT_FILED))
    deadline = _parse_date(os.getenv("GATE_PATENT_DEADLINE_AT"))
    if deadline is None and filed is not None:
        deadline = filed + timedelta(days=365)
    if deadline is None:
        return {
            "ok": False,
            "level": "warn",
            "code": "patent_deadline_unknown",
            "message": "Set GATE_PATENT_FILED_AT or GATE_PATENT_DEADLINE_AT",
            "patent": "64/124,027",
        }
    days = (deadline - now).days
    if days < 0:
        level, code = "fail", "patent_deadline_passed"
    elif days <= 60:
        level, code = "fail", "patent_deadline_urgent"
    elif days <= 120:
        level, code = "warn", "patent_deadline_soon"
    else:
        level, code = "ok", "patent_deadline_ok"
    return {
        "ok": level == "ok",
        "level": level,
        "code": code,
        "patent": "64/124,027",
        "filed_at": _iso(filed) if filed else None,
        "deadline_at": _iso(deadline),
        "days_remaining": days,
        "message": f"{days}d to non-provisional deadline",
    }


def stripe_sku_health() -> dict[str, Any]:
    keys = {
        "secret": bool(os.getenv("STRIPE_SECRET_KEY") or os.getenv("STRIPE_API_KEY")),
        "bind_room": bool(os.getenv("STRIPE_BIND_ROOM_PRICE_ID")),
        "weld": bool(os.getenv("STRIPE_WELD_PRICE_ID")),
        "floor": bool(os.getenv("STRIPE_FLOOR_PRICE_ID")),
        "install": bool(os.getenv("STRIPE_INSTALL_PRICE_ID")),
    }
    missing = [k for k in ("secret", "bind_room") if not keys[k]]
    optional_missing = [k for k in ("weld", "floor") if not keys[k]]
    dev = os.getenv("GATE_DEV_MODE", "").lower() in ("1", "true", "yes")
    if missing:
        return {
            "ok": False,
            "level": "warn" if dev else "fail",
            "code": "stripe_sku_missing",
            "keys": keys,
            "missing": missing,
            "optional_missing": optional_missing,
            "message": "Bind Room checkout not fully configured",
        }
    return {
        "ok": True,
        "level": "warn" if optional_missing else "ok",
        "code": "stripe_sku_ok",
        "keys": keys,
        "optional_missing": optional_missing,
        "message": "Bind Room SKU present"
        + (f"; optional missing: {optional_missing}" if optional_missing else ""),
    }


def buyer_surface_lint(root: Path | None = None) -> dict[str, Any]:
    root = root or Path(__file__).resolve().parent
    findings: list[dict[str, Any]] = []
    for rel in BUYER_TEMPLATES:
        path = root / rel
        if not path.is_file():
            findings.append({"file": rel, "level": "warn", "code": "missing_template"})
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        head = text[:1200]
        if rel.endswith("index.html"):
            if re.search(r"Weld a path", head) and "Bind Room" not in head:
                findings.append({"file": rel, "level": "fail", "code": "home_leads_weld"})
            if "Bind Room" not in text and "bind_room" not in text:
                findings.append({"file": rel, "level": "fail", "code": "home_missing_bind_room_cta"})
        if rel.endswith("bind_room.html"):
            if "Two artifacts" in text:
                findings.append({"file": rel, "level": "fail", "code": "stale_bind_hero"})
            if "block the bind" not in text.lower():
                findings.append({"file": rel, "level": "warn", "code": "bind_missing_buyer_english"})
        if rel.endswith("pricing.html"):
            prices = re.findall(r"\$[\d,]+", text)
            if len(set(prices)) > 5:
                findings.append(
                    {
                        "file": rel,
                        "level": "warn",
                        "code": "price_sprawl",
                        "unique_prices": sorted(set(prices)),
                    }
                )
    fails = [f for f in findings if f.get("level") == "fail"]
    warns = [f for f in findings if f.get("level") == "warn"]
    return {
        "ok": not fails,
        "level": "fail" if fails else ("warn" if warns else "ok"),
        "code": "buyer_surface_lint",
        "findings": findings,
        "message": f"{len(fails)} fail, {len(warns)} warn",
    }


def live_smoke(
    gate_base: str | None = None,
    check_url: str | None = None,
    timeout: float = 12.0,
) -> dict[str, Any]:
    gate_base = (gate_base or os.getenv("GATE_SMOKE_BASE") or "https://gate.velaru.xyz").rstrip("/")
    check_url = check_url or os.getenv("GATE_CHECK_URL") or "https://velaru.xyz/check"
    checks: list[dict[str, Any]] = []

    def one(name: str, url: str, stale: tuple[str, ...], good: tuple[str, ...] = ()) -> None:
        try:
            status, body = _fetch(url, timeout=timeout)
            stale_hit = [p for p in stale if re.search(p, body, re.I | re.S)]
            good_hit = [p for p in good if re.search(p, body, re.I | re.S)]
            if status >= 400:
                checks.append({"name": name, "url": url, "ok": False, "level": "fail", "status": status})
            elif stale_hit:
                checks.append(
                    {
                        "name": name,
                        "url": url,
                        "ok": False,
                        "level": "fail",
                        "status": status,
                        "stale_patterns": stale_hit,
                        "message": "live HTML still has stale copy — deploy lag?",
                    }
                )
            elif good and not good_hit:
                checks.append(
                    {
                        "name": name,
                        "url": url,
                        "ok": False,
                        "level": "warn",
                        "status": status,
                        "message": "expected buyer English not found yet",
                    }
                )
            else:
                checks.append({"name": name, "url": url, "ok": True, "level": "ok", "status": status})
        except (URLError, HTTPError, TimeoutError, OSError) as e:
            checks.append({"name": name, "url": url, "ok": False, "level": "warn", "error": str(e)})

    one("gate_home", f"{gate_base}/", STALE_HOME, GOOD_BIND)
    one("gate_bind_room", f"{gate_base}/bind-room", STALE_BIND, (r"block the bind",))
    one("velaru_check", check_url, STALE_CHECK)

    fails = [c for c in checks if not c.get("ok") and c.get("level") == "fail"]
    warns = [c for c in checks if c.get("level") == "warn"]
    return {
        "ok": not fails,
        "level": "fail" if fails else ("warn" if warns else "ok"),
        "code": "live_smoke",
        "checks": checks,
        "message": f"{len(fails)} fail, {len(warns)} warn on live HTML",
    }


def last_proved_from_db() -> dict[str, Any] | None:
    try:
        try:
            from gate import db as gate_db
        except ImportError:
            import db as gate_db

        row = gate_db.latest_bind_event_any()
        if not row:
            return None
        d = dict(row) if not isinstance(row, dict) else row
        return {
            "last_proved_at": d.get("created_at"),
            "label": "public restraint",
            "href": d.get("verify_url") or None,
            "fuse_id": d.get("fuse_id"),
            "source": "bind_events",
        }
    except Exception as e:  # noqa: BLE001 — ops snapshot must not crash health
        return {"error": str(e), "source": "bind_events"}


def gate1_status() -> dict[str, Any]:
    try:
        try:
            from gate import db as gate_db
        except ImportError:
            import db as gate_db

        rows = [dict(r) for r in gate_db.list_paid_installs(limit=20)]
        n = len(rows)
        latest = rows[0] if rows else None
        return {
            "ok": True,
            "level": "ok" if n else "warn",
            "gate1_met": n > 0,
            "paid_count": n,
            "latest": (
                {
                    "created_at": latest.get("created_at"),
                    "amount_cents": latest.get("amount_cents"),
                    "email_domain": (latest.get("email") or "").split("@")[-1],
                }
                if latest
                else None
            ),
            "message": "Gate 1 met" if n else "Gate 1 open — no paid stranger artifact yet",
        }
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "level": "warn", "gate1_met": False, "error": str(e)}


def snapshot(include_live: bool = False) -> dict[str, Any]:
    parts: dict[str, Any] = {
        "patent": patent_alarm(),
        "stripe": stripe_sku_health(),
        "buyer_lint": buyer_surface_lint(),
        "gate1": gate1_status(),
        "last_proved": last_proved_from_db(),
    }
    if include_live or os.getenv("GATE_OPS_LIVE_SMOKE", "").lower() in ("1", "true", "yes"):
        parts["live_smoke"] = live_smoke()
    levels = [p.get("level") for p in parts.values() if isinstance(p, dict) and "level" in p]
    if "fail" in levels:
        overall = "fail"
    elif "warn" in levels:
        overall = "warn"
    else:
        overall = "ok"
    return {
        "spec": SPEC,
        "overall": overall,
        "ok": overall == "ok",
        "guards": parts,
        "at": _iso(_now()),
    }


def main(argv: list[str] | None = None) -> int:
    argv = list(argv or sys.argv[1:])
    live = "--live" in argv
    snap = snapshot(include_live=live)
    print(json.dumps(snap, indent=2))
    if snap["overall"] == "fail":
        return 2
    if snap["overall"] == "warn":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
