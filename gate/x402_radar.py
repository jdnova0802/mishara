"""Agent-pay radar — public graded directory of x402 endpoints.

Attention object that is also a trust object: shareable grades → wire → weld.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any
from urllib.parse import urlparse

SPEC = "gate-x402-radar-v1"
CARD_SPEC = "gate-x402-radar-card-v1"
_HOST_RE = re.compile(r"^[a-z0-9.-]+(?::\d+)?$", re.I)

try:
    from gate import db as db_mod
    from gate import x402_audit as x402_audit_mod
except ImportError:
    import db as db_mod
    import x402_audit as x402_audit_mod


def _canonical_url(url: str) -> str | None:
    raw = (url or "").strip()
    if not raw:
        return None
    if not re.match(r"^https?://", raw, re.I):
        raw = "https://" + raw
    parsed = urlparse(raw)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    host = parsed.netloc.lower()
    path = parsed.path or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
    return f"{parsed.scheme}://{host}{path}"


def entry_id_for_url(url: str) -> str | None:
    canon = _canonical_url(url)
    if not canon:
        return None
    return hashlib.sha256(canon.encode()).hexdigest()[:20]


def _host_of(url: str) -> str:
    return urlparse(url).netloc.lower()


def upsert_from_audit(audit: dict) -> dict | None:
    """Index a successful-or-graded audit into the public radar. Skips invalid URLs."""
    url = audit.get("url")
    if not url or audit.get("error") == "invalid_url":
        return None
    canon = _canonical_url(str(url))
    if not canon:
        return None
    eid = entry_id_for_url(canon)
    if not eid:
        return None

    grade = str(audit.get("grade") or "F")
    score = int(audit.get("score") or 0)
    ok = 1 if audit.get("ok") else 0
    findings = audit.get("findings") or []
    now = db_mod.utc_now()

    with db_mod.db() as conn:
        existing = conn.execute(
            "SELECT probe_count, first_seen_at FROM x402_radar_entries WHERE id = ?",
            (eid,),
        ).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE x402_radar_entries SET
                    host = ?, url = ?, grade = ?, score = ?, ok = ?,
                    http_status = ?, pay_to = ?, amount_atomic = ?, network = ?,
                    scheme = ?, findings_json = ?, probe_count = ?, last_seen_at = ?
                WHERE id = ?
                """,
                (
                    _host_of(canon),
                    canon,
                    grade,
                    score,
                    ok,
                    audit.get("http_status"),
                    audit.get("pay_to"),
                    str(audit.get("amount_atomic") or "") or None,
                    audit.get("network"),
                    audit.get("scheme"),
                    json.dumps(findings),
                    int(existing["probe_count"] or 0) + 1,
                    now,
                    eid,
                ),
            )
            first_seen = existing["first_seen_at"]
            probe_count = int(existing["probe_count"] or 0) + 1
        else:
            conn.execute(
                """
                INSERT INTO x402_radar_entries (
                    id, host, url, grade, score, ok, http_status, pay_to,
                    amount_atomic, network, scheme, findings_json,
                    probe_count, first_seen_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?, ?)
                """,
                (
                    eid,
                    _host_of(canon),
                    canon,
                    grade,
                    score,
                    ok,
                    audit.get("http_status"),
                    audit.get("pay_to"),
                    str(audit.get("amount_atomic") or "") or None,
                    audit.get("network"),
                    audit.get("scheme"),
                    json.dumps(findings),
                    now,
                    now,
                ),
            )
            first_seen = now
            probe_count = 1

    return {
        "id": eid,
        "host": _host_of(canon),
        "url": canon,
        "grade": grade,
        "score": score,
        "ok": bool(ok),
        "http_status": audit.get("http_status"),
        "pay_to": audit.get("pay_to"),
        "amount_atomic": audit.get("amount_atomic"),
        "network": audit.get("network"),
        "scheme": audit.get("scheme"),
        "findings": findings,
        "probe_count": probe_count,
        "first_seen_at": first_seen,
        "last_seen_at": now,
    }


def probe_and_index(url: str, *, timeout: float = 12.0) -> dict:
    """Run free audit and upsert into radar. Returns audit + radar entry."""
    audit = x402_audit_mod.audit_endpoint(url, timeout=timeout)
    entry = upsert_from_audit(audit)
    return {"spec": SPEC, "audit": audit, "entry": entry}


