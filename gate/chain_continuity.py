"""Hash-chain continuity audit — diagnostic, not a new product.

Negative proof depends on completeness. A broken prev_receipt_hash link is
a real hole. A sparse demo log with quiet hours is not, by itself, a hole.

Sep 1 2026 window: answer whether the chain's *links* broke across that day.
If broken, write an honest corrections ledger entry dated when we found it.
Do not paper over it.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPEC = "gate-chain-corrections-v1"
# Full UTC day Claude flagged; exact 20-minute 500 window was not recorded here.
SEP1_WINDOW = {
    "start": "2026-09-01T00:00:00+00:00",
    "end": "2026-09-02T00:00:00+00:00",
    "note": "Sep 1 2026 UTC day covering reported 500s; exact minute window unknown",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def corrections_path() -> Path:
    db_path = os.getenv("GATE_DB_PATH", "./gate.db")
    return Path(db_path).resolve().parent / "chain_corrections.json"


def load_corrections() -> dict[str, Any]:
    path = corrections_path()
    if not path.is_file():
        return {"spec": SPEC, "entries": [], "updated_at": None}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"spec": SPEC, "entries": [], "updated_at": None, "read_error": True}
    if not isinstance(data, dict):
        return {"spec": SPEC, "entries": [], "updated_at": None, "read_error": True}
    data.setdefault("spec", SPEC)
    data.setdefault("entries", [])
    return data


def save_corrections(doc: dict[str, Any]) -> Path:
    path = corrections_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = dict(doc)
    doc["spec"] = SPEC
    doc["updated_at"] = _utc_now()
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def audit_link_integrity(rows: list[dict]) -> dict[str, Any]:
    """Oldest-first rows with receipt_hash. Check prev_receipt_hash chain."""
    ordered = sorted(
        [r for r in rows if r.get("receipt_hash")],
        key=lambda r: (r.get("created_at") or "", r.get("id") or ""),
    )
    broken: list[dict[str, Any]] = []
    prev_hash = None
    for i, row in enumerate(ordered):
        expected_prev = prev_hash
        got_prev = row.get("prev_receipt_hash")
        if i == 0:
            # First leaf may have null prev.
            if got_prev not in (None, ""):
                # Allow first event to point at nothing only; non-null with empty log is odd but not a mid-chain break.
                pass
        elif got_prev != expected_prev:
            broken.append(
                {
                    "index": i,
                    "event_id": row.get("id"),
                    "created_at": row.get("created_at"),
                    "expected_prev": expected_prev,
                    "got_prev": got_prev,
                    "receipt_hash": row.get("receipt_hash"),
                }
            )
        prev_hash = row.get("receipt_hash")
    return {
        "spec": "gate-chain-link-audit-v1",
        "event_count": len(ordered),
        "broken_link_count": len(broken),
        "ok": len(broken) == 0,
        "broken_links": broken,
    }


def events_in_window(rows: list[dict], start: str, end: str) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        ts = r.get("created_at") or ""
        if start <= ts < end:
            out.append(
                {
                    "id": r.get("id"),
                    "created_at": ts,
                    "receipt_hash": r.get("receipt_hash"),
                    "decision": r.get("decision"),
                }
            )
    return out


def audit_sep1_window(rows: list[dict]) -> dict[str, Any]:
    link = audit_link_integrity(rows)
    start = SEP1_WINDOW["start"]
    end = SEP1_WINDOW["end"]
    in_window = events_in_window(rows, start, end)
    broken_in_or_spanning = [
        b
        for b in link.get("broken_links") or []
        if (b.get("created_at") or "") >= start and (b.get("created_at") or "") < end
    ]
    # Honest read: sparse logs do not prove outage holes; broken links do.
    if broken_in_or_spanning or (not link["ok"] and link["broken_link_count"]):
        # Any broken link is material; flag if any exist at all, with window detail separate.
        result = "broken_links"
        severity = "material"
    else:
        result = "no_broken_links"
        severity = "clear"

    return {
        "spec": "gate-sep1-continuity-audit-v1",
        "audited_at": _utc_now(),
        "window": SEP1_WINDOW,
        "result": result,
        "severity": severity,
        "events_in_window": len(in_window),
        "events_in_window_sample": in_window[:20],
        "link_audit": {
            "event_count": link["event_count"],
            "broken_link_count": link["broken_link_count"],
            "ok": link["ok"],
            "broken_links": link["broken_links"][:50],
        },
        "interpretation": (
            "Broken prev_receipt_hash links are chain holes."
            if severity == "material"
            else (
                "No broken prev_receipt_hash links. "
                "Sparse or zero events on Sep 1 is not itself a hash-chain hole; "
                "it means no receipt was appended in that window on this database."
            )
        ),
    }


def record_sep1_audit(rows: list[dict], *, force: bool = False) -> dict[str, Any]:
    """Run Sep 1 audit; append corrections entry if material or none exists yet."""
    audit = audit_sep1_window(rows)
    doc = load_corrections()
    entries = list(doc.get("entries") or [])
    already = [
        e
        for e in entries
        if e.get("kind") == "sep1_2026_continuity" and e.get("window", {}).get("start") == SEP1_WINDOW["start"]
    ]
    if already and not force:
        return {
            "audit": audit,
            "corrections": doc,
            "wrote": False,
            "reason": "already_recorded",
        }

    entry = {
        "id": str(uuid.uuid4()),
        "kind": "sep1_2026_continuity",
        "dated": _utc_now()[:10],
        "recorded_at": _utc_now(),
        "window": SEP1_WINDOW,
        "result": audit["result"],
        "severity": audit["severity"],
        "events_in_window": audit["events_in_window"],
        "broken_link_count": audit["link_audit"]["broken_link_count"],
        "broken_links": audit["link_audit"]["broken_links"],
        "interpretation": audit["interpretation"],
    }
    if severity_is_material(audit):
        entry["correction"] = (
            "Material chain discontinuity found. Do not paper over. "
            "Negative proof covering this window is incomplete until addressed."
        )
    else:
        entry["correction"] = None
        entry["note"] = "Diagnostic clear on link integrity for this database snapshot."

    # Replace prior sep1 entry when force, else append.
    if force:
        entries = [e for e in entries if e.get("kind") != "sep1_2026_continuity"]
    entries.append(entry)
    doc["entries"] = entries
    path = save_corrections(doc)
    return {"audit": audit, "corrections": doc, "wrote": True, "path": str(path), "entry": entry}


def severity_is_material(audit: dict[str, Any]) -> bool:
    return audit.get("severity") == "material" or audit.get("result") == "broken_links"
