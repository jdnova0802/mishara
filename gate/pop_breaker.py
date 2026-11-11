"""Item 162 — population-velocity circuit breaker.

Distinct from item 19's per-fuse spike halt. This watches rate of
change across the mouth: 133 flags, 161 challenge failures, 161
instruction denials. Level 3 has no auto-resume column.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from gate import sanitize as sanitize_mod
except ImportError:
    import sanitize as sanitize_mod

SPEC = "gate-pop-breaker-v1"
METRICS = (
    "anomaly_flags_per_minute",
    "challenge_failures_per_minute",
    "high_value_gate_denials_per_minute",
)
SCOPES = ("global", "cohort_vertical", "org_id")
WINDOW_S = 60


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _parse(ts: str | None) -> datetime | None:
    if not ts:
        return None
    s = ts.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _path() -> Path:
    return Path(os.getenv("GATE_POP_BREAKER_PATH") or Path(__file__).resolve().parent / "data" / "pop_breaker.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "thresholds": [], "events": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "thresholds": [], "events": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "thresholds": [], "events": []}
    data.setdefault("thresholds", [])
    data.setdefault("events", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def catalog() -> dict[str, Any]:
    store = _load()
    return {
        "spec": SPEC,
        "not_item_19": True,
        "auto_resume_column": False,
        "thresholds": store["thresholds"],
        "events": store["events"],
        "plain": "Rate-of-events pause. Does not diagnose the cause. Thresholds are named, not traffic-tuned.",
    }


def set_threshold(
    *,
    metric: str,
    scope: str,
    level_1_threshold: int,
    level_1_pause_ms: int,
    level_2_threshold: int,
    level_2_pause_ms: int,
    level_3_threshold: int,
    scope_id: str | None = None,
) -> dict[str, Any]:
    met = (metric or "").strip()
    sc = (scope or "").strip()
    if met not in METRICS:
        return {"spec": SPEC, "ok": False, "error": "metric_unknown"}
    if sc not in SCOPES:
        return {"spec": SPEC, "ok": False, "error": "scope_unknown"}
    try:
        l1, l2, l3 = int(level_1_threshold), int(level_2_threshold), int(level_3_threshold)
        p1, p2 = int(level_1_pause_ms), int(level_2_pause_ms)
    except (TypeError, ValueError):
        return {"spec": SPEC, "ok": False, "error": "thresholds_numeric"}
    if not (0 < l1 < l2 < l3):
        return {"spec": SPEC, "ok": False, "error": "levels_must_increase", "plain": "Level 1 < 2 < 3, all positive."}
    rec = {
        "spec": SPEC,
        "ok": True,
        "threshold_id": "cb_" + uuid.uuid4().hex[:12],
        "metric": met,
        "scope": sc,
        "scope_id": sanitize_mod.strip_agent(scope_id, limit=80) or None,
        "level_1_threshold": l1,
        "level_1_pause_ms": p1,
        "level_2_threshold": l2,
        "level_2_pause_ms": p2,
        "level_3_threshold": l3,
        "created_at": _iso(),
        "plain": "Named. Not an exchange-calibrated number.",
    }
    store = _load()
    store["thresholds"].append(rec)
    _save(store)
    return rec


def _level(th: dict[str, Any], observed: int) -> int | None:
    if observed >= int(th["level_3_threshold"]):
        return 3
    if observed >= int(th["level_2_threshold"]):
        return 2
    if observed >= int(th["level_1_threshold"]):
        return 1
    return None


def evaluate(
    ticks: list[dict[str, Any]],
    *,
    threshold_id: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    store = _load()
    th = next((t for t in store["thresholds"] if t.get("threshold_id") == (threshold_id or "").strip()), None)
    if not th:
        return {"spec": SPEC, "ok": False, "error": "threshold_not_found"}
    clock = now or _now()
    cutoff = clock - timedelta(seconds=WINDOW_S)
    observed = 0
    for tick in ticks:
        if str(tick.get("metric") or "") != th["metric"]:
            continue
        if th["scope"] != "global":
            if str(tick.get("scope_id") or "") != str(th.get("scope_id") or ""):
                continue
        when = _parse(str(tick.get("at") or ""))
        if when is None or when < cutoff:
            continue
        observed += 1
    level = _level(th, observed)
    if level is None:
        return {
            "spec": SPEC,
            "ok": True,
            "threshold_id": th["threshold_id"],
            "level": None,
            "observed_value": observed,
            "triggered": False,
            "plain": "Below level 1. No pause.",
        }
    pause_ms = None if level == 3 else int(th[f"level_{level}_pause_ms"])
    rec = {
        "spec": SPEC,
        "ok": True,
        "event_id": "cbe_" + uuid.uuid4().hex[:12],
        "threshold_id": th["threshold_id"],
        "level": level,
        "observed_value": observed,
        "triggered_at": _iso(clock),
        "paused_until": None if level == 3 else _iso(clock + timedelta(milliseconds=pause_ms or 0)),
        "resumed_at": None,
        "resumed_by": None,
        "plain": (
            "Level 3. Manual resume required. No auto-resume column."
            if level == 3
            else f"Level {level} pause. Buys time; does not name the cause."
        ),
    }
    store["events"].append(rec)
    _save(store)
    return rec


def resume(*, event_id: str, resumed_by: str) -> dict[str, Any]:
    who = sanitize_mod.strip_agent(resumed_by, limit=200)
    if not who:
        return {"spec": SPEC, "ok": False, "error": "resumed_by_required", "plain": "Level 3 never auto-resumes."}
    store = _load()
    row = next((e for e in store["events"] if e.get("event_id") == (event_id or "").strip()), None)
    if not row:
        return {"spec": SPEC, "ok": False, "error": "event_not_found"}
    if int(row.get("level") or 0) != 3:
        return {"spec": SPEC, "ok": False, "error": "manual_resume_is_level_3"}
    row["resumed_at"] = _iso()
    row["resumed_by"] = who
    row["plain"] = "Human resumed after level 3. Logged."
    _save(store)
    return {**row, "ok": True}
