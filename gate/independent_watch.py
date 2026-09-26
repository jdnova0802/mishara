"""Independent evidence-head watchers — self-register, no sales loop.

Condition 2 from the Bitcoin-property pastable: unpaid outsiders appear in
`independent_watchers` because *they* decided to watch — not because Gate
onboarded a partner.

Protocol:
  1. GET  /.well-known/evidence-head.json  (or use watch script)
  2. POST /v1/evidence-watch/register  with handle + observed tree_size/root_hash
     matching the *live* head (proves fetch, not a guess).
  3. Re-POST to refresh; watchers go stale after STALE_AFTER_DAYS without refresh.
  4. Listed on /.well-known/evidence-watch.json when fresh.

Optional: Ed25519 public_key_b64 + signature over canonical observe payload
for stable identity across refreshes (recommended, not required for first ping).
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import evidence_log as evidence_log_mod
except ImportError:
    import evidence_log as evidence_log_mod

SPEC = "gate-independent-watcher-v1"
STALE_AFTER_DAYS = 14
HANDLE_RE = re.compile(r"^[a-z0-9][a-z0-9\-_]{2,63}$")


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _b64decode(s: str | None) -> bytes | None:
    if not s:
        return None
    t = s.strip().replace("-", "+").replace("_", "/")
    pad = "=" * (-len(t) % 4)
    try:
        return base64.b64decode(t + pad, validate=False)
    except Exception:
        return None


def live_head() -> dict[str, Any]:
    rows = db.list_bind_events_chronological()
    leaves = evidence_log_mod.log_from_rows(rows)
    head = evidence_log_mod.signed_tree_head(leaves)
    return {
        "tree_size": int(head.get("tree_size") or 0),
        "root_hash": (head.get("root_hash") or "").strip().lower(),
        "head_hash": head.get("head_hash"),
        "timestamp": head.get("timestamp"),
    }


def _ensure_table(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS independent_watchers (
            id TEXT PRIMARY KEY,
            handle TEXT NOT NULL UNIQUE,
            homepage TEXT,
            contact TEXT,
            public_key_b64 TEXT,
            public_key_fingerprint TEXT,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            last_tree_size INTEGER,
            last_root_hash TEXT,
            sample_count INTEGER NOT NULL DEFAULT 1,
            note TEXT,
            user_agent TEXT
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_ind_watch_last ON independent_watchers(last_seen_at)"
    )


def observe_canonical(*, handle: str, tree_size: int, root_hash: str, sampled_at: str) -> bytes:
    body = {
        "handle": handle,
        "root_hash": root_hash.lower(),
        "sampled_at": sampled_at,
        "spec": SPEC,
        "tree_size": int(tree_size),
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":")).encode("utf-8")


def verify_optional_signature(
    *,
    public_key_b64: str | None,
    signature_b64: str | None,
    message: bytes,
) -> dict[str, Any]:
    if not public_key_b64 and not signature_b64:
        return {"provided": False, "ok": True, "fingerprint": None}
    pub = _b64decode(public_key_b64)
    sig = _b64decode(signature_b64)
    if not pub or not sig or len(pub) != 32:
        return {"provided": True, "ok": False, "error": "bad_key_or_signature_encoding"}
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        Ed25519PublicKey.from_public_bytes(pub).verify(sig, message)
        fp = hashlib.sha256(pub).hexdigest()[:16]
        return {"provided": True, "ok": True, "fingerprint": fp}
    except Exception as exc:  # noqa: BLE001
        return {"provided": True, "ok": False, "error": f"verify_failed:{exc}"}


def register(payload: dict[str, Any], *, user_agent: str | None = None) -> dict[str, Any]:
    handle = (payload.get("handle") or "").strip().lower()
    if not HANDLE_RE.match(handle):
        return {
            "ok": False,
            "error": "invalid_handle",
            "plain": "handle must be 3–64 chars: [a-z0-9], starting alphanumeric; - and _ ok.",
        }

    try:
        tree_size = int(payload.get("tree_size"))
    except (TypeError, ValueError):
        return {"ok": False, "error": "tree_size_required"}
    root_hash = (payload.get("root_hash") or "").strip().lower()
    if not re.fullmatch(r"[0-9a-f]{64}", root_hash):
        return {"ok": False, "error": "root_hash_sha256_hex_required"}

    head = live_head()
    if tree_size != head["tree_size"] or root_hash != head["root_hash"]:
        return {
            "ok": False,
            "error": "head_mismatch",
            "plain": (
                "Observed head must match live /.well-known/evidence-head.json "
                "at submit time — fetch, then POST immediately."
            ),
            "live": head,
            "observed": {"tree_size": tree_size, "root_hash": root_hash},
        }

    sampled_at = (payload.get("sampled_at") or "").strip() or _now().isoformat()
    try:
        sample_dt = datetime.fromisoformat(sampled_at.replace("Z", "+00:00"))
        if sample_dt.tzinfo is None:
            sample_dt = sample_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return {"ok": False, "error": "sampled_at_invalid_iso"}
    skew = abs((_now() - sample_dt).total_seconds())
    if skew > 3600:
        return {"ok": False, "error": "sampled_at_too_skewed", "skew_seconds": skew}

    homepage = (payload.get("homepage") or "").strip() or None
    if homepage and not (homepage.startswith("https://") or homepage.startswith("http://")):
        return {"ok": False, "error": "homepage_must_be_http_s"}
    contact = (payload.get("contact") or "").strip() or None
    note = (payload.get("note") or "").strip()[:280] or None

    msg = observe_canonical(
        handle=handle,
        tree_size=tree_size,
        root_hash=root_hash,
        sampled_at=sampled_at,
    )
    sig_check = verify_optional_signature(
        public_key_b64=payload.get("public_key_b64"),
        signature_b64=payload.get("signature_b64"),
        message=msg,
    )
    if sig_check.get("provided") and not sig_check.get("ok"):
        return {"ok": False, "error": "signature_invalid", "detail": sig_check}

    now_iso = _now().isoformat()
    with db.db() as conn:
        _ensure_table(conn)
        existing = conn.execute(
            "SELECT * FROM independent_watchers WHERE handle = ?", (handle,)
        ).fetchone()
        if existing:
            # If they previously published a key, require same key (or matching sig).
            prior_fp = existing["public_key_fingerprint"]
            new_fp = sig_check.get("fingerprint")
            if prior_fp and new_fp and prior_fp != new_fp:
                return {
                    "ok": False,
                    "error": "key_fingerprint_mismatch",
                    "plain": "Handle already bound to a different public key.",
                }
            if prior_fp and not new_fp:
                return {
                    "ok": False,
                    "error": "signature_required",
                    "plain": "This handle was registered with a key; sign the observe payload.",
                }
            conn.execute(
                """UPDATE independent_watchers SET
                     last_seen_at = ?, last_tree_size = ?, last_root_hash = ?,
                     sample_count = sample_count + 1,
                     homepage = COALESCE(?, homepage),
                     contact = COALESCE(?, contact),
                     note = COALESCE(?, note),
                     user_agent = COALESCE(?, user_agent),
                     public_key_b64 = COALESCE(?, public_key_b64),
                     public_key_fingerprint = COALESCE(?, public_key_fingerprint)
                   WHERE handle = ?""",
                (
                    now_iso,
                    tree_size,
                    root_hash,
                    homepage,
                    contact,
                    note,
                    (user_agent or "")[:200] or None,
                    payload.get("public_key_b64") if sig_check.get("fingerprint") else None,
                    sig_check.get("fingerprint"),
                    handle,
                ),
            )
            row = conn.execute(
                "SELECT * FROM independent_watchers WHERE handle = ?", (handle,)
            ).fetchone()
            event = "refreshed"
        else:
            row_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO independent_watchers
                   (id, handle, homepage, contact, public_key_b64, public_key_fingerprint,
                    first_seen_at, last_seen_at, last_tree_size, last_root_hash,
                    sample_count, note, user_agent)
                   VALUES (?,?,?,?,?,?,?,?,?,?,1,?,?)""",
                (
                    row_id,
                    handle,
                    homepage,
                    contact,
                    payload.get("public_key_b64") if sig_check.get("fingerprint") else None,
                    sig_check.get("fingerprint"),
                    now_iso,
                    now_iso,
                    tree_size,
                    root_hash,
                    note,
                    (user_agent or "")[:200] or None,
                ),
            )
            row = conn.execute(
                "SELECT * FROM independent_watchers WHERE handle = ?", (handle,)
            ).fetchone()
            event = "registered"

    return {
        "ok": True,
        "event": event,
        "spec": SPEC,
        "watcher": public_watcher_row(dict(row)),
        "stale_after_days": STALE_AFTER_DAYS,
        "plain": (
            "Listed on /.well-known/evidence-watch.json while fresh. "
            "Re-POST the same shape at least every "
            f"{STALE_AFTER_DAYS} days. Unpaid. No partner agreement. "
            "Gate did not recruit you — you showed up."
        ),
        "their_production": False,
    }


