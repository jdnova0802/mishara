"""Open-act blotter and the job seal a sheet can call.

One row per job_id. Each signed receipt on that job is a print.
The composite word is the latest print. LATE and BROKEN flash.
HOLD starts a new 60-minute window. HALT denies and names the reason code.
"""
from __future__ import annotations

from typing import Any

try:
    from gate import db
except ImportError:
    import db

try:
    from gate import seal_ui as seal_mod
except ImportError:
    import seal_ui as seal_mod

try:
    from gate import clock as clock_mod
except ImportError:
    import clock as clock_mod

try:
    from gate import demo_limit
except ImportError:
    import demo_limit

try:
    from gate import seal_anchor
except ImportError:
    import seal_anchor

SPEC = "gate-blotter-v1"
JOB_SEAL_SPEC = "gate-job-seal-v1"
FLASH = frozenset({"LATE", "BROKEN"})
ACTS = frozenset({"HOLD", "HALT"})


def _watcher_count() -> int:
    try:
        from gate import independent_watch as iw
    except ImportError:
        import independent_watch as iw
    try:
        return len(iw.list_watchers(include_stale=False))
    except Exception:
        return 0


def _prints(job_id: str, rows: list[dict]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in rows:
        if (row.get("job_id") or "").strip() != job_id:
            continue
        sealed = seal_mod.seal_event(row.get("id") or "", rows=rows)
        clock = sealed.get("clock") if isinstance(sealed.get("clock"), dict) else {}
        out.append(
            {
                "event_id": row.get("id"),
                "word": sealed.get("word"),
                "decision": row.get("decision"),
                "created_at": row.get("created_at"),
                "disposition": clock.get("disposition"),
                "due_at": clock.get("due_at"),
                "started_at": clock.get("started_at"),
                "reason_code": clock.get("reason_code"),
            }
        )
    return out


def quote(job_id: str, *, rows: list[dict] | None = None) -> dict[str, Any]:
    """GATE.SEAL(job_id). Latest print is the composite. Older prints stay on the tape."""
    jid = (job_id or "").strip()
    if rows is None:
        rows = db.list_bind_events_chronological()
    prints = _prints(jid, rows) if jid else []
    if not prints:
        body = {
            "spec": JOB_SEAL_SPEC,
            "formula": "GATE.SEAL",
            "job_id": jid or None,
            "composite": "MISSING",
            "flash": False,
            "prints": [],
            "print_count": 0,
            "head_watchers": _watcher_count(),
            "their_production": False,
        }
        return seal_anchor.annotate(body, rows or [])
    latest = prints[-1]
    word = latest.get("word") or "MISSING"
    body = {
        "spec": JOB_SEAL_SPEC,
        "formula": "GATE.SEAL",
        "job_id": jid,
        "composite": word,
        "flash": word in FLASH,
        "disposition": latest.get("disposition"),
        "due_at": latest.get("due_at"),
        "started_at": latest.get("started_at"),
        "reason_code": latest.get("reason_code"),
        "event_id": latest.get("event_id"),
        "prints": prints,
        "print_count": len(prints),
        "head_watchers": _watcher_count(),
        "their_production": False,
    }
    return seal_anchor.annotate(body, rows or [])


def book(*, limit: int = 40) -> dict[str, Any]:
    """Rows still open, LATE first, then soonest due."""
    rows = db.list_bind_events_chronological()
    seen: list[str] = []
    for row in rows:
        jid = (row.get("job_id") or "").strip()
        if jid and jid not in seen:
            seen.append(jid)
    open_rows: list[dict[str, Any]] = []
    for jid in seen:
        q = quote(jid, rows=rows)
        if q.get("disposition") != "open" and q.get("composite") != "LATE":
            continue
        open_rows.append(q)
    open_rows.sort(
        key=lambda q: (
            0 if q.get("composite") == "LATE" else 1,
            q.get("due_at") or "",
        )
    )
    return {
        "spec": SPEC,
        "rows": open_rows[:limit],
        "open_count": len(open_rows),
        "flash_count": sum(1 for q in open_rows if q.get("flash")),
        "head_watchers": _watcher_count(),
        "formula": "GATE.SEAL(job_id)",
        "formula_url": "/v1/seal/job?job_id=",
        "window_minutes": clock_mod.BIND_SETTLEMENT_WINDOW_MINUTES,
        "their_production": False,
    }


def act(job_id: str, decision: str) -> dict[str, Any]:
    """Append a HOLD or HALT print on a demo fuse. Does not edit the old receipt."""
    jid = (job_id or "").strip()
    name = (decision or "").strip().upper()
    if name not in ACTS:
        return {"ok": False, "error": "decision_must_be_HOLD_or_HALT"}
    if not jid:
        return {"ok": False, "error": "job_id_required"}
    latest = db.latest_bind_event_for_job(jid)
    if not latest:
        return {"ok": False, "error": "unknown_job"}
    fuse_id = (latest.get("fuse_id") or "").strip()
    if not demo_limit.validate_demo_fuse(fuse_id):
        return {"ok": False, "error": "demo_fuse_only"}
    event_id = db.record_bind_event(
        fuse_id=fuse_id,
        job_id=jid,
        decision=name,
        acted=False,
        hop={"state": "hold" if name == "HOLD" else "halt", "halt": name == "HALT"},
    )
    body = quote(jid)
    body["ok"] = True
    body["acted_event_id"] = event_id
    body["acted_decision"] = name
    return body


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Blotter",
        "promise": "Open acts, the clock on the row, and one key before the window ends.",
        "formula": "GATE.SEAL(job_id)",
        "formula_get": f"{base}/v1/seal/job?job_id=",
        "page": f"{base}/blotter",
        "api": f"{base}/v1/blotter",
        "act": f"{base}/v1/blotter/act",
        "acts": ["HOLD", "HALT"],
        "their_production": False,
    }
