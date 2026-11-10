"""Public corrections ledger (bugs 7, 11) + item 98 dogfood of Verra retired.

Same shape as a dispute: versions append, status changes, history is never erased.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-corrections-ledger-v1"

SEED = (
    {
        "date": "2026-08-17",
        "id": "verra-name-retired",
        "status": "open_until_demo_copy_clears",
        "claim": "Public name is Velaru. Gate is the commercial mouth. The name Verra is retired.",
        "live_contradiction": (
            "velaru.xyz/demo/bind-room still mints session ids prefixed verra- and "
            "downloads verra-bind-room-*.json. Gate's demo uses bind- prefixes."
        ),
        "resolution": (
            "Bind Room is the live product name. /verra on velaru is an alias, not a sixth brand. "
            "Kudurru (consumer card) is a later brand and is not Verra revived."
        ),
    },
    {
        "date": "2026-08-26",
        "id": "verra-route-retired",
        "status": "resolved_on_gate",
        "claim": "The Bind Room door is gate.velaru.xyz/bind-room (paid officer pack) and /demo/bind-room (free vertical demo).",
        "live_contradiction": None,
        "resolution": "Gate /trust/corrections is this ledger. It does not redirect.",
    },
    {
        "date": "2026-11-10",
        "id": "mandate-registry-was-insurance",
        "status": "resolved_on_gate",
        "claim": "/compliance/mandate-registry is a registry of mandates, not the insurance marketing page.",
        "live_contradiction": "velaru.xyz/compliance/mandate-registry currently 301s to /insurance.",
        "resolution": "Gate serves /compliance/mandate-registry as a list. Velaru site still needs the same fix.",
    },
)

# Compat for existing tests that iterate ENTRIES.
ENTRIES = SEED


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_CORRECTIONS_PATH") or Path(__file__).resolve().parent / "data" / "corrections_ledger.json")


def _seed_row(src: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": src["id"],
        "date": src["date"],
        "status": src["status"],
        "claim": src["claim"],
        "live_contradiction": src.get("live_contradiction"),
        "resolution": src.get("resolution"),
        "history_erased": False,
        "versions": [
            {
                "at": src["date"] + "T00:00:00+00:00",
                "status": src["status"],
                "note": "seed",
            }
        ],
    }


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "rows": [_seed_row(dict(s)) for s in SEED]}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "rows": [_seed_row(dict(s)) for s in SEED]}
    rows = list(data.get("rows") or []) if isinstance(data, dict) else []
    known = {r.get("id") for r in rows}
    for src in SEED:
        if src["id"] not in known:
            rows.append(_seed_row(dict(src)))
    return {"spec": SPEC, "rows": rows}


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def ledger() -> dict[str, Any]:
    store = _load()
    rows = []
    for row in store["rows"]:
        rec = dict(row)
        rec["claim"] = sanitize_mod.strip_agent(rec.get("claim"))
        rec["resolution"] = sanitize_mod.strip_agent(rec.get("resolution"))
        rec["live_contradiction"] = (
            sanitize_mod.strip_agent(rec["live_contradiction"]) if rec.get("live_contradiction") else None
        )
        rec["history_erased"] = False
        rec["versions"] = list(rec.get("versions") or [])
        rows.append(rec)
    verra = next((r for r in rows if r["id"] == "verra-name-retired"), None)
    return {
        "spec": SPEC,
        "plain": (
            "Verra retired is tracked here the same way a disputed BLOCK is: "
            "versions append, the row stays, history is never erased."
        ),
        "rows": rows,
        "verra_retired": verra,
    }


def append_version(entry_id: str, *, status: str, note: str) -> dict[str, Any]:
    entry_id = (entry_id or "").strip()
    status = sanitize_mod.strip_agent(status, limit=80)
    note = sanitize_mod.strip_agent(note, limit=500)
    if not entry_id or not status:
        raise ValueError("entry_id_and_status_required")
    store = _load()
    for rec in store["rows"]:
        if rec.get("id") == entry_id:
            rec["status"] = status
            rec["history_erased"] = False
            rec.setdefault("versions", []).append({"at": _now(), "status": status, "note": note or None})
            _save(store)
            return rec
    raise ValueError("not_found")
