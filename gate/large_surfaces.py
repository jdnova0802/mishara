"""Items 28–36 — public surfaces. Honest about what is not built yet."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

try:
    from gate import weld
except ImportError:
    import weld

MAP_SPEC = "gate-restraint-map-v1"
BOARD_SPEC = "gate-cdpi-board-counts-v1"
FEED_SPEC = "gate-block-feed-v1"
EXPOSURE_SPEC = "gate-ungated-exposure-v1"
TWIN_SPEC = "gate-digital-twin-v1"
SKIN_SPEC = "gate-trust-skin-v1"
COMPANION_SPEC = "gate-companion-receipt-v1"
DATING_SPEC = "gate-dating-receipt-v1"

# Approximate lon/lat. Unlisted jurisdictions stay unlocated — no invented pins.
STATE_LONLAT: dict[str, tuple[float, float]] = {
    "AL": (-86.7, 32.6),
    "AK": (-152.0, 64.0),
    "AZ": (-111.6, 34.0),
    "AR": (-92.4, 34.8),
    "CA": (-119.5, 37.2),
    "CO": (-105.5, 39.0),
    "CT": (-72.7, 41.6),
    "DE": (-75.5, 39.0),
    "FL": (-81.7, 27.8),
    "GA": (-83.4, 32.9),
    "HI": (-157.5, 20.8),
    "ID": (-114.5, 44.0),
    "IL": (-89.2, 40.0),
    "IN": (-86.3, 40.0),
    "IA": (-93.5, 42.0),
    "KS": (-98.3, 38.5),
    "KY": (-84.7, 37.8),
    "LA": (-91.8, 31.0),
    "ME": (-69.2, 45.3),
    "MD": (-76.7, 39.0),
    "MA": (-71.8, 42.2),
    "MI": (-84.6, 43.7),
    "MN": (-94.6, 46.0),
    "MS": (-89.7, 32.7),
    "MO": (-92.5, 38.4),
    "MT": (-110.0, 47.0),
    "NE": (-99.8, 41.5),
    "NV": (-117.0, 39.0),
    "NH": (-71.6, 43.7),
    "NJ": (-74.6, 40.2),
    "NM": (-106.0, 34.2),
    "NY": (-75.5, 42.9),
    "NC": (-79.8, 35.6),
    "ND": (-100.5, 47.5),
    "OH": (-82.8, 40.3),
    "OK": (-97.5, 35.5),
    "OR": (-120.5, 44.0),
    "PA": (-77.8, 40.9),
    "RI": (-71.5, 41.7),
    "SC": (-80.9, 33.9),
    "SD": (-100.2, 44.5),
    "TN": (-86.3, 35.8),
    "TX": (-99.3, 31.5),
    "UT": (-111.7, 39.3),
    "VT": (-72.7, 44.0),
    "VA": (-78.2, 37.5),
    "WA": (-120.7, 47.4),
    "WV": (-80.6, 38.6),
    "WI": (-89.8, 44.5),
    "WY": (-107.6, 43.0),
    "DC": (-77.0, 38.9),
    "GB": (-2.0, 54.0),
    "UK": (-2.0, 54.0),
}

HOT = {"BLOCK", "HALT", "HOLD"}
SPORTS_KEYS = (
    "sport",
    "sports",
    "betting",
    "prediction",
    "kalshi",
    "polymarket",
    "odds",
    "bookmaker",
)


def _lonlat_to_xy(lon: float, lat: float, w: float = 800.0, h: float = 400.0) -> tuple[float, float]:
    x = (lon + 180.0) / 360.0 * w
    y = (90.0 - lat) / 180.0 * h
    return round(x, 1), round(y, 1)


def _code_from_row(row: dict[str, Any]) -> str:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    checks = hop.get("checks") if isinstance(hop.get("checks"), dict) else {}
    raw = hop.get("state") or hop.get("jurisdiction") or checks.get("state") or ""
    return str(raw).strip().upper()


def locate(row: dict[str, Any]) -> dict[str, Any]:
    code = _code_from_row(row)
    if code in STATE_LONLAT:
        lon, lat = STATE_LONLAT[code]
        x, y = _lonlat_to_xy(lon, lat)
        return {
            "located": True,
            "code": code,
            "lon": lon,
            "lat": lat,
            "x": x,
            "y": y,
        }
    return {"located": False, "code": code or None}


def restraint_map(rows: list[dict[str, Any]]) -> dict[str, Any]:
    points = []
    unlocated = 0
    for row in rows:
        if str(row.get("decision") or "").upper() not in HOT:
            continue
        loc = locate(row)
        if not loc["located"]:
            unlocated += 1
            continue
        points.append(
            {
                **loc,
                "id": row.get("id"),
                "decision": row.get("decision"),
                "created_at": row.get("created_at"),
                "fuse_id": row.get("fuse_id"),
            }
        )
    return {
        "spec": MAP_SPEC,
        "projection": "equirectangular",
        "points": points,
        "unlocated": unlocated,
        "plain": (
            "Pins are BLOCK/HOLD/HALT events that already carry a two-letter jurisdiction. "
            "Unlocated events are counted, not invented."
        ),
    }


def leaderboard(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_fuse: dict[str, dict[str, Any]] = {}
    for row in rows:
        fid = str(row.get("fuse_id") or "unknown")
        slot = by_fuse.setdefault(
            fid,
            {"fuse_id": fid, "allow": 0, "block": 0, "hold": 0, "halt": 0, "last_decision": None, "last_event_id": None},
        )
        d = str(row.get("decision") or "").upper()
        if d == "ALLOW":
            slot["allow"] += 1
        elif d == "BLOCK":
            slot["block"] += 1
        elif d == "HOLD":
            slot["hold"] += 1
        elif d == "HALT":
            slot["halt"] += 1
        slot["last_decision"] = d or slot["last_decision"]
        slot["last_event_id"] = row.get("id")
    agents = sorted(
        by_fuse.values(),
        key=lambda a: (a["block"] + a["halt"], a["hold"], a["allow"]),
        reverse=True,
    )
    return {
        "spec": BOARD_SPEC,
        "methodology": "event_counts_not_cdpi_v1",
        "cdpi_items_pending": [75, 76, 77, 78, 79],
        "plain": "This board is raw ALLOW/BLOCK/HOLD/HALT counts. It is not the CDPI score from items 75–79.",
        "agents": agents,
    }


def sports_feed(rows: list[dict[str, Any]]) -> dict[str, Any]:
    hits = []
    for row in rows:
        if str(row.get("decision") or "").upper() not in HOT:
            continue
        blob = (json.dumps(row.get("hop") or {}, default=str) + " " + str(row.get("fuse_id") or "")).lower()
        if any(k in blob for k in SPORTS_KEYS):
            hits.append(
                {
                    "id": row.get("id"),
                    "decision": row.get("decision"),
                    "created_at": row.get("created_at"),
                    "fuse_id": row.get("fuse_id"),
                }
            )
    return {
        "spec": FEED_SPEC,
        "audience": "prediction_markets_sports",
        "events": hits,
        "empty_is_honest": True,
        "plain": (
            "Blocks whose hop names sports, odds, or a prediction market. "
            "Empty means this mouth has not printed one — not a hidden ticker."
        ),
    }


def exposure(*, notional: float, unauthorized_per_year: float, loss_fraction: float = 1.0) -> dict[str, Any]:
    dollars = float(notional) * float(unauthorized_per_year) * float(loss_fraction)
    return {
        "spec": EXPOSURE_SPEC,
        "notional": float(notional),
        "unauthorized_per_year": float(unauthorized_per_year),
        "loss_fraction": float(loss_fraction),
        "dollars": dollars,
        "not_a_quote": True,
        "plain": (
            f"${dollars:,.0f} if {float(unauthorized_per_year):g} ungated writes "
            f"each move ${float(notional):,.0f}."
        ),
    }


def twin(body: dict[str, Any]) -> dict[str, Any]:
    hop = body.get("hop") if isinstance(body.get("hop"), dict) else {"verdict": True, "state": "LIVE"}
    try:
        status = int(body.get("status") or 200)
    except (TypeError, ValueError):
        status = 200
    plan = weld.mga_authority(
        hop,
        status,
        premium=_num(body.get("premium")),
        authority_limit=_num(body.get("authority_limit")),
        line=body.get("line"),
        state=body.get("state"),
        allowed_lines=body.get("allowed_lines") if isinstance(body.get("allowed_lines"), list) else None,
        allowed_states=body.get("allowed_states") if isinstance(body.get("allowed_states"), list) else None,
        mga_contract_terminated=body.get("mga_contract_terminated"),
        commissioner_notice_within_30_days=body.get("commissioner_notice_within_30_days"),
    )
    return {
        "spec": TWIN_SPEC,
        "dry_run": True,
        "recorded": False,
        "their_production": False,
        "plain": "No bind event was written. This is the rule engine against a posted hop.",
        "plan": plan,
    }


def _num(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _skins_path() -> Path:
    return Path(os.getenv("GATE_TRUST_SKINS_PATH") or Path(__file__).resolve().parent / "data" / "trust_skins.json")


def load_skins() -> dict[str, Any]:
    p = _skins_path()
    if not p.exists():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(data.get("skins") or {}) if isinstance(data, dict) else {}


def get_skin(slug: str) -> dict[str, Any] | None:
    slug = (slug or "").strip().lower()
    if not slug:
        return None
    skins = load_skins()
    skin = skins.get(slug)
    if not isinstance(skin, dict):
        return None
    return {
        "spec": SKIN_SPEC,
        "slug": slug,
        "name": skin.get("name") or slug,
        "tagline": skin.get("tagline") or "",
        "fuse_ids": list(skin.get("fuse_ids") or []),
        "dns": "not_edited",
        "plain": "This is a path on this mouth. It is not a new company and not a DNS change.",
    }


def save_skin(*, slug: str, name: str, tagline: str = "", fuse_ids: list | None = None) -> dict[str, Any]:
    slug = (slug or "").strip().lower()
    if not slug or not name.strip():
        raise ValueError("slug_and_name_required")
    skins = load_skins()
    skins[slug] = {
        "name": name.strip(),
        "tagline": (tagline or "").strip(),
        "fuse_ids": [str(x) for x in (fuse_ids or [])],
    }
    p = _skins_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"spec": SKIN_SPEC, "skins": skins}, indent=2), encoding="utf-8")
    out = get_skin(slug)
    if not out:
        raise ValueError("save_failed")
    return out


def filter_skin_events(rows: list[dict[str, Any]], skin: dict[str, Any]) -> list[dict[str, Any]]:
    wanted = {str(x) for x in (skin.get("fuse_ids") or []) if x}
    if not wanted:
        return rows
    return [r for r in rows if str(r.get("fuse_id") or "") in wanted]


def companion_status(row: dict[str, Any] | None) -> dict[str, Any]:
    if not row:
        return {
            "spec": COMPANION_SPEC,
            "ok": False,
            "emergency": False,
            "plain": "No receipt for that id on this mouth. This page is not emergency services.",
        }
    decision = row.get("decision")
    return {
        "spec": COMPANION_SPEC,
        "ok": True,
        "emergency": False,
        "event_id": row.get("id"),
        "decision": decision,
        "receipt_hash": row.get("receipt_hash"),
        "plain": (
            f"This mouth printed {decision} as event {row.get('id')}. "
            "Open the verify URL. This is a receipt check, not a crisis line."
        ),
    }


def dating_status(row: dict[str, Any] | None) -> dict[str, Any]:
    if not row:
        return {
            "spec": DATING_SPEC,
            "ok": False,
            "catfish_model": False,
            "receipt_present": False,
            "confidence_kind": "receipt_presence_only",
            "plain": (
                "No signed receipt for that id. Gate does not run face match or reverse-image search. "
                "Those are items 45–47, research."
            ),
        }
    return {
        "spec": DATING_SPEC,
        "ok": True,
        "catfish_model": False,
        "receipt_present": True,
        "confidence_kind": "receipt_presence_only",
        "event_id": row.get("id"),
        "decision": row.get("decision"),
        "receipt_hash": row.get("receipt_hash"),
        "plain": (
            "A signed receipt exists for this id. That is not a catfish score and not a photo check."
        ),
    }
