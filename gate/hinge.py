"""Item 165 — small-N hinge dissent (2–5 orgs).

Community Notes factorization needs a crowd. At a handful of mutually
distrusting orgs there is no polarity dimension to estimate. This module
refuses a helpfulness score. It names the shape of the split:

- dormant: fewer than two orgs
- hold: any org filed false_positive (asymmetric halt — cheap)
- unanimous: every org confirmed
- hinged: a historically dissenting org now confirms, and nobody filed false_positive
- split: otherwise, shown as-is, never collapsed

A rating without a falsifier is refused. That is the discourse-map test
relocated onto reviewers.
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

SPEC = "gate-hinge-v1"
RATINGS = ("confirmed", "false_positive", "needs_more_evidence")


def _iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_HINGE_PATH") or Path(__file__).resolve().parent / "data" / "hinge.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "ratings": [], "verdicts": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "ratings": [], "verdicts": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "ratings": [], "verdicts": []}
    data.setdefault("ratings", [])
    data.setdefault("verdicts", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def catalog() -> dict[str, Any]:
    store = _load()
    return {
        "spec": SPEC,
        "helpfulness_factor": False,
        "community_notes_threshold": None,
        "ratings": store["ratings"],
        "verdicts": store["verdicts"],
        "plain": "Small-N. No matrix factorization. Split is shown, not scored.",
    }


def rate(
    *,
    flag_id: str,
    reviewer_org_id: str,
    rating: str,
    falsifier: str,
) -> dict[str, Any]:
    fid = (flag_id or "").strip()
    org = sanitize_mod.strip_agent(reviewer_org_id, limit=200)
    rt = (rating or "").strip()
    change = sanitize_mod.strip_agent(falsifier, limit=400)
    if rt not in RATINGS:
        return {"spec": SPEC, "ok": False, "error": "rating_unknown"}
    if not fid or not org:
        return {"spec": SPEC, "ok": False, "error": "fields_required"}
    if not change:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "falsifier_required",
            "plain": "State what evidence would change this org's mind. Unfalsifiable ratings are the other genre.",
        }
    rec = {
        "spec": SPEC,
        "ok": True,
        "rating_id": "hg_" + uuid.uuid4().hex[:12],
        "flag_id": fid,
        "reviewer_org_id": org,
        "rating": rt,
        "falsifier": change,
        "rated_at": _iso(),
    }
    store = _load()
    store["ratings"].append(rec)
    _save(store)
    return rec


def _dissenters(store: dict[str, Any], org: str, except_flag: str) -> bool:
    prior = [
        r
        for r in store["ratings"]
        if r.get("reviewer_org_id") == org and r.get("flag_id") != except_flag
    ]
    return any(r.get("rating") in ("false_positive", "needs_more_evidence") for r in prior)


def adjudicate(*, flag_id: str) -> dict[str, Any]:
    fid = (flag_id or "").strip()
    store = _load()
    rows = [r for r in store["ratings"] if r.get("flag_id") == fid]
    orgs = sorted({r["reviewer_org_id"] for r in rows})
    by_org = {org: next(r for r in reversed(rows) if r["reviewer_org_id"] == org) for org in orgs}
    if len(orgs) < 2:
        rec = {
            "spec": SPEC,
            "ok": True,
            "verdict_id": None,
            "flag_id": fid,
            "verdict": "dormant",
            "helpfulness_factor": None,
            "orgs": orgs,
            "plain": "One org is a rater, not a consensus.",
        }
        return rec
    marks = {org: by_org[org]["rating"] for org in orgs}
    if any(m == "false_positive" for m in marks.values()):
        verdict = "hold"
        plain = "Any false_positive holds the finding. Halt is cheap. Collapse is not."
    elif all(m == "confirmed" for m in marks.values()):
        hinged = [org for org in orgs if _dissenters(store, org, fid)]
        if hinged:
            verdict = "hinged"
            plain = (
                "Unanimous on this flag, and "
                + ", ".join(hinged)
                + " previously dissented elsewhere. That is the small-N bridge."
            )
        else:
            verdict = "unanimous"
            plain = "Every org confirmed. Still not a crowd-factored helpfulness score."
    else:
        verdict = "split"
        plain = "Split shown. No 0.4 threshold at N=" + str(len(orgs)) + "."
    rec = {
        "spec": SPEC,
        "ok": True,
        "verdict_id": "hv_" + uuid.uuid4().hex[:12],
        "flag_id": fid,
        "verdict": verdict,
        "helpfulness_factor": None,
        "marks": marks,
        "falsifiers": {org: by_org[org]["falsifier"] for org in orgs},
        "orgs": orgs,
        "computed_at": _iso(),
        "plain": plain,
    }
    store["verdicts"].append(rec)
    _save(store)
    return rec