def list_entries(*, limit: int = 50, min_score: int | None = None) -> list[dict]:
    limit = max(1, min(200, int(limit or 50)))
    with db_mod.db() as conn:
        if min_score is not None:
            rows = conn.execute(
                """
                SELECT * FROM x402_radar_entries
                WHERE score >= ?
                ORDER BY score DESC, last_seen_at DESC
                LIMIT ?
                """,
                (int(min_score), limit),
            ).fetchall()
        else:
            rows = conn.execute(
                """
                SELECT * FROM x402_radar_entries
                ORDER BY score DESC, last_seen_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
    return [_row_to_entry(r) for r in rows]


def get_entry(entry_id: str) -> dict | None:
    eid = (entry_id or "").strip().lower()
    if not eid or len(eid) > 64:
        return None
    with db_mod.db() as conn:
        row = conn.execute(
            "SELECT * FROM x402_radar_entries WHERE id = ?", (eid,)
        ).fetchone()
    return _row_to_entry(row) if row else None


def get_entry_by_host(host: str) -> dict | None:
    h = (host or "").strip().lower()
    if not h or not _HOST_RE.match(h):
        return None
    with db_mod.db() as conn:
        row = conn.execute(
            """
            SELECT * FROM x402_radar_entries
            WHERE host = ?
            ORDER BY score DESC, last_seen_at DESC
            LIMIT 1
            """,
            (h,),
        ).fetchone()
    return _row_to_entry(row) if row else None


def _row_to_entry(row: Any) -> dict:
    findings: list = []
    raw = row["findings_json"] if row["findings_json"] is not None else "[]"
    try:
        findings = json.loads(raw) if raw else []
    except json.JSONDecodeError:
        findings = []
    return {
        "id": row["id"],
        "host": row["host"],
        "url": row["url"],
        "grade": row["grade"],
        "score": int(row["score"] or 0),
        "ok": bool(row["ok"]),
        "http_status": row["http_status"],
        "pay_to": row["pay_to"],
        "amount_atomic": row["amount_atomic"],
        "network": row["network"],
        "scheme": row["scheme"],
        "findings": findings,
        "probe_count": int(row["probe_count"] or 1),
        "first_seen_at": row["first_seen_at"],
        "last_seen_at": row["last_seen_at"],
    }


def public_manifest(public_url: str, *, limit: int = 50) -> dict:
    base = (public_url or "").rstrip("/")
    entries = list_entries(limit=limit)
    return {
        "spec": SPEC,
        "title": "Agent-pay radar",
        "description": (
            "Public graded directory of x402 / HTTP 402 pay endpoints. "
            "Submit a URL to probe and index. Free. Share the grade card."
        ),
        "human_url": f"{base}/radar",
        "submit": f"{base}/api/x402/radar?url=",
        "card_template": f"{base}/radar/e/{{id}}",
        "badge_template": f"{base}/radar/badge/{{id}}.svg",
        "wire": f"{base}/api/x402/wire",
        "weld": f"{base}/operator",
        "count": len(entries),
        "entries": [
            {
                **e,
                "card_url": f"{base}/radar/e/{e['id']}",
                "badge_url": f"{base}/radar/badge/{e['id']}.svg",
            }
            for e in entries
        ],
    }


def card_payload(entry: dict, public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    eid = entry["id"]
    return {
        "spec": CARD_SPEC,
        "entry": entry,
        "card_url": f"{base}/radar/e/{eid}",
        "badge_url": f"{base}/radar/badge/{eid}.svg",
        "audit_url": f"{base}/audit?url={entry['url']}",
        "wire_url": (
            f"{base}/api/x402/wire?domain={entry['host']}"
            f"&email=you@example.com&audit_url={entry['url']}"
        ),
        "weld_url": f"{base}/operator",
        "share_text": (
            f"x402 grade {entry['grade']} ({entry['score']}/100) — {entry['host']}. "
            f"Probe: {base}/radar/e/{eid}"
        ),
    }


def badge_svg(entry: dict) -> str:
    """Embeddable SVG trust mark — grade letter + score."""
    grade = str(entry.get("grade") or "F")
    score = int(entry.get("score") or 0)
    ok = bool(entry.get("ok"))
    fill = "#1a3d2e" if ok and grade in ("A", "B") else "#3d2a1a" if grade in ("C", "D") else "#3d1a1a"
    accent = "#3dffa8" if ok and grade in ("A", "B") else "#ffb347" if grade in ("C", "D") else "#ff6b6b"
    host = str(entry.get("host") or "x402")[:28]
    # Escape for XML text
    host_safe = (
        host.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="200" height="40" role="img" aria-label="x402 grade {grade}">
  <title>Gate x402 radar · {grade} · {score}/100</title>
  <rect width="200" height="40" rx="6" fill="{fill}"/>
  <rect x="0" y="0" width="40" height="40" rx="6" fill="{accent}"/>
  <text x="20" y="26" text-anchor="middle" font-family="ui-monospace,monospace" font-size="18" font-weight="700" fill="#0a0a0a">{grade}</text>
  <text x="52" y="17" font-family="ui-sans-serif,system-ui,sans-serif" font-size="11" font-weight="600" fill="#f0f0f0">x402 · {score}/100</text>
  <text x="52" y="31" font-family="ui-monospace,monospace" font-size="10" fill="#a0a0a0">{host_safe}</text>
</svg>
"""
