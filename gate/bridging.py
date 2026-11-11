"""Item 158 — bridging-based cross-org reviewer consensus.

With one reviewing org there is no polarity to factor out — dormant
is a valid state. The 0.4 threshold is Community Notes' starting
point, not a sacred number. This is not the full matrix-factorization
solver; it subtracts org-mean so affiliation bias is visible.
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

SPEC = "gate-bridging-v1"
RATINGS = ("confirmed", "false_positive", "needs_more_evidence")
SCORE = {"confirmed": 1.0, "needs_more_evidence": 0.5, "false_positive": 0.0}
CONSENSUS_THRESHOLD = 0.4


def _iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_BRIDGING_PATH") or Path(__file__).resolve().parent / "data" / "bridging.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "ratings": [], "scores": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "ratings": [], "scores": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "ratings": [], "scores": []}
    data.setdefault("ratings", [])
    data.setdefault("scores", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def catalog() -> dict[str, Any]:
    store = _load()
    orgs = {r.get("reviewer_org_id") for r in store["ratings"] if r.get("reviewer_org_id")}
    dormant = len(orgs) < 2
    return {
        "spec": SPEC,
        "ratings": store["ratings"],
        "scores": store["scores"],
        "consensus_threshold": CONSENSUS_THRESHOLD,
        "dormant": dormant,
        "reviewer_orgs": sorted(orgs),
        "plain": (
            "One reviewing org (or none). No polarity to factor out. Empty consensus is honest."
            if dormant
            else "Helpfulness is residual after subtracting each org's mean rating."
        ),
    }


def rate(
    *,
    flag_id: str,
    reviewer_org_id: str,
    rating: str,
) -> dict[str, Any]:
    fid = (flag_id or "").strip()
    org = sanitize_mod.strip_agent(reviewer_org_id, limit=200)
    rt = (rating or "").strip()
    if rt not in RATINGS:
        return {"spec": SPEC, "ok": False, "error": "rating_unknown", "plain": "confirmed, false_positive, or needs_more_evidence."}
    if not fid or not org:
        return {"spec": SPEC, "ok": False, "error": "fields_required"}
    rec = {
        "spec": SPEC,
        "ok": True,
        "rating_id": "rt_" + uuid.uuid4().hex[:12],
        "flag_id": fid,
        "reviewer_org_id": org,
        "rating": rt,
        "rated_at": _iso(),
    }
    store = _load()
    store["ratings"].append(rec)
    _save(store)
    return rec


def score(*, flag_id: str) -> dict[str, Any]:
    fid = (flag_id or "").strip()
    store = _load()
    rows = [r for r in store["ratings"] if r.get("flag_id") == fid]
    orgs = sorted({r["reviewer_org_id"] for r in rows})
    if len(orgs) < 2:
        rec = {
            "spec": SPEC,
            "ok": True,
            "score_id": None,
            "flag_id": fid,
            "helpfulness_factor": None,
            "org_polarity_factors": {},
            "consensus_threshold": CONSENSUS_THRESHOLD,
            "computed_at": _iso(),
            "dormant": True,
            "plain": "Need two reviewing orgs before bridging. One rater is just that rater.",
        }
        return rec
    by_org: dict[str, list[float]] = {}
    for r in rows:
        by_org.setdefault(r["reviewer_org_id"], []).append(SCORE[r["rating"]])
    org_mean = {org: sum(vals) / len(vals) for org, vals in by_org.items()}
    global_mean = sum(org_mean.values()) / len(org_mean)
    polarity = {org: round(org_mean[org] - global_mean, 6) for org in orgs}
    residuals = []
    for r in rows:
        residuals.append(SCORE[r["rating"]] - org_mean[r["reviewer_org_id"]])
    helpfulness = round(global_mean + (sum(residuals) / len(residuals) if residuals else 0.0), 6)
    rec = {
        "spec": SPEC,
        "ok": True,
        "score_id": "sc_" + uuid.uuid4().hex[:12],
        "flag_id": fid,
        "helpfulness_factor": helpfulness,
        "org_polarity_factors": polarity,
        "consensus_threshold": CONSENSUS_THRESHOLD,
        "clears_threshold": helpfulness >= CONSENSUS_THRESHOLD,
        "computed_at": _iso(),
        "dormant": False,
        "solver": "org-mean residual, not Community Notes matrix factorization",
        "plain": "Affiliation mean pulled out. Not a claim the note is true.",
    }
    store["scores"].append(rec)
    _save(store)
    return rec
