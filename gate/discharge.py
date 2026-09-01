"""Discharge — time-bounded standing. The chain stays. The standing lapses.

A proof rail with no expiry rail is a prison. Contributing to a permanent
record with no discharge is strictly increasing liability. That is why
incident registries stay journalism: nobody self-reports into a subpoena.

This is not deletion. Not admin CHARGE. Not an actor self-wipe.
Standing is metadata about the record. The record remains stranger-openable.
A stranger can open both: the folio, and the receipt that its standing ended.

Vacancy test:
  Identifier — job_id
  Contribution rule — no schedule, no second folio (prison)
  Chokepoint — the next contribution cannot proceed without an expiry rail

Cash SKU: Discharge of Record $1,500. We lapse one folio. They attach both.
They do not implement Gate. Actor cannot self-discharge.
Not a sixth sibling. Not a /for/ plate. Not Being. Never sell may.
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from gate import inventor as inventor_mod
except ImportError:
    import inventor as inventor_mod

try:
    from gate import remaining as remaining_mod
except ImportError:
    import remaining as remaining_mod

try:
    from gate import time_source as time_source_mod
except ImportError:
    import time_source as time_source_mod

SPEC = "gate-discharge-v1"
FAMILY_SIBLINGS_REMAIN = 5
L2_MODULE = False
CLEVERER_LAYER = None
PAYEE = "Nisaba LLC"

DISCHARGE_LABEL = "$1,500"
DISCHARGE_CENTS = 150_000
DISCHARGE_USD = 1500

EMAIL_LINE = (
    "Your remaining has no expiry. The next contribution is a prison. "
    "We lapse the standing and issue the receipt. You open both. $1,500. "
    "The folio stays. The actor cannot wipe themselves."
)

SKUS: dict[str, dict[str, Any]] = {
    "discharge_of_record": {
        "id": "discharge_of_record",
        "name": "Discharge of Record",
        "label": DISCHARGE_LABEL,
        "cents": DISCHARGE_CENTS,
        "stripe_name": "Discharge of Record — lapse receipt for one folio",
        "stripe_desc": "We schedule the already-lapsed standing and issue the receipt. You open both. The folio stays.",
        "who": "GC / board with a prison folio — no expiry rail, next contribution blocked",
        "deliverable": (
            "Operated discharge pack: schedule already lapsed + stranger-openable "
            "receipt + folio. They never implement. Actor cannot self-wipe."
        ),
        "why_now": (
            "They already have a stale remaining or a Bind they cannot contribute to again. "
            "They will pay to lapse it, not to invent jubilee."
        ),
        "surpasses": (
            "Bind is the lock. Finished is the live write. This is the lawful end of standing. "
            "Cheaper than Refusal because the try already exists."
        ),
    },
}

IDENTITY = "standing lapses; the chain does not"
THESIS = (
    "Every durable recording institution eventually requires a forgetting "
    "institution or it becomes a prison. Law has statutes of limitation. "
    "Money has bankruptcy and jubilee. Digital remaining had none. "
    "A discharge receipt attests that standing ended on schedule. "
    "The folio is still there. A stranger opens both."
)

DEFAULT_STANDING_DAYS = 365

# job_id -> schedule / receipts. Demo mouth. Not a production ledger.
_SCHEDULES: dict[str, dict[str, Any]] = {}
_RECEIPTS: dict[str, dict[str, Any]] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def _parse(iso: str) -> datetime:
    raw = (iso or "").strip()
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    return datetime.fromisoformat(raw)


def _folio_head(job_id: str) -> str:
    folio = remaining_mod.folio(job_id)
    blob = (
        f"{folio.get('job_id')}|{folio.get('identity_holds')}|"
        f"{(folio.get('tree_head') or {}).get('root') or ''}|"
        f"{(folio.get('remaining') or {}).get('one_way_class') or ''}"
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def schedule(job_id: str, standing_until: str = "", days: int = DEFAULT_STANDING_DAYS) -> dict[str, Any]:
    """Put an expiry rail on a remaining. Without this, contribution is a prison."""
    jid = (job_id or "").strip()[:160]
    if not jid:
        return {
            "spec": SPEC,
            "kind": "discharge_schedule",
            "ok": False,
            "reason": "job_id_required",
            "until_gate1_usd": 0,
        }
    if standing_until:
        until = _parse(standing_until)
    else:
        until = _now() + timedelta(days=int(days or DEFAULT_STANDING_DAYS))
    if until.tzinfo is None:
        until = until.replace(tzinfo=timezone.utc)
    row = {
        "job_id": jid,
        "standing_until": _iso(until),
        "scheduled_at": _iso(_now()),
        "folio_head_at_schedule": _folio_head(jid),
        "actor_cannot_self_discharge": True,
    }
    _SCHEDULES[jid] = row
    return {
        "spec": SPEC,
        "kind": "discharge_schedule",
        "ok": True,
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "job_id": jid,
        "standing_until": row["standing_until"],
        "deletion": False,
        "chain_intact": True,
        "may_sold": False,
        "being_sold": False,
        "until_gate1_usd": 0,
        "evaluated_at": _iso(_now()),
    }


def standing(job_id: str, now: datetime | None = None) -> dict[str, Any]:
    jid = (job_id or "").strip()[:160]
    recs = [r for r in _RECEIPTS.values() if r.get("job_id") == jid]
    sched = _SCHEDULES.get(jid)
    when = now or _now()
    if recs:
        state = "DISCHARGED"
    elif not sched:
        state = "UNBOUNDED"
    else:
        until = _parse(sched["standing_until"])
        state = "LAPSED" if when >= until else "LIVE"
    return {
        "spec": SPEC,
        "kind": "standing_of_record",
        "job_id": jid or None,
        "state": state,
        "has_schedule": bool(sched),
        "standing_until": (sched or {}).get("standing_until"),
        "discharges": len(recs),
        "deletion": False,
        "chain_intact": True,
        "unbounded_is_a_prison": state == "UNBOUNDED",
    }


def may_contribute(job_id: str) -> dict[str, Any]:
    """Chokepoint: no expiry rail → the next folio cannot proceed."""
    st = standing(job_id)
    ok = st["state"] != "UNBOUNDED"
    return {
        "spec": SPEC,
        "kind": "contribution_gate",
        "job_id": (job_id or "").strip()[:160] or None,
        "ok": ok,
        "state": st["state"],
        "reason": None if ok else "no_expiry_rail_prison",
        "chokepoint": "the next contribution cannot proceed without an expiry rail",
        "vacancy_test": {
            "identifier": True,
            "contribution_rule": ok,
            "chokepoint": True,
        },
    }


def issue(job_id: str, reason: str = "standing_lapsed_on_schedule", now: datetime | None = None) -> dict[str, Any]:
    """Stranger-openable receipt that standing ended. Folio is not deleted."""
    jid = (job_id or "").strip()[:160]
    if not jid:
        return {
            "spec": SPEC,
            "kind": "discharge_receipt",
            "ok": False,
            "reason": "job_id_required",
            "until_gate1_usd": 0,
        }
    st = standing(jid, now=now)
    if st["state"] == "UNBOUNDED":
        return {
            "spec": SPEC,
            "kind": "discharge_receipt",
            "ok": False,
            "reason": "no_schedule_cannot_discharge",
            "identity": IDENTITY,
            "job_id": jid,
            "deletion": False,
            "until_gate1_usd": 0,
        }
    if st["state"] == "LIVE":
        return {
            "spec": SPEC,
            "kind": "discharge_receipt",
            "ok": False,
            "reason": "standing_still_live",
            "standing_until": st["standing_until"],
            "job_id": jid,
            "deletion": False,
            "actor_cannot_self_discharge": True,
            "until_gate1_usd": 0,
        }
    folio = remaining_mod.folio(jid)
    rid = f"dch_{uuid.uuid4().hex[:16]}"
    head = _folio_head(jid)
    receipt = {
        "spec": SPEC,
        "kind": "discharge_receipt",
        "ok": True,
        "id": rid,
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "job_id": jid,
        "reason": (reason or "standing_lapsed_on_schedule")[:160],
        "standing_until": st["standing_until"],
        "discharged_at": _iso(now or _now()),
        "folio_still_exists": True,
        "folio_identity_holds": folio.get("identity_holds"),
        "folio_head": head,
        "deletion": False,
        "chain_intact": True,
        "standing_is_metadata": True,
        "actor_cannot_self_discharge": True,
        "may_sold": False,
        "being_sold": False,
        "payee": PAYEE,
        "until_gate1_usd": 0,
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
    }
    _RECEIPTS[rid] = receipt
    return receipt


def stripe_line_item(sku: str = "discharge_of_record") -> dict[str, Any]:
    row = SKUS[sku]
    return {
        "price_data": {
            "currency": "usd",
            "unit_amount": int(row["cents"]),
            "product_data": {
                "name": row["stripe_name"],
                "description": row["stripe_desc"],
            },
        },
        "quantity": 1,
    }


def pack(job_id: str, public_url: str = "", contact_email: str = "") -> dict[str, Any]:
    """They pay. We lapse one folio. They attach both. They do not implement."""
    jid = (job_id or "").strip()[:160] or f"pc:DCH-PAY-{uuid.uuid4().hex[:12]}"
    st = standing(jid)
    if st["state"] != "DISCHARGED":
        past = _iso(_now() - timedelta(seconds=1))
        schedule(jid, standing_until=past)
        issued = issue(jid)
    else:
        recs = [r for r in _RECEIPTS.values() if r.get("job_id") == jid]
        issued = recs[-1] if recs else issue(jid)
    both = open_both(jid)
    return {
        "spec": SPEC,
        "kind": "discharge_of_record_pack",
        "inventor": inventor_mod.stamp(),
        "job_id": jid,
        "price": DISCHARGE_LABEL,
        "until_gate1_usd": DISCHARGE_USD,
        "operated_by": "Nisaba LLC",
        "payee": PAYEE,
        "they_do_not_implement_gate": True,
        "identity": IDENTITY,
        "receipt": issued,
        "open_both": both,
        "deletion": False,
        "chain_intact": True,
        "folio_still_exists": True,
        "actor_cannot_self_discharge": True,
        "time_source": time_source_mod.attest(),
        "may_sold": False,
        "being_sold": False,
        "cleverer_layer": CLEVERER_LAYER,
        "l2_module": L2_MODULE,
        "their_production": False,
        "not": [
            "deletion",
            "admin CHARGE",
            "actor self-wipe",
            "a memory hole",
            "Being",
            "immunity",
        ],
        "evaluated_at": _iso(_now()),
        "page": f"{(public_url or '').rstrip('/')}/discharge" if public_url else "/discharge",
        "contact": contact_email or None,
    }


def open_both(job_id: str) -> dict[str, Any]:
    """A stranger opens the folio and the discharge. That is the product."""
    jid = (job_id or "").strip()[:160]
    folio = remaining_mod.folio(jid)
    recs = [r for r in _RECEIPTS.values() if r.get("job_id") == jid]
    st = standing(jid)
    return {
        "spec": SPEC,
        "kind": "stranger_opens_both",
        "identity": IDENTITY,
        "standing": st,
        "folio": folio,
        "discharges": recs,
        "deletion": False,
        "chain_intact": True,
        "the_record_is_not_the_standing": True,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Discharge",
        "inventor": inventor_mod.stamp(),
        "identity": IDENTITY,
        "thesis": THESIS,
        "email_line": EMAIL_LINE,
        "skus": {k: {kk: vv for kk, vv in v.items() if kk != "stripe_desc"} for k, v in SKUS.items()},
        "vacancy_test": {
            "identifier": "job_id",
            "contribution_rule": "no expiry rail → contribution is a prison",
            "chokepoint": "the next folio cannot proceed without a schedule",
        },
        "not": [
            "deletion",
            "admin CHARGE",
            "actor self-wipe",
            "a memory hole",
            "Being",
            "immunity",
        ],
        "payee": PAYEE,
        "family_siblings_remain": FAMILY_SIBLINGS_REMAIN,
        "l2_module": L2_MODULE,
        "cleverer_layer": CLEVERER_LAYER,
        "not_museum": True,
        "until_gate1_usd": DISCHARGE_USD,
        "checkout": f"{base}/discharge/checkout",
        "cash_now": True,
        "prints_when": "they pay — we lapse — they open both",
        "cash_door": f"{base}/discharge",
        "page": f"{base}/discharge",
        "links": {
            "page": f"{base}/discharge",
            "null": f"{base}/null",
            "remaining": f"{base}/remaining",
            "finished": f"{base}/finished",
            "bind_room": f"{base}/bind-room",
            "commons": f"{base}/commons",
            "vital": f"{base}/vital",
        },
        "gatekeep": (
            "Cash SKU. Forgetting institution. Not a buyer plate. Not a sixth sibling. "
            "Standing lapses. The chain does not. $1,500 operated lapse."
        ),
    }
