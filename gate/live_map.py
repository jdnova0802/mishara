"""Items 58–68 — live restraint map over located BLOCK events."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

try:
    from gate import large_surfaces as ls
except ImportError:
    import large_surfaces as ls

SPEC = "gate-live-map-v1"
ROLES = ("insurer", "regulator", "internal")
INSURER_KEYS = ("insurance", "mga", "pas", "gl", "wc", "bind")
PALETTES = {
    "default": {"BLOCK": "#f87171", "HOLD": "#fbbf24", "HALT": "#e5e7eb"},
    "cb": {"BLOCK": "#0072B2", "HOLD": "#E69F00", "HALT": "#000000"},
}


def _notes_path() -> Path:
    return Path(os.getenv("GATE_MAP_NOTES_PATH") or Path(__file__).resolve().parent / "data" / "map_notes.json")


def load_notes() -> list[dict[str, Any]]:
    p = _notes_path()
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return list(data.get("notes") or []) if isinstance(data, dict) else []


def add_note(*, event_id: str, text: str, org_only: bool = True) -> dict[str, Any]:
    event_id = (event_id or "").strip()
    text = (text or "").strip()[:500]
    if not event_id or not text:
        raise ValueError("event_id_and_text_required")
    notes = load_notes()
    rec = {"event_id": event_id, "text": text, "org_only": bool(org_only)}
    notes.append(rec)
    p = _notes_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"spec": SPEC, "notes": notes[-200:]}, indent=2), encoding="utf-8")
    return rec


def _chain_len(row: dict[str, Any], by_hash: dict[str, dict[str, Any]]) -> int:
    n = 1
    seen = set()
    cur = row
    while cur and cur.get("prev_receipt_hash") and str(cur.get("id")) not in seen:
        seen.add(str(cur.get("id")))
        nxt = by_hash.get(str(cur.get("prev_receipt_hash")))
        if not nxt:
            break
        n += 1
        cur = nxt
        if n > 32:
            break
    return n


def _vertical(row: dict[str, Any]) -> str:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    return str(hop.get("vertical") or hop.get("line") or hop.get("domain") or "").lower()


def _severity(row: dict[str, Any]) -> float:
    d = str(row.get("decision") or "").upper()
    if d == "HALT":
        return 1.0
    if d == "BLOCK":
        return 0.8
    if d == "HOLD":
        return 0.4
    return 0.0


def view(rows: list[dict[str, Any]], q: dict[str, Any] | None = None) -> dict[str, Any]:
    q = q or {}
    role = (q.get("role") or "regulator").strip().lower()
    if role not in ROLES:
        role = "regulator"
    org = (q.get("org") or "").strip()
    mode = (q.get("view") or "global").strip().lower()
    if mode not in ("mine", "global"):
        mode = "global"
    watch = [p.strip().upper() for p in str(q.get("watch") or "").split(",") if p.strip()]
    until = (q.get("until") or "").strip()
    try:
        min_chain = int(q.get("min_chain") or 0)
    except (TypeError, ValueError):
        min_chain = 0
    try:
        min_severity = float(q.get("min_severity") or 0)
    except (TypeError, ValueError):
        min_severity = 0.0
    palette_name = (q.get("palette") or "default").strip().lower()
    if palette_name not in PALETTES:
        palette_name = "default"
    pin = (q.get("pin") or "").strip()
    try:
        z = float(q.get("z") or 1)
    except (TypeError, ValueError):
        z = 1.0
    try:
        cx = float(q.get("cx") or 400)
        cy = float(q.get("cy") or 200)
    except (TypeError, ValueError):
        cx, cy = 400.0, 200.0

    by_hash = {str(r.get("receipt_hash")): r for r in rows if r.get("receipt_hash")}
    colors = PALETTES[palette_name]
    points = []
    unlocated = 0
    for row in rows:
        if str(row.get("decision") or "").upper() not in ls.HOT:
            continue
        loc = ls.locate(row)
        if not loc["located"]:
            unlocated += 1
            continue
        vert = _vertical(row)
        if role == "insurer" and vert and not any(k in vert for k in INSURER_KEYS):
            continue
        if watch and loc["code"] not in watch:
            continue
        if until and str(row.get("created_at") or "") > until:
            continue
        chain = _chain_len(row, by_hash)
        sev = _severity(row)
        if chain < min_chain or sev < min_severity:
            continue
        mine = bool(org) and str(row.get("fuse_id") or "") == org
        if mode == "mine" and org and not mine:
            continue
        points.append(
            {
                **loc,
                "id": row.get("id"),
                "decision": row.get("decision"),
                "created_at": row.get("created_at"),
                "fuse_id": row.get("fuse_id"),
                "receipt_hash": row.get("receipt_hash"),
                "prev_receipt_hash": row.get("prev_receipt_hash"),
                "reason": (row.get("hop") or {}).get("reason") if isinstance(row.get("hop"), dict) else None,
                "chain_length": chain,
                "severity": sev,
                "mine": mine,
                "dim": bool(org) and mode == "global" and not mine,
                "fill": colors.get(str(row.get("decision") or "").upper(), colors["BLOCK"]),
                "alert": (min_chain > 0 and chain >= min_chain)
                or (min_severity > 0 and sev >= min_severity),
            }
        )

    by_pt_hash = {p["receipt_hash"]: p for p in points if p.get("receipt_hash")}
    edges = []
    for p in points:
        prev = p.get("prev_receipt_hash")
        src = by_pt_hash.get(prev) if prev else None
        if src:
            edges.append(
                {
                    "from": src["id"],
                    "to": p["id"],
                    "x1": src["x"],
                    "y1": src["y"],
                    "x2": p["x"],
                    "y2": p["y"],
                }
            )

    detail = next((p for p in points if str(p.get("id")) == pin), points[-1] if points and pin else None)
    notes = load_notes()
    if role != "internal":
        notes = [n for n in notes if not n.get("org_only")]
    query = {
        "role": role,
        "org": org,
        "view": mode,
        "watch": ",".join(watch),
        "until": until,
        "min_chain": min_chain,
        "min_severity": min_severity,
        "palette": palette_name,
        "pin": pin,
        "cx": cx,
        "cy": cy,
        "z": z,
    }
    deep = "/map?" + urlencode({k: v for k, v in query.items() if v not in ("", 0, 0.0, None)})
    return {
        "spec": SPEC,
        "projection": "equirectangular",
        "role": role,
        "view": mode,
        "palette": palette_name,
        "colors": colors,
        "camera": {"cx": cx, "cy": cy, "z": z},
        "points": points,
        "edges": edges,
        "unlocated": unlocated,
        "detail": detail,
        "notes": notes,
        "deep_link": deep,
        "plain": (
            "Pan/zoom the world plate. Pins are located BLOCK/HOLD/HALT only. "
            "Dashed edges follow prev_receipt_hash. Unlocated events stay counted, not invented."
        ),
    }