def public_watcher_row(row: dict[str, Any]) -> dict[str, Any]:
    last = row.get("last_seen_at") or ""
    try:
        last_dt = datetime.fromisoformat(last.replace("Z", "+00:00"))
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        age_days = (_now() - last_dt).total_seconds() / 86400.0
        fresh = age_days <= STALE_AFTER_DAYS
    except ValueError:
        age_days = None
        fresh = False
    return {
        "handle": row.get("handle"),
        "homepage": row.get("homepage"),
        # contact omitted from public list by default (spam); present in register response
        "public_key_fingerprint": row.get("public_key_fingerprint"),
        "first_seen_at": row.get("first_seen_at"),
        "last_seen_at": row.get("last_seen_at"),
        "last_tree_size": row.get("last_tree_size"),
        "last_root_hash": row.get("last_root_hash"),
        "sample_count": row.get("sample_count"),
        "note": row.get("note"),
        "fresh": fresh,
        "age_days": round(age_days, 2) if age_days is not None else None,
        "independent": True,
        "paid_by_gate": False,
    }


def list_watchers(*, include_stale: bool = False) -> list[dict[str, Any]]:
    with db.db() as conn:
        _ensure_table(conn)
        rows = conn.execute(
            "SELECT * FROM independent_watchers ORDER BY last_seen_at DESC"
        ).fetchall()
    out = [public_watcher_row(dict(r)) for r in rows]
    if not include_stale:
        out = [w for w in out if w.get("fresh")]
    return out


def manifest(public_url: str = "") -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    watchers = list_watchers(include_stale=False)
    stale = list_watchers(include_stale=True)
    stale_only = [w for w in stale if not w.get("fresh")]
    return {
        "spec": SPEC,
        "register": f"{base}/v1/evidence-watch/register" if base else "/v1/evidence-watch/register",
        "how": [
            "GET /.well-known/evidence-head.json",
            "POST /v1/evidence-watch/register with handle + matching tree_size + root_hash",
            "Optional: Ed25519 sign canonical observe JSON; bind handle to key",
            f"Re-POST within {STALE_AFTER_DAYS} days or drop from fresh list",
        ],
        "canonical_observe": {
            "fields": ["spec", "handle", "tree_size", "root_hash", "sampled_at"],
            "encoding": "json sort_keys separators compact utf-8",
            "signed_over": "UTF-8 bytes of canonical JSON",
        },
        "stale_after_days": STALE_AFTER_DAYS,
        "fresh_count": len(watchers),
        "stale_count": len(stale_only),
        "independent_watchers": watchers,
        "plain": (
            "Self-register. No API key. No partner desk. Matching the live head "
            "is the only ticket. Gate's first-party GitHub Action does not count."
        ),
        "their_production": False,
    }
