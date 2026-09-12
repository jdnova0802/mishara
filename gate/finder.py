"""Finder — the Google that never happened.

Google indexed documents by link authority.
Finder indexes consequence: refusals, deaths, sinks, continuity —
whether an act may become real, was denied existence, or is dead.

The boom searched for pages. This searches for authority and its absence.
"""
from __future__ import annotations

import re
import threading
import time
from datetime import datetime, timezone
from typing import Any

try:
    from gate import sinks as sinks_mod
except ImportError:
    import sinks as sinks_mod

try:
    from gate import continuity as continuity_mod
except ImportError:
    import continuity as continuity_mod

try:
    from gate import mandate as mandate_mod
except ImportError:
    import mandate as mandate_mod

SPEC = "gate-finder-v1"
KINDS = ("refusal", "death", "sink", "continuity", "mandate")

_lock = threading.Lock()
_docs: list[dict[str, Any]] = []
_by_id: dict[str, dict[str, Any]] = {}


def _iso(ts: float | None = None) -> str:
    dt = datetime.fromtimestamp(ts or time.time(), tz=timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _reset_for_tests() -> None:
    with _lock:
        _docs.clear()
        _by_id.clear()


def _tokenize(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9_.:/-]+", (text or "").lower()) if t and len(t) > 1}


def _index_doc(doc: dict) -> dict:
    """Upsert a searchable consequence document."""
    did = str(doc.get("id") or "")
    if not did:
        return doc
    with _lock:
        if did in _by_id:
            # replace in place
            old = _by_id[did]
            try:
                idx = _docs.index(old)
                _docs[idx] = doc
            except ValueError:
                _docs.append(doc)
            _by_id[did] = doc
        else:
            _docs.append(doc)
            _by_id[did] = doc
    return doc


def record_refusal(
    *,
    refusal_digest: str,
    action: str = "",
    sink: str = "",
    actor: str = "",
    signals: list | None = None,
    evaluation_id: str | None = None,
    fingerprint: str | None = None,
) -> dict:
    digest = (refusal_digest or "").strip()
    if not digest:
        return {"ok": False, "reason": "refusal_digest_required"}
    now = time.time()
    hay = " ".join(
        [
            digest,
            action,
            sink,
            actor,
            evaluation_id or "",
            " ".join(str(s) for s in (signals or [])),
            "refusal nonexist no_go",
        ]
    )
    doc = {
        "spec": SPEC,
        "kind": "refusal",
        "id": f"refusal:{digest}",
        "refusal_digest": digest,
        "action": (action or "").strip() or None,
        "sink": (sink or "").strip() or None,
        "actor": (actor or "").strip() or None,
        "signals": list(signals or []),
        "evaluation_id": evaluation_id,
        "fingerprint": fingerprint,
        "indexed_at": _iso(now),
        "indexed_at_unix": int(now),
        "title": f"NONEXIST · {action or 'act'} → {sink or 'sink'}",
        "summary": (
            f"Signed refusal: {action or 'act'} may not EXIST at {sink or 'sink'}. "
            f"Digest {digest[:16]}…"
        ),
        "_haystack": hay.lower(),
        "invariant": "Refusal is a first-class searchable object — not a log line.",
    }
    _index_doc(doc)
    return {"ok": True, "doc": {k: v for k, v in doc.items() if k != "_haystack"}}


def record_death(certificate: dict) -> dict:
    cert = certificate if isinstance(certificate, dict) else {}
    death_id = str(cert.get("death_id") or "").strip()
    if not death_id:
        return {"ok": False, "reason": "death_id_required"}
    subj = cert.get("subject") if isinstance(cert.get("subject"), dict) else {}
    now = time.time()
    killed = cert.get("cascade_killed") or []
    hay = " ".join(
        [
            death_id,
            str(cert.get("reason") or ""),
            str(subj.get("mandate_id") or ""),
            str(subj.get("human_principal_id") or ""),
            str(subj.get("human_root_digest") or ""),
            str(subj.get("agent_id") or ""),
            " ".join(str(x) for x in killed),
            "death mortality dead",
        ]
    )
    doc = {
        "spec": SPEC,
        "kind": "death",
        "id": f"death:{death_id}",
        "death_id": death_id,
        "reason": cert.get("reason"),
        "subject": subj,
        "cascade_killed": list(killed),
        "died_at": cert.get("died_at"),
        "epoch": cert.get("epoch"),
        "certificate": cert,
        "indexed_at": _iso(now),
        "indexed_at_unix": int(now),
        "title": f"DEAD · {subj.get('agent_id') or subj.get('human_principal_id') or death_id}",
        "summary": (
            f"Death certificate {death_id}: authority voided "
            f"({cert.get('reason') or 'mortality'}). "
            f"{len(killed)} mandate(s) cascade-killed."
        ),
        "_haystack": hay.lower(),
        "invariant": "Death is stranger-searchable current-state truth.",
    }
    _index_doc(doc)
    return {"ok": True, "doc": {k: v for k, v in doc.items() if k != "_haystack"}}


def record_continuity(event: dict) -> dict:
    ev = event if isinstance(event, dict) else {}
    cid = str(ev.get("continuity_id") or "").strip()
    if not cid:
        return {"ok": False, "reason": "continuity_id_required"}
    now = time.time()
    hay = " ".join(
        [
            cid,
            str(ev.get("human_principal_id") or ""),
            str(ev.get("event") or ""),
            str(ev.get("reason") or ""),
            str(ev.get("agent_id") or ""),
            "continuity incapacity departure",
        ]
    )
    doc = {
        "spec": SPEC,
        "kind": "continuity",
        "id": f"continuity:{cid}",
        "continuity_id": cid,
        "human_principal_id": ev.get("human_principal_id"),
        "event": ev.get("event"),
        "reason": ev.get("reason"),
        "death": ev.get("death"),
        "indexed_at": _iso(now),
        "indexed_at_unix": int(now),
        "title": f"CONTINUITY · {ev.get('event')} · {ev.get('human_principal_id')}",
        "summary": (
            f"Human continuity {ev.get('event')}: "
            f"{ev.get('human_principal_id')} — {ev.get('reason')}"
        ),
        "_haystack": hay.lower(),
        "invariant": "Continuity ends the right to authorize — searchable, not folklore.",
    }
    _index_doc(doc)
    return {"ok": True, "doc": {k: v for k, v in doc.items() if k != "_haystack"}}


def reindex_sinks() -> int:
    """Refresh sink registry documents into the finder."""
    n = 0
    now = time.time()
    for row in sinks_mod.list_sinks():
        sid = row.get("sink_id")
        hay = " ".join(
            [
                str(sid),
                str(row.get("class") or ""),
                str(row.get("irreversibility") or ""),
                str(row.get("description") or ""),
                "sink irreversible",
            ]
        )
        doc = {
            "spec": SPEC,
            "kind": "sink",
            "id": f"sink:{sid}",
            "sink_id": sid,
            "class": row.get("class"),
            "irreversibility": row.get("irreversibility"),
            "burn_required": row.get("burn_required"),
            "mandate_required": row.get("mandate_required"),
            "description": row.get("description"),
            "indexed_at": _iso(now),
            "indexed_at_unix": int(now),
            "title": f"SINK · {sid} · {row.get('irreversibility')}",
            "summary": row.get("description") or f"{row.get('class')} / {row.get('irreversibility')}",
            "_haystack": hay.lower(),
            "invariant": "Consequence has a type. Unknown sink fails closed.",
        }
        _index_doc(doc)
        n += 1
    return n


def search(
    q: str = "",
    *,
    kind: str | None = None,
    limit: int = 25,
) -> dict:
    """Search the consequence web — refusals, deaths, sinks, continuity."""
    reindex_sinks()
    query = (q or "").strip()
    tokens = _tokenize(query)
    kind_f = (kind or "").strip().lower() or None
    if kind_f and kind_f not in KINDS:
        return {
            "spec": SPEC,
            "ok": False,
            "reason": "unknown_kind",
            "kinds": list(KINDS),
            "results": [],
        }

    with _lock:
        corpus = list(_docs)

    scored: list[tuple[int, dict]] = []
    for doc in corpus:
        if kind_f and doc.get("kind") != kind_f:
            continue
        hay = doc.get("_haystack") or ""
        if not tokens:
            score = int(doc.get("indexed_at_unix") or 0)
        else:
            score = 0
            for t in tokens:
                if t in hay:
                    score += 10
                if t == str(doc.get("kind") or ""):
                    score += 5
                if t in str(doc.get("id") or "").lower():
                    score += 8
            if score <= 0:
                continue
        public = {k: v for k, v in doc.items() if k != "_haystack"}
        scored.append((score, public))

    scored.sort(key=lambda x: (-x[0], -int(x[1].get("indexed_at_unix") or 0)))
    limit_n = max(1, min(int(limit or 25), 100))
    results = [d for _, d in scored[:limit_n]]

    return {
        "spec": SPEC,
        "ok": True,
        "q": query,
        "kind": kind_f,
        "count": len(results),
        "results": results,
        "thesis": (
            "Google indexed documents by who linked to whom. "
            "Finder indexes whether an act may become real — and when that right is dead."
        ),
        "invariant": "The boom searched for pages. This searches for authority and its absence.",
    }


def get(doc_id: str) -> dict | None:
    with _lock:
        row = _by_id.get(doc_id)
        if not row:
            return None
        return {k: v for k, v in row.items() if k != "_haystack"}


def stats() -> dict:
    reindex_sinks()
    with _lock:
        counts: dict[str, int] = {}
        for d in _docs:
            k = str(d.get("kind") or "unknown")
            counts[k] = counts.get(k, 0) + 1
        total = len(_docs)
    return {
        "spec": SPEC,
        "total": total,
        "by_kind": counts,
        "thesis": "The Google that never happened — an index of consequence, not pages.",
    }


def manifest(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Gate Finder",
        "tagline": "The Google that never happened",
        "description": (
            "Search refusals, death certificates, typed sinks, and human continuity. "
            "Not pages — whether an act may become real."
        ),
        "invariant": (
            "Google ranked documents by link authority. "
            "Finder ranks consequence by living authority and its absence."
        ),
        "kinds": list(KINDS),
        "search": f"{base}/v1/finder/search",
        "stats": f"{base}/v1/finder/stats",
        "page": f"{base}/finder",
        "well_known": f"{base}/.well-known/finder.json",
        "related": {
            "sinks": f"{base}/.well-known/sinks.json",
            "continuity": f"{base}/.well-known/continuity.json",
            "mandate": f"{base}/.well-known/mandate.json",
            "right_to_act": f"{base}/.well-known/right-to-act.json",
            "mortality_federation": f"{base}/v1/mandate/deaths/export",
        },
    }


# Eager sink seed so empty finder still has consequence nouns.
reindex_sinks()
