"""Item 130 — Brier calibration ledger.

feeds_kudurru is false until sample_size clears an operator-set floor.
Unset floor means never feed — a perfect Brier on three rows is luck.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPEC = "gate-calibration-v1"
CORRECT = "CORRECT"
INCORRECT = "INCORRECT"
OUTCOMES = (CORRECT, INCORRECT)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(
        os.getenv("GATE_CALIBRATION_PATH") or Path(__file__).resolve().parent / "data" / "calibration.json"
    )


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "entries": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "entries": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "entries": []}
    data.setdefault("entries", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def min_sample() -> int | None:
    """Named floor, not a live baseline. Unset → Kudurru is not fed."""
    raw = (os.getenv("GATE_CALIBRATION_MIN_SAMPLE") or "").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        return None
    return value if value > 0 else None


def list_entries() -> list[dict[str, Any]]:
    return list(_load().get("entries") or [])


def _brier(p: float, outcome: str) -> float:
    y = 1.0 if outcome == CORRECT else 0.0
    return (p - y) ** 2


def resolve(
    *,
    operator_id: str,
    receipt_id: str,
    stated_confidence: Any,
    actual_outcome: str,
    persist: bool = True,
) -> dict[str, Any]:
    op = (operator_id or "").strip()
    rid = (receipt_id or "").strip()
    outcome = (actual_outcome or "").strip().upper()
    if not op or not rid:
        return {"spec": SPEC, "ok": False, "error": "fields_required", "plain": "operator_id and receipt_id required."}
    if outcome not in OUTCOMES:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "outcome_required",
            "plain": "actual_outcome is CORRECT or INCORRECT once Velaru/Mishara confirm.",
        }
    try:
        p = float(stated_confidence)
    except (TypeError, ValueError):
        return {"spec": SPEC, "ok": False, "error": "confidence_required", "plain": "stated_confidence is in [0, 1]."}
    if p < 0 or p > 1:
        return {"spec": SPEC, "ok": False, "error": "confidence_range", "plain": "stated_confidence is in [0, 1]."}

    rec = {
        "spec": SPEC,
        "ok": True,
        "entry_id": "cal_" + uuid.uuid4().hex[:12],
        "operator_id": op,
        "receipt_id": rid,
        "stated_confidence": p,
        "actual_outcome": outcome,
        "brier_component": _brier(p, outcome),
        "resolved_at": _iso(),
        "plain": "Brier component is (p − y)². Lower is better. 0 is perfect.",
    }
    if persist:
        store = _load()
        store["entries"].append(rec)
        _save(store)
    return rec


def score(operator_id: str) -> dict[str, Any]:
    op = (operator_id or "").strip()
    rows = [e for e in list_entries() if e.get("operator_id") == op]
    n = len(rows)
    mean = (sum(float(e["brier_component"]) for e in rows) / n) if n else None
    floor = min_sample()
    feeds = bool(n and floor is not None and n >= floor)
    return {
        "spec": SPEC,
        "score_id": "cals_" + (op or "none"),
        "operator_id": op or None,
        "period_start": min((e.get("resolved_at") or "") for e in rows) if rows else None,
        "period_end": max((e.get("resolved_at") or "") for e in rows) if rows else None,
        "mean_brier_score": mean,
        "sample_size": n,
        "min_sample": floor,
        "feeds_kudurru": feeds,
        "plain": (
            "sample_size gates Kudurru. A perfect Brier on thin data is luck."
            if not feeds
            else "Sample clears the named floor. This score may feed Kudurru."
        ),
    }
