"""Items 134–135 — case workspace and alert-to-human triage.

Bundles 132 receipts and 133 flags. Triage severity is set at enrichment,
not at ingest, and never auto-acted. Disposition always needs a reason.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

CASE_SPEC = "gate-case-file-v1"
TRIAGE_SPEC = "gate-triage-v1"

STATUSES = ("OPEN", "CLOSED", "ESCALATED")
SOURCES = ("anomaly_flag", "counter_case_score", "kudurru_watch")
SEVERITIES = ("LOW", "MEDIUM", "HIGH", "CRITICAL")
DISPOSITIONS = ("ESCALATE", "MONITOR", "CLOSE_NON_ACTIONABLE")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_CASE_PATH") or Path(__file__).resolve().parent / "data" / "cases.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": CASE_SPEC, "cases": [], "triage": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": CASE_SPEC, "cases": [], "triage": []}
    if not isinstance(data, dict):
        return {"spec": CASE_SPEC, "cases": [], "triage": []}
    data.setdefault("cases", [])
    data.setdefault("triage", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def list_cases() -> list[dict[str, Any]]:
    return list(_load().get("cases") or [])


def list_triage() -> list[dict[str, Any]]:
    return list(_load().get("triage") or [])


def get_case(case_id: str) -> dict[str, Any] | None:
    cid = (case_id or "").strip()
    for row in list_cases():
        if row.get("case_id") == cid:
            return row
    return None


def get_triage(triage_id: str) -> dict[str, Any] | None:
    tid = (triage_id or "").strip()
    for row in list_triage():
        if row.get("triage_id") == tid:
            return row
    return None


def _ids(raw: Any) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(x).strip() for x in raw if str(x).strip()]


def open_case(
    *,
    opened_by: str,
    hypothesis: str,
    linked_receipt_ids: Any = None,
    linked_anomaly_flag_ids: Any = None,
    linked_link_graph_query_id: str | None = None,
) -> dict[str, Any]:
    who = (opened_by or "").strip()
    hyp = sanitize_mod.strip_agent(hypothesis)
    receipts = _ids(linked_receipt_ids)
    flags = _ids(linked_anomaly_flag_ids)
    if not who or not hyp:
        return {
            "spec": CASE_SPEC,
            "ok": False,
            "error": "fields_required",
            "plain": "A case needs an opener and a dated hypothesis. It is not an unlabeled pile of receipts.",
        }
    if not receipts and not flags:
        return {
            "spec": CASE_SPEC,
            "ok": False,
            "error": "nothing_to_bundle",
            "plain": "Bundle at least one 132 receipt id or 133 anomaly flag. Do not open an empty workspace.",
        }
    rec = {
        "spec": CASE_SPEC,
        "ok": True,
        "case_id": "case_" + uuid.uuid4().hex[:12],
        "opened_by": who,
        "opened_at": _iso(),
        "status": "OPEN",
        "hypothesis": hyp,
        "linked_receipt_ids": receipts,
        "linked_anomaly_flag_ids": flags,
        "linked_link_graph_query_id": (linked_link_graph_query_id or "").strip() or None,
        "case_notes": [],
        "resolution": None,
        "resolved_at": None,
        "plain": "Working case. CLOSE needs a resolution. Competing hypotheses are item 146, not this surface.",
    }
    store = _load()
    store["cases"].append(rec)
    _save(store)
    return rec


def add_note(*, case_id: str, author: str, body: str) -> dict[str, Any]:
    store = _load()
    row = next((c for c in store["cases"] if c.get("case_id") == (case_id or "").strip()), None)
    if not row:
        return {"spec": CASE_SPEC, "ok": False, "error": "case_not_found", "plain": "Unknown case_id."}
    who = (author or "").strip()
    text = sanitize_mod.strip_agent(body)
    if not who or not text:
        return {"spec": CASE_SPEC, "ok": False, "error": "note_required", "plain": "Notes need an author and a body."}
    note = {
        "note_id": "note_" + uuid.uuid4().hex[:12],
        "author": who,
        "body": text,
        "created_at": _iso(),
    }
    row.setdefault("case_notes", []).append(note)
    _save(store)
    return {**row, "ok": True, "note": note}


def set_status(*, case_id: str, status: str, resolution: str | None = None) -> dict[str, Any]:
    st = (status or "").strip().upper()
    if st not in STATUSES:
        return {"spec": CASE_SPEC, "ok": False, "error": "status_unknown", "plain": "OPEN, CLOSED, or ESCALATED."}
    store = _load()
    row = next((c for c in store["cases"] if c.get("case_id") == (case_id or "").strip()), None)
    if not row:
        return {"spec": CASE_SPEC, "ok": False, "error": "case_not_found", "plain": "Unknown case_id."}
    if st == "CLOSED" and not sanitize_mod.strip_agent(resolution or row.get("resolution")):
        return {
            "spec": CASE_SPEC,
            "ok": False,
            "error": "resolution_required",
            "plain": "CLOSED needs a resolution. Never left blank.",
        }
    row["status"] = st
    if st == "CLOSED":
        row["resolution"] = sanitize_mod.strip_agent(resolution or row.get("resolution"))
        row["resolved_at"] = _iso()
    if st == "ESCALATED":
        row["status"] = "ESCALATED"
    _save(store)
    return {**row, "ok": True}


def ingest_triage(
    *,
    source: str,
    source_id: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = extra if isinstance(extra, dict) else {}
    src = (source or "").strip()
    sid = (source_id or "").strip()
    if src not in SOURCES:
        return {
            "spec": TRIAGE_SPEC,
            "ok": False,
            "error": "source_unknown",
            "plain": "Source is anomaly_flag, counter_case_score, or kudurru_watch.",
        }
    if not sid:
        return {"spec": TRIAGE_SPEC, "ok": False, "error": "source_id_required", "plain": "Triage points at a source id."}
    if body.get("severity") not in (None, "", False):
        return {
            "spec": TRIAGE_SPEC,
            "ok": False,
            "error": "severity_at_ingest_refused",
            "plain": "Severity is set at enrichment, not at raw detection. Do not invent a desk cutoff.",
        }
    rec = {
        "spec": TRIAGE_SPEC,
        "ok": True,
        "triage_id": "tri_" + uuid.uuid4().hex[:12],
        "source": src,
        "source_id": sid,
        "severity": None,
        "context": None,
        "assigned_to": None,
        "disposition": None,
        "disposition_reason": None,
        "disposed_at": None,
        "ingested_at": _iso(),
        "never_auto_acted": True,
        "plain": "Ingested. Unassigned, unrated. A human has to enrich it before disposition.",
    }
    store = _load()
    store["triage"].append(rec)
    _save(store)
    return rec


def enrich_triage(
    *,
    triage_id: str,
    severity: str,
    actor_history_ref: str | None = None,
    asset_criticality: str | None = None,
    recent_related_flags: Any = None,
) -> dict[str, Any]:
    sev = (severity or "").strip().upper()
    if sev not in SEVERITIES:
        return {
            "spec": TRIAGE_SPEC,
            "ok": False,
            "error": "severity_unknown",
            "plain": "LOW, MEDIUM, HIGH, or CRITICAL — named by a human, not a sigma table.",
        }
    store = _load()
    row = next((t for t in store["triage"] if t.get("triage_id") == (triage_id or "").strip()), None)
    if not row:
        return {"spec": TRIAGE_SPEC, "ok": False, "error": "triage_not_found", "plain": "Unknown triage_id."}
    row["severity"] = sev
    row["context"] = {
        "actor_history_ref": (actor_history_ref or "").strip() or None,
        "asset_criticality": sanitize_mod.strip_agent(asset_criticality) or None,
        "recent_related_flags": _ids(recent_related_flags),
    }
    row["plain"] = "Enriched. Still not auto-acted."
    _save(store)
    return {**row, "ok": True}


def claim_triage(*, triage_id: str, assigned_to: str) -> dict[str, Any]:
    who = (assigned_to or "").strip()
    if not who:
        return {"spec": TRIAGE_SPEC, "ok": False, "error": "assignee_required", "plain": "Claim needs a person."}
    store = _load()
    row = next((t for t in store["triage"] if t.get("triage_id") == (triage_id or "").strip()), None)
    if not row:
        return {"spec": TRIAGE_SPEC, "ok": False, "error": "triage_not_found", "plain": "Unknown triage_id."}
    row["assigned_to"] = who
    _save(store)
    return {**row, "ok": True}


def dispose_triage(*, triage_id: str, disposition: str, disposition_reason: str) -> dict[str, Any]:
    disp = (disposition or "").strip().upper()
    reason = sanitize_mod.strip_agent(disposition_reason)
    if disp not in DISPOSITIONS:
        return {"spec": TRIAGE_SPEC, "ok": False, "error": "disposition_unknown", "plain": "ESCALATE, MONITOR, or CLOSE_NON_ACTIONABLE."}
    if not reason:
        return {
            "spec": TRIAGE_SPEC,
            "ok": False,
            "error": "disposition_reason_required",
            "plain": "Never closed silently. Same doctrine as item 115.",
        }
    store = _load()
    row = next((t for t in store["triage"] if t.get("triage_id") == (triage_id or "").strip()), None)
    if not row:
        return {"spec": TRIAGE_SPEC, "ok": False, "error": "triage_not_found", "plain": "Unknown triage_id."}
    if not row.get("severity"):
        return {
            "spec": TRIAGE_SPEC,
            "ok": False,
            "error": "enrich_first",
            "plain": "Disposition waits on enrichment. Raw ingest has no severity.",
        }
    row["disposition"] = disp
    row["disposition_reason"] = reason
    row["disposed_at"] = _iso()
    row["plain"] = "Disposed. Not auto-acted. Reason is on the record."
    _save(store)
    return {**row, "ok": True}
