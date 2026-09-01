"""Pardon Sunset — Hard Mercy with expiry metallurgy.

Invention: LIVE against score is real only if scarred, co-signed, and sunsetting.
Forever pardon = aristocracy. Silent exception = forged.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

SPEC = "gate-pardon-sunset-v1"
INVENTION = "Pardon Sunset"
FAMILY = "foothill"

VERDICT_MERCY = "MERCY"
VERDICT_EXPIRED = "MERCY_EXPIRED"
VERDICT_FORGED = "FORGED_MERCY"
VERDICT_NOT_MERCY = "NOT_MERCY"

REASON_SELF_MERCY = "self_mercy_forbidden"
REASON_NO_COSIGN = "mercy_requires_second_sheath"
REASON_NO_SUNSET = "mercy_requires_sunset"
REASON_PAID = "paid_mercy_indulgence"
REASON_EXPIRED = "mercy_sunset_elapsed"
REASON_NO_SCAR = "mercy_requires_scar"


def _parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    t = str(ts).strip()
    if t.endswith("Z"):
        t = t[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(t)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def evaluate(
    *,
    against_score: bool | None = None,
    grantor_id: str | None = None,
    subject_id: str | None = None,
    cosigner_id: str | None = None,
    sunset_at: str | None = None,
    ttl_seconds: int | None = None,
    now: str | None = None,
    scar: bool | None = None,
    paid: bool | None = None,
    relationship_path: bool | None = None,
) -> dict[str, Any]:
    """Evaluate a mercy LIVE attempt."""
    if not against_score:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "verdict": VERDICT_NOT_MERCY,
            "may_proceed": True,
            "detail": "Not against-score — ordinary LIVE path; Pardon Sunset stands aside.",
            "rule": "Mercy is LIVE against score — scarred, co-signed, sunsetting. Forever pardon is aristocracy.",
        }

    reasons: list[str] = []
    if paid or relationship_path:
        reasons.append(REASON_PAID)
    if grantor_id and subject_id and grantor_id.strip() == subject_id.strip():
        reasons.append(REASON_SELF_MERCY)
    if not (cosigner_id or "").strip():
        reasons.append(REASON_NO_COSIGN)
    if scar is False:
        reasons.append(REASON_NO_SCAR)

    sunset = _parse_iso(sunset_at)
    if ttl_seconds is not None and sunset is None:
        base = _parse_iso(now) or datetime.now(timezone.utc)
        sunset = base + timedelta(seconds=max(60, int(ttl_seconds)))
    if sunset is None:
        reasons.append(REASON_NO_SUNSET)

    if reasons:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_FORGED,
            "may_proceed": False,
            "state": "MERCY",
            "reasons": reasons,
            "scar": True,
            "detail": "Hard Mercy forged — missing scar/co-sign/sunset or paid/self path.",
            "rule": "Mercy is LIVE against score — scarred, co-signed, sunsetting. Forever pardon is aristocracy.",
        }

    now_dt = _parse_iso(now) or datetime.now(timezone.utc)
    assert sunset is not None
    if now_dt >= sunset:
        return {
            "spec": SPEC,
            "invention": INVENTION,
            "family": FAMILY,
            "verdict": VERDICT_EXPIRED,
            "may_proceed": False,
            "state": "MERCY",
            "reasons": [REASON_EXPIRED],
            "sunset_at": sunset.isoformat(),
            "scar": True,
            "detail": "Mercy sunset elapsed — exception is dead. Re-mercy or CHOKE.",
            "rule": "Mercy is LIVE against score — scarred, co-signed, sunsetting. Forever pardon is aristocracy.",
        }

    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "verdict": VERDICT_MERCY,
        "may_proceed": True,
        "state": "MERCY",
        "grantor_id": grantor_id,
        "cosigner_id": cosigner_id,
        "subject_id": subject_id,
        "sunset_at": sunset.isoformat(),
        "scar": True if scar is not False else False,
        "against_score": True,
        "detail": "Hard Mercy cleared under Temporal Sheath — scarred, co-signed, sunsetting.",
        "rule": "Mercy is LIVE against score — scarred, co-signed, sunsetting. Forever pardon is aristocracy.",
        "pairs_with": "Indulgence Trap · Watchman Fuse · Moral Throat",
    }


def attach(plan: dict) -> dict:
    result = evaluate(
        against_score=plan.get("against_score") or plan.get("mercy"),
        grantor_id=plan.get("mercy_grantor_id") or plan.get("grantor_id"),
        subject_id=plan.get("job_id") or plan.get("subject_id"),
        cosigner_id=plan.get("mercy_cosigner_id") or plan.get("cosigner_id"),
        sunset_at=plan.get("mercy_sunset_at"),
        ttl_seconds=plan.get("mercy_ttl_seconds"),
        scar=plan.get("mercy_scar"),
        paid=plan.get("paid_mercy"),
        relationship_path=plan.get("relationship_live"),
    )
    plan["pardon_sunset"] = result
    if result.get("verdict") in (VERDICT_FORGED, VERDICT_EXPIRED):
        plan["allow_bind"] = False
        if "bind_allowed" in plan:
            plan["bind_allowed"] = False
        plan["halt"] = True
        plan["decision"] = "HALT"
        plan["reason"] = plan.get("reason") or (result.get("reasons") or ["forged_mercy"])[0]
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Hard Mercy — scarred, co-signed, sunsetting. Forever pardon is aristocracy.",
        "demo": f"POST {base}/demo/pas/pardon-sunset",
        "well_known": f"{base}/.well-known/pardon-sunset.json",
        "bind_room": f"{base}/bind-room",
        "temporal_sheath": "gate/TEMPORAL_SHEATH.md",
        "north_star": "gate/NORTH_STAR.md#moral-throat",
        "posture": "Under coordinators. Exception is real only on-ledger.",
    }
