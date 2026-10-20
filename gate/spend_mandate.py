"""Bound spend mandate — a prior write the auth mouth evaluates.

Card metadata is the same key that can spend. A cap edited in the second of
the swipe is not a rule a stranger can date. This object is the rule: agent,
amount, counterparty, categories, and an expiry, stored and signed before
the authorization. The issuing mouth loads it by id and refuses if the card
metadata disagrees or the record is missing, expired, or revoked.

Strangers can read the bound terms. The value is that they can check them.
"""
from __future__ import annotations

import hashlib
import json
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

SPEC = "gate-spend-mandate-v1"
ID_PREFIX = "gmd_"
DEFAULT_TTL_SECONDS = 30 * 24 * 3600
MAX_TTL_SECONDS = 366 * 24 * 3600

try:
    from gate import claim_scope as claim_scope_mod
except ImportError:
    import claim_scope as claim_scope_mod

try:
    from gate import db as db_mod
except ImportError:
    import db as db_mod


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _iso(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _parse_time(raw: str | None) -> datetime | None:
    s = (raw or "").strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).replace(microsecond=0)


def _parse_amount(raw: Any) -> float | None:
    if raw is None:
        return None
    s = str(raw).strip().replace(",", "").replace("$", "")
    if not s:
        return None
    try:
        return round(float(s), 2)
    except (TypeError, ValueError):
        return None


