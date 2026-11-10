"""Items 129 / 129b / 131 — Kudurru card, watch, glyph.

The flex object and the proof object are the same artifact: receipt_root_hash
is sha256 over ordered underlying_receipt_ids. Streak policy is unset — this
module does not pick hard-reset vs decay vs Chess.com 2-day grace.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

SPEC_CARD = "gate-kudurru-card-v1"
SPEC_WATCH = "gate-kudurru-watch-v1"
SPEC_GLYPH = "gate-kudurru-glyph-v1"
SPEC_BREAK = "gate-kudurru-streak-break-v1"

COHORTS = ("Insurance", "Fleet", "Clinical", "Grid", "Counsel")
MARKS = ("CLEAN", "WATCH", "BREAK")
LEGEND = {"CLEAN": "🟩", "WATCH": "🟨", "BREAK": "🟥"}
LEGEND_VERSION = "kudurru-glyph-v1"
MILESTONES = (30, 100, 365)
WATCH_STATUSES = ("NONE", "POSITIVE_WATCH", "NEGATIVE_WATCH")
WATCH_RESOLUTIONS = ("HELD", "BROKEN", "EXTENDED", "REMOVED")
STAKE_KEYS = ("stake", "wager", "payout", "notional", "contracts", "price")
OPEN_POLICIES = ("hard_reset", "severity_decay", "chess_2day_grace")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def normalize_cohort(raw: str | None) -> str | None:
    text = (raw or "").strip()
    if not text:
        return None
    aliases = {
        "insurance": "Insurance",
        "fleet": "Fleet",
        "network": "Fleet",
        "clinical": "Clinical",
        "biology": "Clinical",
        "grid": "Grid",
        "climate": "Grid",
        "counsel": "Counsel",
        "epistemics": "Counsel",
    }
    if text in COHORTS:
        return text
    return aliases.get(text.lower())


def root_hash(underlying_receipt_ids: list[str]) -> str:
    ordered = [str(x).strip() for x in underlying_receipt_ids if str(x).strip()]
    blob = receipt_mod._canonical_json(ordered)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _marks(days: Any) -> list[dict[str, Any]]:
    out = []
    for raw in days or []:
        if not isinstance(raw, dict):
            continue
        mark = str(raw.get("mark") or "CLEAN").strip().upper()
        if mark not in MARKS:
            continue
        out.append(
            {
                "date": str(raw.get("date") or "").strip() or None,
                "mark": mark,
                "cause_receipt_id": str(raw.get("cause_receipt_id") or "").strip() or None,
            }
        )
    return out


def _streak_from_marks(marks: list[dict[str, Any]]) -> tuple[int, str | None, dict[str, Any] | None]:
    """Count CLEAN marks; WATCH does not reset; BREAK ends. Calendar gaps are ignored."""
    streak = 0
    broken_at = None
    brk = None
    for row in marks:
        if row["mark"] == "BREAK":
            broken_at = row.get("date")
            brk = {
                "spec": SPEC_BREAK,
                "break_id": "brk_" + uuid.uuid4().hex[:12],
                "broken_at": broken_at,
                "cause_receipt_id": row.get("cause_receipt_id"),
                "previous_streak_days": streak,
            }
            streak = 0
            continue
        if row["mark"] == "CLEAN":
            streak += 1
    return streak, broken_at, brk


def card(
    *,
    operator_id: str,
    org_id: str,
    cohort_vertical: str,
    period_start: str,
    period_end: str,
    underlying_receipt_ids: list[str] | None = None,
    days: Any = None,
    composite_score: Any = None,
    peer_composites: list[float] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = extra if isinstance(extra, dict) else {}
    if body.get("streak_policy") not in (None, "", False):
        return {
            "spec": SPEC_CARD,
            "ok": False,
            "error": "streak_policy_open",
            "open_call": list(OPEN_POLICIES),
            "plain": "hard-reset vs severity-decay vs Chess.com 2-day grace is not decided. Do not pick it here.",
        }

    op = (operator_id or "").strip()
    org = (org_id or "").strip()
    cohort = normalize_cohort(cohort_vertical)
    ids = [str(x).strip() for x in (underlying_receipt_ids or body.get("underlying_receipt_ids") or []) if str(x).strip()]
    if not op or not org or not cohort:
        return {
            "spec": SPEC_CARD,
            "ok": False,
            "error": "fields_required",
            "plain": "operator_id, org_id, and a CDPI cohort vertical are required. The flex is personal, not org-scoped.",
        }
    if not ids:
        return {
            "spec": SPEC_CARD,
            "ok": False,
            "error": "receipts_required",
            "plain": "A Kudurru card without underlying_receipt_ids is a vanity checkmark.",
        }

    marks = _marks(days if days is not None else body.get("days"))
    streak_days, broken_at, brk = _streak_from_marks(marks)
    dates = []
    for m in marks:
        raw = m.get("date") or ""
        try:
            dates.append(datetime.fromisoformat(raw[:10]).date())
        except ValueError:
            continue
    dates.sort()
    gap_unscored = any((dates[i] - dates[i - 1]).days > 1 for i in range(1, len(dates)))

    score = None
    if composite_score not in (None, "", False):
        try:
            score = float(composite_score)
        except (TypeError, ValueError):
            return {"spec": SPEC_CARD, "ok": False, "error": "composite_not_numeric", "plain": "composite_score is 0–100 or omitted."}
        if score < 0 or score > 100:
            return {"spec": SPEC_CARD, "ok": False, "error": "composite_range", "plain": "composite_score is 0–100 or omitted."}

    percentile = None
    peers = [float(x) for x in (peer_composites or []) if x is not None]
    if score is not None and len(peers) >= 20:
        below = sum(1 for p in peers if p <= score)
        percentile = round(100.0 * below / len(peers), 1)

    hashed = root_hash(ids)
    if brk:
        brk["operator_id"] = op
    rec = {
        "spec": SPEC_CARD,
        "ok": True,
        "card_id": "kud_" + uuid.uuid4().hex[:12],
        "operator_id": op,
        "org_id": org,
        "cohort_vertical": cohort,
        "period_start": period_start,
        "period_end": period_end,
        "streak_days": streak_days,
        "streak_broken_at": broken_at,
        "streak_policy": None,
        "streak_break_event": brk,
        "percentile_rank": percentile,
        "composite_score": score,
        "receipt_root_hash": hashed,
        "underlying_receipt_ids": ids,
        "milestone_flag": streak_days in MILESTONES,
        "generated_at": _iso(),
        "gap_unscored": gap_unscored,
        "plain": (
            "Card hashes ordered receipt ids. Streak counts CLEAN marks only; "
            "calendar gaps do not apply a skip policy because that policy is unset."
        ),
    }
    return rec


def watch(
    *,
    card_id: str,
    status: str | None = None,
    follower_count: Any = 0,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    body = extra if isinstance(extra, dict) else {}
    hits = [k for k in STAKE_KEYS if body.get(k) not in (None, "", False)]
    if hits:
        return {
            "spec": SPEC_WATCH,
            "ok": False,
            "error": "stakes_refused",
            "refused": hits,
            "plain": "Watch is attention, not a market. No money on someone else's streak.",
        }
    cid = (card_id or "").strip()
    st = str(status or body.get("status") or "NONE").strip().upper()
    if not cid:
        return {"spec": SPEC_WATCH, "ok": False, "error": "card_id_required", "plain": "Watch points at a Kudurru card."}
    if st not in WATCH_STATUSES:
        return {"spec": SPEC_WATCH, "ok": False, "error": "status_unknown", "plain": "NONE, POSITIVE_WATCH, or NEGATIVE_WATCH."}
    reso = body.get("resolution")
    if reso not in (None, "", False) and str(reso).upper() not in WATCH_RESOLUTIONS:
        return {"spec": SPEC_WATCH, "ok": False, "error": "resolution_unknown", "plain": "HELD, BROKEN, EXTENDED, or REMOVED."}
    try:
        followers = int(follower_count if follower_count not in (None, "") else body.get("follower_count") or 0)
    except (TypeError, ValueError):
        followers = 0
    return {
        "spec": SPEC_WATCH,
        "ok": True,
        "watch_id": "watch_" + uuid.uuid4().hex[:12],
        "card_id": cid,
        "status": st,
        "trigger_reason": body.get("trigger_reason"),
        "opened_at": _iso(),
        "resolves_by": body.get("resolves_by"),
        "resolved_at": body.get("resolved_at"),
        "resolution": str(reso).upper() if reso not in (None, "", False) else None,
        "follower_count": max(followers, 0),
        "stakes": False,
        "plain": "S&P CreditWatch words. Follower count is attention, not money.",
    }


def glyph(
    *,
    card_id: str,
    days: Any,
    period_start: str | None = None,
    period_end: str | None = None,
) -> dict[str, Any]:
    cid = (card_id or "").strip()
    marks = _marks(days)
    if not cid:
        return {"spec": SPEC_GLYPH, "ok": False, "error": "card_id_required", "plain": "Glyph derives from a card."}
    if not marks:
        return {"spec": SPEC_GLYPH, "ok": False, "error": "days_required", "plain": "Glyph is one tile per marked day."}
    tiles = "".join(LEGEND[m["mark"]] for m in marks)
    return {
        "spec": SPEC_GLYPH,
        "ok": True,
        "glyph_id": "gly_" + uuid.uuid4().hex[:12],
        "card_id": cid,
        "period_start": period_start,
        "period_end": period_end,
        "glyph_string": tiles,
        "legend_version": LEGEND_VERSION,
        "legend": dict(LEGEND),
        "generated_at": _iso(),
        "plain": "Pattern only. No operator, no cause_receipt_id. The card is still the proof object.",
    }
