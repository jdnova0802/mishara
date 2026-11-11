"""Item 152 — reversible-only auto-response playbooks.

SOAR's missing pillar here is automation of *procedural* steps.
The action enum has no bind / liquidate / confirm value. Adding one
is a schema change, not a runtime flag.
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from gate import case_file as case_file_mod
except ImportError:
    import case_file as case_file_mod

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-auto-response-v1"
TRIGGERS = ("anomaly_flag", "link_graph_pattern", "campaign_cluster")
ACTIONS = ("enqueue_triage", "notify_analyst", "rate_limit_temporary", "tag_priority")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_AUTO_RESPONSE_PATH") or Path(__file__).resolve().parent / "data" / "auto_response.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "playbooks": [], "executions": [], "brakes": [], "tags": [], "notices": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "playbooks": [], "executions": [], "brakes": [], "tags": [], "notices": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "playbooks": [], "executions": [], "brakes": [], "tags": [], "notices": []}
    for key in ("playbooks", "executions", "brakes", "tags", "notices"):
        data.setdefault(key, [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def catalog() -> dict[str, Any]:
    store = _load()
    return {
        "spec": SPEC,
        "actions": list(ACTIONS),
        "triggers": list(TRIGGERS),
        "reversible_only": True,
        "irreversible_action_column": False,
        "playbooks": store["playbooks"],
        "executions": store["executions"],
        "plain": "Playbooks enqueue, notify, tag, or apply a self-expiring brake. They never disposition.",
    }


def register(
    *,
    name: str,
    trigger_source: str,
    action: str,
    created_by: str,
    trigger_condition: dict[str, Any] | None = None,
    max_duration_ms: int | None = None,
) -> dict[str, Any]:
    src = (trigger_source or "").strip()
    act = (action or "").strip()
    who = sanitize_mod.strip_agent(created_by, limit=200)
    label = sanitize_mod.strip_agent(name, limit=200)
    if src not in TRIGGERS:
        return {"spec": SPEC, "ok": False, "error": "trigger_unknown", "plain": "anomaly_flag, link_graph_pattern, or campaign_cluster."}
    if act not in ACTIONS:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "action_not_reversible",
            "plain": "enqueue_triage, notify_analyst, rate_limit_temporary, or tag_priority. No bind, liquidate, or confirm.",
        }
    if not label or not who:
        return {"spec": SPEC, "ok": False, "error": "fields_required", "plain": "Need a name and created_by."}
    duration = None
    if act == "rate_limit_temporary":
        try:
            duration = int(max_duration_ms or 0)
        except (TypeError, ValueError):
            duration = 0
        if duration <= 0:
            return {
                "spec": SPEC,
                "ok": False,
                "error": "max_duration_required",
                "plain": "A temporary brake always self-expires. Permanent rate limits are not in this table.",
            }
    cond = trigger_condition if isinstance(trigger_condition, dict) else {}
    rec = {
        "spec": SPEC,
        "ok": True,
        "playbook_id": "pb_" + uuid.uuid4().hex[:12],
        "name": label,
        "trigger_source": src,
        "trigger_condition": cond,
        "action": act,
        "reversible": True,
        "max_duration_ms": duration,
        "created_by": who,
        "created_at": _iso(),
        "plain": "Registered. Will not disposition a flag or close a case.",
    }
    store = _load()
    store["playbooks"].append(rec)
    _save(store)
    return rec


def _condition_hits(playbook: dict[str, Any], payload: dict[str, Any]) -> bool:
    cond = playbook.get("trigger_condition") if isinstance(playbook.get("trigger_condition"), dict) else {}
    if playbook.get("trigger_source") == "anomaly_flag":
        need = cond.get("deviation_sigma")
        if need is None:
            return True
        try:
            return float(payload.get("deviation_sigma") or 0) >= float(need)
        except (TypeError, ValueError):
            return False
    if playbook.get("trigger_source") == "link_graph_pattern":
        want = str(cond.get("edge_type") or "")
        if not want:
            return True
        return want == str(payload.get("edge_type") or "")
    return True


def _receipt_id(execution_id: str) -> str:
    return hashlib.sha256(f"auto-response:{execution_id}".encode()).hexdigest()[:32]


def fire(
    *,
    playbook_id: str,
    trigger_ref_id: str,
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    store = _load()
    pb = next((p for p in store["playbooks"] if p.get("playbook_id") == (playbook_id or "").strip()), None)
    if not pb:
        return {"spec": SPEC, "ok": False, "error": "playbook_not_found", "plain": "Unknown playbook_id."}
    ref = (trigger_ref_id or "").strip()
    if not ref:
        return {"spec": SPEC, "ok": False, "error": "trigger_ref_required", "plain": "Point at the flag, pattern, or cluster that fired."}
    body = payload if isinstance(payload, dict) else {}
    if not _condition_hits(pb, body):
        return {"spec": SPEC, "ok": False, "error": "condition_not_met", "plain": "Trigger condition missed. No action taken."}

    action = pb["action"]
    exec_id = "ex_" + uuid.uuid4().hex[:12]
    receipt = _receipt_id(exec_id)
    now = _now()
    note = ""
    if action == "enqueue_triage":
        ingested = case_file_mod.ingest_triage(source="anomaly_flag", source_id=ref)
        if not ingested.get("ok"):
            return {**ingested, "spec": SPEC}
        note = f"enqueued {ingested.get('triage_id')}"
    elif action == "notify_analyst":
        store["notices"].append({"execution_id": exec_id, "trigger_ref_id": ref, "at": _iso(now)})
        note = "analyst notified; mailbox is ops, not a disposition"
    elif action == "tag_priority":
        store["tags"].append({"execution_id": exec_id, "trigger_ref_id": ref, "tag": "priority", "at": _iso(now)})
        note = "tagged priority"
    else:
        ms = int(pb.get("max_duration_ms") or 0)
        expires = now + timedelta(milliseconds=ms)
        store["brakes"].append(
            {
                "execution_id": exec_id,
                "trigger_ref_id": ref,
                "applied_at": _iso(now),
                "expires_at": _iso(expires),
                "permanent": False,
            }
        )
        note = f"temporary brake expires {expires.replace(microsecond=0).isoformat()}"

    rec = {
        "spec": SPEC,
        "ok": True,
        "execution_id": exec_id,
        "playbook_id": pb["playbook_id"],
        "trigger_ref_id": ref,
        "action_taken": action,
        "executed_at": _iso(now),
        "receipt_id": receipt,
        "overridden_by": None,
        "note": note,
        "reversible": True,
        "plain": "Reversible step logged. Disposition stays human.",
    }
    store["executions"].append(rec)
    _save(store)
    return rec


def override(*, execution_id: str, overridden_by: str) -> dict[str, Any]:
    who = sanitize_mod.strip_agent(overridden_by, limit=200)
    if not who:
        return {"spec": SPEC, "ok": False, "error": "overridden_by_required", "plain": "Overrides are named, never silent."}
    store = _load()
    row = next((e for e in store["executions"] if e.get("execution_id") == (execution_id or "").strip()), None)
    if not row:
        return {"spec": SPEC, "ok": False, "error": "execution_not_found", "plain": "Unknown execution_id."}
    row["overridden_by"] = who
    row["overridden_at"] = _iso()
    row["plain"] = "Human reversed the reversible step. Logged."
    _save(store)
    return {**row, "ok": True, "spec": SPEC}


def active_brakes(*, now: datetime | None = None) -> list[dict[str, Any]]:
    clock = now or _now()
    out = []
    for brake in _load().get("brakes") or []:
        exp = str(brake.get("expires_at") or "")
        try:
            when = datetime.fromisoformat(exp.replace("Z", "+00:00"))
        except ValueError:
            continue
        if when > clock:
            out.append(brake)
    return out
