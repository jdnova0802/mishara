"""Negative payout registry — prove a DENY existed.

Verification atom pipes avoid: shared, append-only registry of denied/blocked
payout fingerprints that counterparties can check without a pipe dashboard.

Stores privacy-preserving hashes only (no PII, no account numbers).
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

SPEC = "gate-deny-registry-v1"
_LOCK = threading.Lock()


def _db_path() -> str:
    base = os.getenv("GATE_DB_PATH", "").strip()
    if base:
        if base.endswith(".db"):
            return base[:-3] + ".deny.db"
        return base + ".deny.db"
    return os.path.join("/tmp", "gate-deny-registry.db")


def _conn() -> sqlite3.Connection:
    path = _db_path()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    c = sqlite3.connect(path, check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS deny_entries (
            id TEXT PRIMARY KEY,
            payout_hash TEXT NOT NULL,
            reason_code TEXT NOT NULL,
            rail TEXT,
            created_at TEXT NOT NULL,
            meta_json TEXT
        )
        """
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_deny_payout_hash ON deny_entries(payout_hash)"
    )
    return c


def payout_fingerprint(
    *,
    rail: str,
    amount: str,
    currency: str,
    destination: str,
    agent_id: str | None = None,
    memo: str | None = None,
) -> str:
    """Canonical hash of a payout attempt — no raw secrets in the registry."""
    payload = {
        "rail": (rail or "").strip().lower(),
        "amount": (amount or "").strip(),
        "currency": (currency or "").strip().upper(),
        "destination": (destination or "").strip(),
        "agent_id": (agent_id or "").strip() or None,
        "memo": (memo or "").strip() or None,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def register_deny(
    *,
    payout_hash: str | None = None,
    reason_code: str,
    rail: str | None = None,
    fingerprint_parts: dict | None = None,
    meta: dict | None = None,
) -> dict[str, Any]:
    h = (payout_hash or "").strip().lower()
    if not h and fingerprint_parts:
        h = payout_fingerprint(**fingerprint_parts)
    if not h or len(h) != 64:
        raise ValueError("payout_hash must be 64-char sha256 hex (or pass fingerprint_parts)")
    reason = (reason_code or "").strip() or "unspecified"
    created = datetime.now(timezone.utc).isoformat()
    entry_id = str(uuid.uuid4())
    with _LOCK:
        c = _conn()
        try:
            c.execute(
                """INSERT INTO deny_entries
                   (id, payout_hash, reason_code, rail, created_at, meta_json)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    entry_id,
                    h,
                    reason,
                    (rail or "").strip().lower() or None,
                    created,
                    json.dumps(meta) if meta else None,
                ),
            )
            c.commit()
        finally:
            c.close()
    return {
        "spec": SPEC,
        "id": entry_id,
        "payout_hash": h,
        "reason_code": reason,
        "rail": rail,
        "created_at": created,
        "their_production": False,
    }


def lookup(payout_hash: str) -> dict[str, Any]:
    h = (payout_hash or "").strip().lower()
    with _LOCK:
        c = _conn()
        try:
            rows = c.execute(
                """SELECT id, payout_hash, reason_code, rail, created_at
                   FROM deny_entries WHERE payout_hash = ?
                   ORDER BY created_at ASC""",
                (h,),
            ).fetchall()
        finally:
            c.close()
    denials = [dict(r) for r in rows]
    return {
        "spec": SPEC,
        "payout_hash": h,
        "denied": len(denials) > 0,
        "count": len(denials),
        "denials": denials,
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Negative payout registry",
        "atom": "Prove a DENY existed for a payout fingerprint — pipes keep denials private",
        "stores": "sha256 payout fingerprints only",
        "urls": {
            "manifest": f"{base}/.well-known/deny-registry.json",
            "lookup": f"{base}/v1/deny-registry/{{payout_hash}}",
            "register": f"{base}/v1/deny-registry",
            "fingerprint": f"{base}/v1/deny-registry/fingerprint",
        },
        "their_production": False,
    }