def _categories(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        items = raw
    elif isinstance(raw, str):
        s = raw.strip()
        if not s:
            return []
        if s.startswith("["):
            try:
                parsed = json.loads(s)
                items = parsed if isinstance(parsed, list) else [s]
            except json.JSONDecodeError:
                items = s.split(",")
        else:
            items = s.split(",")
    else:
        return []
    out: list[str] = []
    for item in items:
        text = str(item).strip().lower()
        if text and text not in out:
            out.append(text)
    return out


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _terms_from_body(body: dict) -> tuple[dict[str, Any] | None, str | None]:
    body = body if isinstance(body, dict) else {}
    agent_id = (str(body.get("agent_id") or "")).strip()
    if not agent_id or len(agent_id) > 128:
        return None, "agent_id_required"
    max_amount = _parse_amount(body.get("max_amount"))
    daily_cap = _parse_amount(body.get("daily_cap"))
    if max_amount is None and daily_cap is None:
        return None, "max_amount_or_daily_cap_required"
    if max_amount is not None and max_amount <= 0:
        return None, "max_amount_invalid"
    if daily_cap is not None and daily_cap <= 0:
        return None, "daily_cap_invalid"
    currency = (str(body.get("currency") or "USD")).strip().upper() or "USD"
    if currency != "USD":
        return None, "unsupported_currency"
    expected = (str(body.get("expected_counterparty") or body.get("expected_merchant") or "")).strip()
    if len(expected) > 256:
        return None, "expected_counterparty_too_long"
    job_id = (str(body.get("job_id") or "")).strip()
    if len(job_id) > 128:
        return None, "job_id_too_long"
    categories = _categories(body.get("allowed_categories"))
    now = _utc_now()
    not_after = _parse_time(body.get("not_after") if isinstance(body.get("not_after"), str) else None)
    if body.get("not_after") and not_after is None:
        return None, "not_after_invalid"
    if not_after is None:
        ttl = body.get("ttl_seconds")
        try:
            ttl_s = int(ttl) if ttl is not None else DEFAULT_TTL_SECONDS
        except (TypeError, ValueError):
            return None, "ttl_invalid"
        if ttl_s <= 0 or ttl_s > MAX_TTL_SECONDS:
            return None, "ttl_invalid"
        not_after = now + timedelta(seconds=ttl_s)
    if not_after <= now:
        return None, "not_after_in_past"
    if not_after > now + timedelta(seconds=MAX_TTL_SECONDS):
        return None, "not_after_too_far"
    terms = {
        "agent_id": agent_id,
        "max_amount": f"{max_amount:.2f}" if max_amount is not None else None,
        "daily_cap": f"{daily_cap:.2f}" if daily_cap is not None else None,
        "currency": currency,
        "expected_counterparty": expected or None,
        "allowed_categories": categories,
        "job_id": job_id or None,
        "not_after": _iso(not_after),
    }
    return terms, None


def fingerprint(terms: dict) -> str:
    return hashlib.sha256(_canonical(terms).encode("utf-8")).hexdigest()


def _sign(record: dict) -> dict:
    scope = claim_scope_mod.build(
        boundary="gate_spend_mandate",
        logs=["spend_mandates.terms_json", "spend_mandates.fingerprint"],
        plain=(
            "BOUND covers only this mandate id's stored terms — agent, caps, "
            "counterparty, categories, job, expiry. Not the card network, not "
            "capture, not a claim that the swipe already happened."
        ),
        time_window={
            "kind": "mandate_lifetime",
            "from": record.get("created_at"),
            "to": (record.get("terms") or {}).get("not_after"),
        },
        counterparties=[
            c
            for c in [(record.get("terms") or {}).get("expected_counterparty")]
            if c
        ]
        or None,
        keys_checked={
            "mandate_id": record.get("mandate_id"),
            "fingerprint": record.get("fingerprint"),
            "status": record.get("status"),
            "card_id": record.get("card_id"),
            "terms": record.get("terms"),
        },
        as_of=record.get("created_at"),
    )
    return claim_scope_mod.attach(
        {
            "spec": SPEC,
            "decision": "BOUND",
            "evaluation_id": record.get("mandate_id"),
            "rail": "issuing",
        },
        scope=scope,
        force=True,
    )


def _row_to_public(row: dict, *, public_url: str = "") -> dict[str, Any]:
    terms = row.get("terms") if isinstance(row.get("terms"), dict) else {}
    base = (public_url or "").rstrip("/")
    mandate_id = row["mandate_id"]
    record = {
        "spec": SPEC,
        "mandate_id": mandate_id,
        "fingerprint": row["fingerprint"],
        "status": row["status"],
        "demo": bool(row.get("demo")),
        "created_at": row["created_at"],
        "card_id": row.get("card_id") or None,
        "terms": terms,
        "verify_url": f"{base}/v1/mandate/{mandate_id}" if base else f"/v1/mandate/{mandate_id}",
    }
    signed = _sign(record)
    record["claim_scope"] = signed.get("claim_scope")
    record["signed_claim"] = signed.get("signed_claim")
    return record


def _card_id(raw: Any) -> tuple[str | None, str | None]:
    if raw is None or raw == "":
        return None, None
    text = str(raw).strip()
    if not text.replace("_", "").isalnum() or len(text) > 64:
        return None, "card_id_invalid"
    return text, None


def bind(body: dict, *, demo: bool = False, public_url: str = "") -> dict[str, Any]:
    body = body if isinstance(body, dict) else {}
    terms, err = _terms_from_body(body)
    if err or terms is None:
        return {"ok": False, "error": err or "invalid_mandate", "spec": SPEC}
    card_id, card_err = _card_id(body.get("card_id"))
    if card_err:
        return {"ok": False, "error": card_err, "spec": SPEC}
    mandate_id = ID_PREFIX + secrets.token_hex(8)
    created_at = _iso(_utc_now())
    fp = fingerprint(terms)
    db_mod.insert_spend_mandate(
        mandate_id=mandate_id,
        fingerprint=fp,
        agent_id=terms["agent_id"],
        terms=terms,
        created_at=created_at,
        not_after=terms["not_after"],
        status="bound",
        demo=demo,
        card_id=card_id,
    )
    public = _row_to_public(
        {
            "mandate_id": mandate_id,
            "fingerprint": fp,
            "status": "bound",
            "demo": demo,
            "created_at": created_at,
            "card_id": card_id,
            "terms": terms,
        },
        public_url=public_url,
    )
    public["ok"] = True
    public["card_metadata_key"] = "gate_mandate_id"
    public["plain"] = (
        "Put gate_mandate_id on the Issuing card. Disagreement with these terms "
        "is mandate_diverged. Omitting the id is mandate_omitted once this agent_id "
        "is presented, or once this Stripe card id is stored here. Pass card_id at "
        "bind so the first swipe cannot drop both the id and the agent_id."
    )
    public["enforcement"] = enforcement()
    return public


def fetch(mandate_id: str, *, public_url: str = "") -> dict[str, Any] | None:
    row = db_mod.get_spend_mandate(mandate_id)
    if not row:
        return None
    return _row_to_public(row, public_url=public_url)


def revoke(mandate_id: str, *, public_url: str = "") -> dict[str, Any] | None:
    row = db_mod.revoke_spend_mandate(mandate_id, revoked_at=_iso(_utc_now()))
    if not row:
        return None
    return _row_to_public(row, public_url=public_url)


def _presented(auth: dict, body: dict) -> dict[str, Any]:
    meta = {}
    try:
        from gate import issuing_mouth as mouth
    except ImportError:
        import issuing_mouth as mouth

    meta = mouth.card_meta(auth)
    mandate = body.get("mandate") if isinstance(body.get("mandate"), dict) else {}
    return {
        "mandate_id": (
            (meta.get("gate_mandate_id") or meta.get("mandate_id") or "")
            .strip()
        ),
        "agent_id": (mandate.get("agent_id") or "").strip() or None,
        "max_amount": _parse_amount(mandate.get("max_amount")),
        "daily_cap": _parse_amount(mandate.get("daily_cap")),
        "expected_counterparty": (mandate.get("expected_counterparty") or "").strip() or None,
        "allowed_categories": _categories(mandate.get("allowed_categories")),
        "job_id": (mandate.get("job_id") or "").strip() or None,
        "max_amount_set": bool((meta.get("max_amount") or meta.get("mandate_max") or "").strip()),
        "daily_cap_set": bool((meta.get("daily_cap") or "").strip()),
        "expected_set": bool((meta.get("expected_merchant") or meta.get("allowed_merchant") or "").strip()),
        "categories_set": bool(mouth.workflow_allowed_categories(auth)),
        "job_set": bool((meta.get("job_id") or meta.get("gate_job_id") or "").strip()),
        "agent_set": bool((meta.get("agent_id") or meta.get("gate_agent_id") or "").strip()),
        "card_id": _auth_card_id(auth),
    }


def _auth_card_id(auth: dict) -> str | None:
    auth = auth if isinstance(auth, dict) else {}
    card = auth.get("card") if isinstance(auth.get("card"), dict) else {}
    text = (str(card.get("id") or "")).strip()
    return text or None


def _is_live(row: dict) -> bool:
    if row.get("status") != "bound":
        return False
    not_after = _parse_time((row.get("terms") or {}).get("not_after"))
    return not_after is not None and not_after > _utc_now()


def _live_for(*, agent_id: str | None, card_id: str | None) -> list[dict]:
    if not agent_id and not card_id:
        return []
    try:
        rows = db_mod.list_spend_mandates(agent_id=agent_id, card_id=card_id)
    except Exception:
        raise
    seen: set[str] = set()
    live: list[dict] = []
    for row in rows:
        if not row or row["mandate_id"] in seen or not _is_live(row):
            continue
        seen.add(row["mandate_id"])
        live.append(row)
    return live


def _divergences(presented: dict, terms: dict) -> list[str]:
    bad: list[str] = []
    if presented["agent_set"] and presented["agent_id"] != terms.get("agent_id"):
        bad.append("agent_id")
    if presented["max_amount_set"]:
        bound = _parse_amount(terms.get("max_amount"))
        if presented["max_amount"] != bound:
            bad.append("max_amount")
    if presented["daily_cap_set"]:
        bound = _parse_amount(terms.get("daily_cap"))
        if presented["daily_cap"] != bound:
            bad.append("daily_cap")
    if presented["expected_set"]:
        if (presented["expected_counterparty"] or "").lower() != (terms.get("expected_counterparty") or "").lower():
            bad.append("expected_counterparty")
    if presented["categories_set"]:
        left = sorted(presented["allowed_categories"])
        right = sorted(list(terms.get("allowed_categories") or []))
        if left != right:
            bad.append("allowed_categories")
    if presented["job_set"] and presented["job_id"] != terms.get("job_id"):
        bad.append("job_id")
    return bad


def _omitted(presented: dict) -> dict[str, Any] | None:
    """A missing id fail-closes when this agent or this card already has a live mandate.

    Returns None when nothing live is anchored, which leaves the metadata path.
    """
    agent_id = presented["agent_id"] if presented["agent_set"] else None
    card_id = presented.get("card_id")
    try:
        live = _live_for(agent_id=agent_id, card_id=card_id)
    except Exception:
        return {
            "applied": False,
            "halt": True,
            "signal": "mandate_lookup_failed",
            "plain": "Could not read live mandates — fail closed.",
        }
    if not live:
        return None
    only = live[0]["mandate_id"] if len(live) == 1 else None
    return {
        "applied": False,
        "halt": True,
        "signal": "mandate_omitted",
        "mandate_id": only,
        "live_count": len(live),
        "plain": (
            "A live bound mandate exists for this agent or this card, and this "
            "swipe did not present gate_mandate_id."
        ),
    }


def resolve(auth: dict, body: dict) -> dict[str, Any]:
    """Bound record wins over metadata when the swipe names a mandate id.

    A missing id fail-closes with mandate_omitted when the presented agent_id
    has a live mandate, or when this Stripe card id is already stored on one.
    A swipe that names neither, on a card that was never stored, stays on the
    metadata path.
    """
    presented = _presented(auth, body)
    mandate_id = presented["mandate_id"]
    if not mandate_id:
        omitted = _omitted(presented)
        if omitted:
            return omitted
        return {"applied": False, "halt": False, "body": body, "signal": None}
    if not mandate_id.startswith(ID_PREFIX):
        return {
            "applied": False,
            "halt": True,
            "body": body,
            "signal": "mandate_unknown",
            "mandate_id": mandate_id,
            "plain": "gate_mandate_id is not a bound spend mandate id.",
        }
    try:
        row = db_mod.get_spend_mandate(mandate_id)
    except Exception:
        return {
            "applied": False,
            "halt": True,
            "body": body,
            "signal": "mandate_lookup_failed",
            "mandate_id": mandate_id,
            "plain": "Could not read the bound mandate — fail closed.",
        }
    if not row:
        return {
            "applied": False,
            "halt": True,
            "body": body,
            "signal": "mandate_unknown",
            "mandate_id": mandate_id,
            "plain": "No bound mandate for this id.",
        }
    terms = row.get("terms") if isinstance(row.get("terms"), dict) else {}
    if row.get("status") != "bound":
        return {
            "applied": False,
            "halt": True,
            "body": body,
            "signal": "mandate_revoked",
            "mandate_id": mandate_id,
            "fingerprint": row.get("fingerprint"),
            "plain": "Mandate is not bound.",
        }
    not_after = _parse_time(terms.get("not_after"))
    if not_after is None or not_after <= _utc_now():
        return {
            "applied": False,
            "halt": True,
            "body": body,
            "signal": "mandate_expired",
            "mandate_id": mandate_id,
            "fingerprint": row.get("fingerprint"),
            "plain": "Mandate is past not_after.",
        }
    auth_card = presented.get("card_id")
    stored_card = (row.get("card_id") or "").strip() or None
    if stored_card and auth_card and stored_card != auth_card:
        return {
            "applied": False,
            "halt": True,
            "body": body,
            "signal": "mandate_card_mismatch",
            "mandate_id": mandate_id,
            "fingerprint": row.get("fingerprint"),
            "plain": "This mandate is stored for a different Stripe card id.",
        }
    diverged = _divergences(presented, terms)
    if diverged:
        return {
            "applied": False,
            "halt": True,
            "body": body,
            "signal": "mandate_diverged",
            "mandate_id": mandate_id,
            "fingerprint": row.get("fingerprint"),
            "diverged": diverged,
            "plain": "Card metadata disagrees with the bound mandate: " + ", ".join(diverged) + ".",
        }
    overlaid = dict(body)
    mandate = dict(overlaid.get("mandate") or {})
    mandate["agent_id"] = terms["agent_id"]
    mandate["mandate_id"] = mandate_id
    mandate["mandate_fingerprint"] = row["fingerprint"]
    if terms.get("max_amount"):
        mandate["max_amount"] = terms["max_amount"]
    else:
        mandate.pop("max_amount", None)
    if terms.get("daily_cap"):
        mandate["daily_cap"] = terms["daily_cap"]
    else:
        mandate.pop("daily_cap", None)
    if terms.get("expected_counterparty"):
        mandate["expected_counterparty"] = terms["expected_counterparty"]
    else:
        mandate.pop("expected_counterparty", None)
    if terms.get("job_id"):
        mandate["job_id"] = terms["job_id"]
    if terms.get("allowed_categories"):
        mandate["allowed_categories"] = list(terms["allowed_categories"])
    overlaid["mandate"] = mandate
    if auth_card and not stored_card:
        latched = db_mod.latch_spend_mandate_card(mandate_id, auth_card)
        if latched and latched.get("card_id"):
            stored_card = latched["card_id"]
    return {
        "applied": True,
        "halt": False,
        "body": overlaid,
        "signal": None,
        "mandate_id": mandate_id,
        "fingerprint": row["fingerprint"],
        "terms": terms,
        "card_id": stored_card,
        "plain": "Auth is evaluated against the bound mandate.",
    }


def enforcement() -> dict[str, str]:
    return {
        "disagreement": (
            "Metadata that contradicts the bound terms is mandate_diverged."
        ),
        "omission": (
            "A swipe with no gate_mandate_id is mandate_omitted when the presented "
            "agent_id has a live bound mandate, or when this Stripe card id is already "
            "stored on a live mandate. Pass card_id at bind, or the first swipe that "
            "presents the id stores the card id."
        ),
        "still_metadata_path": (
            "A swipe that presents neither gate_mandate_id nor agent_id, on a card id "
            "that was not passed at bind and was never stored from a prior swipe, still "
            "uses the metadata cap. Clearing both fields on an unbound card is still open."
        ),
    }


def spec(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Bound spend mandate",
        "plain": (
            "Bind the cap before the swipe. Disagreement with the bound terms is "
            "mandate_diverged. Omitting gate_mandate_id is mandate_omitted when the "
            "agent_id on the swipe has a live mandate, or when the Stripe card id is "
            "already stored on one. A swipe that drops both the id and the agent_id, "
            "on a card that was never stored, still uses the metadata cap."
        ),
        "enforcement": enforcement(),
        "bind": f"{base}/v1/mandate/bind",
        "demo_bind": f"{base}/demo/mandate/bind",
        "read": f"{base}/v1/mandate/{{mandate_id}}",
        "card_metadata_key": "gate_mandate_id",
        "whose_check": (
            "The cardholder, the issuer, and any stranger with the mandate id "
            "can read the terms. The mouth compares the swipe to those terms."
        ),
    }
