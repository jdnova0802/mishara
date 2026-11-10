"""Item 138 — OPSEC disclosure review (NSDD-298 five-step).

Does not un-publish stranger-verifiable surfaces. Records what an adversary
learns and whether a countermeasure is proposed or applied. Item 118 banding
is applied in code (exact cutoffs 409); that review is derived, not a desk score.
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

SPEC = "gate-opsec-review-v1"
SURFACES = (
    "item_25_open_spec",
    "item_29_leaderboard",
    "item_58_live_map",
    "item_74_verify_api",
    "item_118_threshold_curve",
)
RANKS = ("LOW", "MEDIUM", "HIGH")
STATUSES = ("PROPOSED", "APPLIED")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_OPSEC_PATH") or Path(__file__).resolve().parent / "data" / "opsec.json")


def _load() -> dict[str, Any]:
    path = _path()
    if not path.exists():
        return {"spec": SPEC, "reviews": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"spec": SPEC, "reviews": []}
    if not isinstance(data, dict):
        return {"spec": SPEC, "reviews": []}
    data.setdefault("reviews", [])
    return data


def _save(store: dict[str, Any]) -> None:
    path = _path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, indent=2), encoding="utf-8")


def curve_banding_review() -> dict[str, Any]:
    """Item 118 already refuses exact cutoffs. That is an APPLIED countermeasure."""
    return {
        "spec": SPEC,
        "review_id": "opsec_118_banding",
        "surface": "item_118_threshold_curve",
        "critical_info_identified": "Exact precision/recall operating point per vertical.",
        "threat_actor": "Anyone crafting near-threshold ALLOW (ATLAS AML.T0043 / AML.T0015).",
        "vulnerability": "Publishing the cutoff is a map of the boundary.",
        "risk_rank": "HIGH",
        "countermeasure": "Banded empty curve; operating_point null; numeric POSTs 409. ZK consistency is item 51, unbuilt.",
        "countermeasure_status": "APPLIED",
        "reviewed_at": None,
        "derived_from_code": True,
        "plain": "Do not un-publish the curve. Prove consistency, not the exact number.",
    }


def list_reviews() -> list[dict[str, Any]]:
    rows = [curve_banding_review()]
    for row in _load().get("reviews") or []:
        if row.get("review_id") != "opsec_118_banding":
            rows.append(row)
    return rows


def record(
    *,
    surface: str,
    critical_info_identified: str,
    threat_actor: str,
    vulnerability: str,
    risk_rank: str,
    countermeasure: str,
    countermeasure_status: str = "PROPOSED",
) -> dict[str, Any]:
    surf = (surface or "").strip()
    if surf not in SURFACES:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "surface_unknown",
            "allowed": list(SURFACES),
            "plain": "Review a named stranger-verifiable surface, not a new one.",
        }
    rank = (risk_rank or "").strip().upper()
    if rank not in RANKS:
        return {"spec": SPEC, "ok": False, "error": "rank_unknown", "plain": "LOW, MEDIUM, or HIGH."}
    status = (countermeasure_status or "PROPOSED").strip().upper()
    if status not in STATUSES:
        return {"spec": SPEC, "ok": False, "error": "status_unknown", "plain": "PROPOSED or APPLIED."}
    info = sanitize_mod.strip_agent(critical_info_identified)
    threat = sanitize_mod.strip_agent(threat_actor, limit=400)
    vuln = sanitize_mod.strip_agent(vulnerability)
    measure = sanitize_mod.strip_agent(countermeasure)
    if not info or not threat or not vuln or not measure:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "five_steps_required",
            "plain": "NSDD-298: name the critical info, threat, vulnerability, rank, and countermeasure.",
        }
    rec = {
        "spec": SPEC,
        "ok": True,
        "review_id": "opsec_" + uuid.uuid4().hex[:12],
        "surface": surf,
        "critical_info_identified": info,
        "threat_actor": threat,
        "vulnerability": vuln,
        "risk_rank": rank,
        "countermeasure": measure,
        "countermeasure_status": status,
        "reviewed_at": _iso(),
        "derived_from_code": False,
        "plain": "Disclosure review logged. Stranger-verifiability stays; the number does not have to.",
    }
    store = _load()
    store["reviews"].append(rec)
    _save(store)
    return rec
