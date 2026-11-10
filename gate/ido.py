"""Item 140 — Priority Intelligence Requirements and the feedback loop.

Direction and feedback around 132–135/137. An empty requirement list is an
unused table, not a live watch. SATISFIED needs a closed case. Feedback does
not silently retune item 133.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import case_file as case_file_mod
except ImportError:
    import case_file as case_file_mod

try:
    from gate import campaign as campaign_mod
except ImportError:
    import campaign as campaign_mod

try:
    from gate import link_graph as link_graph_mod
except ImportError:
    import link_graph as link_graph_mod

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-ido-v1"
REQ_STATUSES = ("ACTIVE", "SATISFIED", "STALE")
SOURCES = ("case_file", "campaign_cluster")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_IDO_PATH") or Path(__file__).resolve().parent / "data" / "ido.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "requirements": [], "feedback": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "requirements": [], "feedback": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "requirements": [], "feedback": []}
    data.setdefault("requirements", [])
    data.setdefault("feedback", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def list_requirements() -> list[dict[str, Any]]:
    return list(_load().get("requirements") or [])


def list_feedback() -> list[dict[str, Any]]:
    return list(_load().get("feedback") or [])


def catalog() -> dict[str, Any]:
    reqs = list_requirements()
    return {
        "spec": SPEC,
        "requirements": reqs,
        "feedback": list_feedback(),
        "empty_is_unused_table": len(reqs) == 0,
        "plain": (
            "No Priority Intelligence Requirements yet. An empty list is an unused table, not a live watch."
            if not reqs
            else "Direction is stated. Feedback closes into a new requirement or stays on the record."
        ),
    }


def state_requirement(
    *,
    stated_by: str,
    question: str,
    cohort_vertical: str | None = None,
    edge_types: Any = None,
    atlas_technique_ids: Any = None,
    disarm_technique_ids: Any = None,
) -> dict[str, Any]:
    who = sanitize_mod.strip_agent(stated_by, limit=200)
    q = sanitize_mod.strip_agent(question)
    if not who or not q:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "pir_required",
            "plain": "A PIR needs who is asking and the question in plain language.",
        }
    edges = [str(x).strip() for x in (edge_types or []) if str(x).strip()]
    bad = [e for e in edges if e not in link_graph_mod.EDGE_TYPES]
    if bad:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "edge_unknown",
            "allowed": list(link_graph_mod.EDGE_TYPES),
            "plain": "tasked_watch.edge_types must be 132 edges.",
        }
    rec = {
        "spec": SPEC,
        "ok": True,
        "requirement_id": "pir_" + uuid.uuid4().hex[:12],
        "stated_by": who,
        "question": q,
        "tasked_watch": {
            "cohort_vertical": sanitize_mod.strip_agent(cohort_vertical or "", limit=80) or None,
            "edge_types": edges,
            "atlas_technique_ids": [str(x).strip() for x in (atlas_technique_ids or []) if str(x).strip()],
            "disarm_technique_ids": [str(x).strip() for x in (disarm_technique_ids or []) if str(x).strip()],
        },
        "status": "ACTIVE",
        "opened_at": _iso(),
        "satisfied_by_case_id": None,
        "plain": "ACTIVE watch. SATISFIED only when a closed case answers it.",
    }
    store = _load()
    store["requirements"].append(rec)
    _save(store)
    return rec


def satisfy(*, requirement_id: str, case_id: str) -> dict[str, Any]:
    store = _load()
    row = next((r for r in store["requirements"] if r.get("requirement_id") == (requirement_id or "").strip()), None)
    if not row:
        return {"spec": SPEC, "ok": False, "error": "requirement_not_found", "plain": "Unknown requirement_id."}
    case = case_file_mod.get_case(case_id)
    if not case or case.get("status") != "CLOSED" or not case.get("resolution"):
        return {
            "spec": SPEC,
            "ok": False,
            "error": "closed_case_required",
            "plain": "SATISFIED needs a closed 134 case with a resolution. An open workspace is not an answer.",
        }
    row["status"] = "SATISFIED"
    row["satisfied_by_case_id"] = case["case_id"]
    row["plain"] = "PIR answered by case " + case["case_id"]
    _save(store)
    return {**row, "ok": True}


def feedback(
    *,
    source: str,
    source_id: str,
    new_requirement_id: str | None = None,
    updated_baseline_id: str | None = None,
) -> dict[str, Any]:
    src = (source or "").strip()
    if src not in SOURCES:
        return {"spec": SPEC, "ok": False, "error": "source_unknown", "plain": "Feedback is from case_file or campaign_cluster."}
    sid = (source_id or "").strip()
    conclusion = None
    if src == "case_file":
        case = case_file_mod.get_case(sid)
        if not case or not case.get("resolution"):
            return {
                "spec": SPEC,
                "ok": False,
                "error": "resolution_required",
                "plain": "case_file feedback pulls resolution. An open case is a dead end until it closes.",
            }
        conclusion = case["resolution"]
    else:
        cluster = next(
            (c for c in campaign_mod.list_clusters() if c.get("campaign_cluster_id") == sid),
            None,
        )
        if not cluster:
            return {"spec": SPEC, "ok": False, "error": "cluster_not_found", "plain": "Unknown campaign_cluster_id."}
        conclusion = str(cluster.get("status") or "")
    nid = (new_requirement_id or "").strip() or None
    if nid and not any(r.get("requirement_id") == nid for r in list_requirements()):
        return {"spec": SPEC, "ok": False, "error": "new_requirement_not_found", "plain": "new_requirement_id must already exist."}
    rec = {
        "spec": SPEC,
        "ok": True,
        "entry_id": "fb_" + uuid.uuid4().hex[:12],
        "source": src,
        "source_id": sid,
        "conclusion": conclusion,
        "new_requirement_id": nid,
        "updated_baseline_id": None,
        "baseline_retuned": False,
        "logged_at": _iso(),
        "plain": (
            "Feedback logged. Item 133 baseline is not silently retuned."
            if not updated_baseline_id
            else "Feedback logged. Passing a baseline id does not retune 133 from this mouth."
        ),
    }
    store = _load()
    store["feedback"].append(rec)
    _save(store)
    return rec
