"""Item 125 — per-action billing ledger.

Points at a Gate/Verra receipt. Idempotency key is Stripe-style retry safety.
Items 126–128 (rate card, dispute, fee-split) are named and not schema'd.
"""
from __future__ import annotations

import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPEC = "gate-ledger-entry-v1"
NOT_SCHEMA = ("rate_card", "dispute", "fee_split", "split", "risk_price")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime | None = None) -> str:
    return (dt or _now()).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _path() -> Path:
    return Path(os.getenv("GATE_LEDGER_PATH") or Path(__file__).resolve().parent / "data" / "ledger.json")


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


def list_entries() -> list[dict[str, Any]]:
    return list(_load().get("entries") or [])


def post(
    *,
    idempotency_key: str,
    receipt_id: str,
    debit_account: str,
    credit_account: str,
    amount: Any,
    extra: dict[str, Any] | None = None,
    persist: bool = True,
) -> dict[str, Any]:
    body = extra if isinstance(extra, dict) else {}
    hits = [k for k in NOT_SCHEMA if body.get(k) not in (None, "", False)]
    if hits:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "not_schema",
            "refused": hits,
            "plain": "Rate card, billing dispute, and fee-split are named gaps (126–128), not this ledger.",
        }
    key = (idempotency_key or "").strip()
    rid = (receipt_id or "").strip()
    debit = (debit_account or "").strip()
    credit = (credit_account or "").strip()
    if not key or not rid or not debit or not credit:
        return {
            "spec": SPEC,
            "ok": False,
            "error": "fields_required",
            "plain": "idempotency_key, receipt_id, debit_account, and credit_account are required.",
        }
    try:
        amt = float(amount)
    except (TypeError, ValueError):
        return {
            "spec": SPEC,
            "ok": False,
            "error": "amount_required",
            "plain": "Amount is a number. This ledger does not price the action.",
        }

    store = _load()
    for existing in store["entries"]:
        if existing.get("idempotency_key") == key:
            return {**existing, "ok": True, "replayed": True}

    rec = {
        "spec": SPEC,
        "ok": True,
        "replayed": False,
        "entry_id": "led_" + uuid.uuid4().hex[:12],
        "idempotency_key": key,
        "receipt_id": rid,
        "debit_account": debit,
        "credit_account": credit,
        "amount": amt,
        "posted_at": _iso(),
        "duplicates_receipt": False,
        "plain": "Posted. Points at the receipt. Does not copy it. 126–128 are not in this table.",
    }
    if persist:
        store["entries"].append(rec)
        _save(store)
    return rec
