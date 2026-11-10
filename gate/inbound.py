"""Item 139 — inbound signal integrity.

Same 137 cluster machinery, pointed at harm reports, calibration
resolutions, and operator registrations instead of outbound acts.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from gate import campaign as campaign_mod
except ImportError:
    import campaign as campaign_mod

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-inbound-integrity-v1"
SIGNAL_TYPES = ("harm_report", "calibration_resolution", "operator_registration")
DISPOSITIONS = ("TRUSTED", "QUARANTINED", "REJECTED")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_INBOUND_PATH") or Path(__file__).resolve().parent / "data" / "inbound.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "checks": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "checks": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "checks": []}
    data.setdefault("checks", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def list_checks() -> list[dict[str, Any]]:
    return list(_load().get("checks") or [])


def check(
    *,
    signal_type: str,
    signal_id: str,
    submitted_by: str,
    correlation_cluster_id: str | None = None,
    disposition: str | None = None,
) -> dict[str, Any]:
    kind = (signal_type or "").strip()
    if kind not in SIGNAL_TYPES:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "signal_type_unknown",
            "plain": "harm_report, calibration_resolution, or operator_registration.",
        }
    sid = (signal_id or "").strip()
    who = sanitize_mod.strip_agent(submitted_by, limit=200)
    if not sid or not who:
        return {"spec": SPEC, "ok": False, "error": "fields_required", "plain": "Need a signal_id and submitted_by."}

    cid = (correlation_cluster_id or "").strip() or None
    cluster = None
    if cid:
        cluster = next(
            (c for c in campaign_mod.list_clusters() if c.get("campaign_cluster_id") == cid),
            None,
        )
        if cluster is None:
            return {
                "spec": SPEC,
                "ok": False,
                "error": "cluster_not_found",
                "plain": "correlation_cluster_id must be a real 137 campaign_cluster. This is not a new detector.",
            }

    coordinated = bool(cluster and cluster.get("status") in ("SUSPECTED", "CONFIRMED"))
    disp = (disposition or "").strip().upper() or None
    if disp and disp not in DISPOSITIONS:
        return {"spec": SPEC, "ok": False, "error": "disposition_unknown", "plain": "TRUSTED, QUARANTINED, or REJECTED."}
    if disp == "REJECTED" and not coordinated:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "coordination_required",
            "plain": "REJECTED for inbound poisoning needs a 137 cluster showing coordination. A lone report is not Sybil by itself.",
        }

    rec = {
        "spec": SPEC,
        "ok": True,
        "check_id": "inb_" + uuid.uuid4().hex[:12],
        "signal_type": kind,
        "signal_id": sid,
        "submitted_by": who,
        "correlation_cluster_id": cid,
        "suspicious_coordination_flag": coordinated,
        "flagged_at": _iso() if coordinated else None,
        "disposition": disp,
        "never_auto_acted": True,
        "plain": (
            "Inbound signal tied to a 137 cluster. Disposition is human, not auto."
            if coordinated
            else "No coordination cluster. TRUSTED/QUARANTINED are available; REJECTED is not."
        ),
    }
    store = _load()
    store["checks"].append(rec)
    _save(store)
    return rec
