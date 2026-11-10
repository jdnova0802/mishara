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
ACH_SPEC = "gate-competing-hypothesis-v1"
OSINT_SPEC = "gate-osint-v1"
EVIDENTIARY_WEIGHT = "CORROBORATING_ONLY"
HARD_BINDING = False
SOURCE_CATEGORIES = ("social_media", "public_records", "news_media", "geospatial", "technical_infra")

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
        return {"spec": CASE_SPEC, "cases": [], "triage": [], "osint": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": CASE_SPEC, "cases": [], "triage": [], "osint": []}
    if not isinstance(data, dict):
        return {"spec": CASE_SPEC, "cases": [], "triage": [], "osint": []}
    data.setdefault("cases", [])
    data.setdefault("triage", [])
    data.setdefault("osint", [])
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
        "competing_hypotheses": [],
        "osint_corroboration_ids": [],
        "resolution": None,
        "resolved_at": None,
        "plain": "Working case. CLOSE/ESCALATE needs a weighed deception hypothesis (146). OSINT is corroborating only.",
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


def _has_deception(row: dict[str, Any]) -> bool:
    return any(h.get("is_deception_hypothesis") for h in (row.get("competing_hypotheses") or []))


def add_hypothesis(
    *,
    case_id: str,
    hypothesis_text: str,
    is_deception_hypothesis: Any,
    diagnostic_evidence_for: Any = None,
    diagnostic_evidence_against: Any = None,
    weight: Any = None,
) -> dict[str, Any]:
    text = sanitize_mod.strip_agent(hypothesis_text)
    if not text:
        return {
            "spec": ACH_SPEC,
            "ok": False,
            "error": "hypothesis_required",
            "plain": "ACH needs a named explanation, not a blank slot.",
        }
    if is_deception_hypothesis not in (True, False):
        return {
            "spec": ACH_SPEC,
            "ok": False,
            "error": "deception_flag_required",
            "plain": "Say whether this is the staged-to-mislead hypothesis. Not an afterthought.",
        }
    try:
        w = float(weight)
    except (TypeError, ValueError):
        return {
            "spec": ACH_SPEC,
            "ok": False,
            "error": "weight_required",
            "plain": "Weight is 0.0–1.0. Zero still counts as weighed, including a rejected deception hypothesis.",
        }
    if w < 0 or w > 1:
        return {"spec": ACH_SPEC, "ok": False, "error": "weight_range", "plain": "Weight is 0.0–1.0."}
    store = _load()
    row = next((c for c in store["cases"] if c.get("case_id") == (case_id or "").strip()), None)
    if not row:
        return {"spec": ACH_SPEC, "ok": False, "error": "case_not_found", "plain": "Unknown case_id."}
    rec = {
        "spec": ACH_SPEC,
        "ok": True,
        "hypothesis_id": "hyp_" + uuid.uuid4().hex[:12],
        "case_id": row["case_id"],
        "hypothesis_text": text,
        "is_deception_hypothesis": bool(is_deception_hypothesis),
        "diagnostic_evidence_for": _ids(diagnostic_evidence_for),
        "diagnostic_evidence_against": _ids(diagnostic_evidence_against),
        "weight": w,
        "logged_at": _iso(),
        "plain": (
            "Deception hypothesis on the record. CLOSE/ESCALATE may proceed even if this weight is zero."
            if is_deception_hypothesis
            else "Competing explanation logged."
        ),
    }
    row.setdefault("competing_hypotheses", []).append(rec)
    _save(store)
    return rec


def add_osint(
    *,
    finding: str,
    source_category: str,
    source_url: str,
    independence_verified: Any,
    case_id: str | None = None,
    campaign_cluster_id: str | None = None,
) -> dict[str, Any]:
    cat = (source_category or "").strip()
    if cat not in SOURCE_CATEGORIES:
        return {
            "spec": OSINT_SPEC,
            "ok": False,
            "error": "source_category_unknown",
            "plain": "social_media, public_records, news_media, geospatial, or technical_infra.",
        }
    text = sanitize_mod.strip_agent(finding)
    url = sanitize_mod.strip_agent(source_url, limit=500)
    if not text or not url:
        return {"spec": OSINT_SPEC, "ok": False, "error": "fields_required", "plain": "Need a finding and a source_url."}
    if independence_verified not in (True, False):
        return {
            "spec": OSINT_SPEC,
            "ok": False,
            "error": "independence_required",
            "plain": "Syndicated copies are not independent corroboration. Say whether this source is independent.",
        }
    cid = (case_id or "").strip() or None
    camp = (campaign_cluster_id or "").strip() or None
    if bool(cid) == bool(camp):
        return {
            "spec": OSINT_SPEC,
            "ok": False,
            "error": "anchor_required",
            "plain": "OSINT corroborates a case or a 137 cluster. It does not stand in for either.",
        }
    store = _load()
    if cid:
        row = next((c for c in store["cases"] if c.get("case_id") == cid), None)
        if not row:
            return {"spec": OSINT_SPEC, "ok": False, "error": "case_not_found", "plain": "Unknown case_id."}
    else:
        try:
            from gate import campaign as campaign_mod
        except ImportError:
            import campaign as campaign_mod
        if not any(c.get("campaign_cluster_id") == camp for c in campaign_mod.list_clusters()):
            return {"spec": OSINT_SPEC, "ok": False, "error": "cluster_not_found", "plain": "Unknown campaign_cluster_id."}
        row = None
    rec = {
        "spec": OSINT_SPEC,
        "ok": True,
        "corroboration_id": "osint_" + uuid.uuid4().hex[:12],
        "case_id": cid,
        "campaign_cluster_id": camp,
        "source_category": cat,
        "finding": text,
        "source_url": url,
        "independence_verified": bool(independence_verified),
        "evidentiary_weight": EVIDENTIARY_WEIGHT,
        "hard_binding": HARD_BINDING,
        "logged_at": _iso(),
        "plain": "Corroborating only. Not hash-verified proof. Syndicated copies stay flagged if independence_verified is false.",
    }
    store.setdefault("osint", []).append(rec)
    if row is not None:
        row.setdefault("osint_corroboration_ids", []).append(rec["corroboration_id"])
    _save(store)
    return rec


def list_osint() -> list[dict[str, Any]]:
    return list(_load().get("osint") or [])


def set_status(*, case_id: str, status: str, resolution: str | None = None) -> dict[str, Any]:
    st = (status or "").strip().upper()
    if st not in STATUSES:
        return {"spec": CASE_SPEC, "ok": False, "error": "status_unknown", "plain": "OPEN, CLOSED, or ESCALATED."}
    store = _load()
    row = next((c for c in store["cases"] if c.get("case_id") == (case_id or "").strip()), None)
    if not row:
        return {"spec": CASE_SPEC, "ok": False, "error": "case_not_found", "plain": "Unknown case_id."}
    if st in ("CLOSED", "ESCALATED") and not _has_deception(row):
        return {
            "spec": CASE_SPEC,
            "ok": False,
            "error": "deception_hypothesis_required",
            "plain": "CLOSE/ESCALATE needs a logged is_deception_hypothesis, even if its weight is zero. Ask whether this was staged.",
        }
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
