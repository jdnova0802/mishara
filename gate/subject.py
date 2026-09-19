"""Subject Sovereignty — the right not to be the object.

Civilization II, first-class:
  Actors need Right-to-Act.
  Subjects need the power to REFUSE being written.

The boom gave every API a way to act *on* people.
It never gave people a stranger-verifiable way to deny the write.

Meterable events (billable today):
  - subject.clear   → clearance_id
  - subject.refuse  → refusal_id + refusal_digest
  - subject.verify  → verify of a refusal digest

Invariant: No living subject clearance ⇒ no admittance against that subject.
"""
from __future__ import annotations

import hashlib
import json
import threading
import time
import uuid
from datetime import datetime, timezone
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

SPEC = "gate-subject-v1"
STATUSES = ("clear", "refuse")

_lock = threading.Lock()
_subjects: dict[str, dict[str, Any]] = {}
_clearances: dict[str, dict[str, Any]] = {}
_refusals: dict[str, dict[str, Any]] = {}
_by_digest: dict[str, str] = {}


def _iso(ts: float | None = None) -> str:
    dt = datetime.fromtimestamp(ts or time.time(), tz=timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _reset_for_tests() -> None:
    with _lock:
        _subjects.clear()
        _clearances.clear()
        _refusals.clear()
        _by_digest.clear()


def _sign(digest_hex: str) -> str | None:
    try:
        return receipt_mod.sign_receipt_hash(digest_hex)
    except Exception:
        return None


def _finder_subject_refusal(row: dict) -> None:
    try:
        from gate import finder as finder_mod
    except ImportError:
        try:
            import finder as finder_mod
        except ImportError:
            return
    try:
        finder_mod.record_refusal(
            refusal_digest=str(row.get("refusal_digest") or ""),
            action=str(row.get("action") or "subject.write"),
            sink=str(row.get("sink") or "subject"),
            actor=str(row.get("actor") or ""),
            signals=["subject_refused", str(row.get("reason") or "refuse")],
            evaluation_id=row.get("refusal_id"),
            fingerprint=row.get("subject_id"),
        )
    except Exception:
        return


def register(
    *,
    subject_id: str,
    display_name: str = "",
    public_url: str = "",
) -> dict:
    sid = (subject_id or "").strip()
    if not sid:
        return {"ok": False, "reason": "subject_id_required", "subject": None}
    now = time.time()
    with _lock:
        row = _subjects.get(sid) or {
            "spec": SPEC,
            "subject_id": sid,
            "created_at": _iso(now),
            "created_at_unix": int(now),
        }
        if display_name:
            row["display_name"] = display_name.strip()
        row["updated_at"] = _iso(now)
        _subjects[sid] = dict(row)
    base = (public_url or "").rstrip("/")
    return {
        "ok": True,
        "reason": None,
        "subject": row,
        "meter": {"event": "subject.register", "billable": False},
        "well_known": f"{base}/.well-known/subjects/{sid}.json" if base else None,
        "invariant": "Subjects are first-class principals — not rows to be written.",
    }


def get(subject_id: str) -> dict | None:
    with _lock:
        row = _subjects.get((subject_id or "").strip())
        return dict(row) if row else None


def refuse(
    *,
    subject_id: str,
    action: str = "",
    sink: str = "",
    actor: str = "",
    reason: str = "subject_refuse",
    scope: dict | None = None,
    ttl_seconds: int = 86400 * 365,
    public_url: str = "",
) -> dict:
    """Mint a stranger-verifiable subject refusal (meterable)."""
    sid = (subject_id or "").strip()
    if not sid:
        return {"ok": False, "reason": "subject_id_required", "refusal": None}

    register(subject_id=sid, public_url=public_url)
    now = time.time()
    ttl = max(60, min(int(ttl_seconds), 86400 * 3650))
    refusal_id = f"sref_{uuid.uuid4().hex}"
    body = {
        "spec": SPEC,
        "kind": "refusal",
        "refusal_id": refusal_id,
        "subject_id": sid,
        "action": (action or "").strip() or None,
        "sink": (sink or "").strip() or None,
        "actor": (actor or "").strip() or None,
        "reason": (reason or "subject_refuse").strip(),
        "scope": scope if isinstance(scope, dict) else {},
        "status": "refuse",
        "refused_at": _iso(now),
        "refused_at_unix": int(now),
        "expires_at": _iso(now + ttl),
        "expires_at_unix": int(now + ttl),
    }
    digest = hashlib.sha256(_canonical(body).encode()).hexdigest()
    body["refusal_digest"] = digest
    sig = _sign(digest)
    if receipt_mod.signing_required() and not sig:
        return {"ok": False, "reason": "unsigned_halt", "refusal": None}
    body["signature"] = sig

    with _lock:
        _refusals[refusal_id] = dict(body)
        _by_digest[digest] = refusal_id

    _finder_subject_refusal(body)
    base = (public_url or "").rstrip("/")
    return {
        "ok": True,
        "reason": None,
        "refusal": body,
        "meter": {
            "event": "subject.refuse",
            "billable": True,
            "unit": "refusal",
            "id": refusal_id,
            "digest": digest,
        },
        "verify_url": f"{base}/v1/subject/verify" if base else None,
        "well_known": f"{base}/.well-known/subject-refusals/{digest}.json" if base else None,
        "invariant": "Subject refusal is product — stranger-verifiable non-writability.",
    }


def clear(
    *,
    subject_id: str,
    action: str,
    sink: str,
    actor: str = "",
    amount: float | None = None,
    ttl_seconds: int = 300,
    public_url: str = "",
) -> dict:
    """Issue a single-use-ish subject clearance for a specific act (meterable)."""
    sid = (subject_id or "").strip()
    act = (action or "").strip()
    snk = (sink or "").strip()
    if not sid or not act or not snk:
        return {
            "ok": False,
            "reason": "subject_action_sink_required",
            "clearance": None,
        }

    # Active matching refusal blocks clearance.
    blocked = active_refusal(subject_id=sid, action=act, sink=snk, actor=actor)
    if blocked:
        return {
            "ok": False,
            "reason": "subject_refused",
            "clearance": None,
            "refusal": blocked,
            "meter": {"event": "subject.clear_blocked", "billable": True, "id": blocked.get("refusal_id")},
        }

    register(subject_id=sid, public_url=public_url)
    now = time.time()
    ttl = max(30, min(int(ttl_seconds), 86400))
    clearance_id = f"sclear_{uuid.uuid4().hex}"
    body = {
        "spec": SPEC,
        "kind": "clearance",
        "clearance_id": clearance_id,
        "subject_id": sid,
        "action": act,
        "sink": snk,
        "actor": (actor or "").strip() or None,
        "amount": amount,
        "status": "clear",
        "cleared_at": _iso(now),
        "cleared_at_unix": int(now),
        "expires_at": _iso(now + ttl),
        "expires_at_unix": int(now + ttl),
        "consumed": False,
    }
    digest = hashlib.sha256(_canonical(body).encode()).hexdigest()
    body["clearance_digest"] = digest
    sig = _sign(digest)
    if receipt_mod.signing_required() and not sig:
        return {"ok": False, "reason": "unsigned_halt", "clearance": None}
    body["signature"] = sig

    with _lock:
        _clearances[clearance_id] = dict(body)

    base = (public_url or "").rstrip("/")
    return {
        "ok": True,
        "reason": None,
        "clearance": body,
        "meter": {
            "event": "subject.clear",
            "billable": True,
            "unit": "clearance",
            "id": clearance_id,
            "digest": digest,
        },
        "verify_url": f"{base}/v1/subject/verify" if base else None,
        "invariant": "Subject clearance is narrow, timed, and meterable.",
    }


def active_refusal(
    *,
    subject_id: str,
    action: str = "",
    sink: str = "",
    actor: str = "",
) -> dict | None:
    sid = (subject_id or "").strip()
    now = int(time.time())
    act = (action or "").strip()
    snk = (sink or "").strip()
    actr = (actor or "").strip()
    with _lock:
        rows = [dict(v) for v in _refusals.values() if v.get("subject_id") == sid]
    rows.sort(key=lambda r: int(r.get("refused_at_unix") or 0), reverse=True)
    for row in rows:
        if int(row.get("expires_at_unix") or 0) < now:
            continue
        # Broad refusal (no action/sink) blocks all.
        if not row.get("action") and not row.get("sink"):
            return row
        if row.get("action") and act and row.get("action") != act:
            continue
        if row.get("sink") and snk and row.get("sink") != snk:
            continue
        if row.get("actor") and actr and row.get("actor") != actr:
            continue
        return row
    return None


def require_for_admit(
    *,
    subject_id: str,
    action: str,
    sink: str,
    actor: str = "",
    clearance_id: str | None = None,
    subject_refuse: bool = False,
    public_url: str = "",
    consume: bool = True,
) -> dict:
    """Gate used by Admittance — fail closed on subject writes."""
    sid = (subject_id or "").strip()
    if not sid:
        return {
            "ok": True,
            "required": False,
            "status": "no_subject",
            "reason": None,
        }

    if subject_refuse:
        minted = refuse(
            subject_id=sid,
            action=action,
            sink=sink,
            actor=actor,
            reason="subject_refuse_flag",
            public_url=public_url,
        )
        return {
            "ok": False,
            "required": True,
            "status": "refuse",
            "reason": "subject_refused",
            "refusal": minted.get("refusal"),
            "meter": minted.get("meter"),
        }

    blocked = active_refusal(subject_id=sid, action=action, sink=sink, actor=actor)
    if blocked:
        return {
            "ok": False,
            "required": True,
            "status": "refuse",
            "reason": "subject_refused",
            "refusal": blocked,
            "meter": {
                "event": "subject.refuse_hit",
                "billable": True,
                "unit": "refusal_hit",
                "id": blocked.get("refusal_id"),
                "digest": blocked.get("refusal_digest"),
            },
        }

    cid = (clearance_id or "").strip()
    if cid:
        with _lock:
            clr = dict(_clearances[cid]) if cid in _clearances else None
        if not clr:
            return {
                "ok": False,
                "required": True,
                "status": "missing_clearance",
                "reason": "unknown_clearance",
            }
        now = int(time.time())
        if clr.get("consumed"):
            return {
                "ok": False,
                "required": True,
                "status": "clearance_consumed",
                "reason": "clearance_consumed",
                "clearance": clr,
            }
        if int(clr.get("expires_at_unix") or 0) < now:
            return {
                "ok": False,
                "required": True,
                "status": "clearance_expired",
                "reason": "clearance_expired",
                "clearance": clr,
            }
        if clr.get("subject_id") != sid:
            return {
                "ok": False,
                "required": True,
                "status": "clearance_mismatch",
                "reason": "clearance_subject_mismatch",
            }
        if clr.get("action") != action or clr.get("sink") != sink:
            return {
                "ok": False,
                "required": True,
                "status": "clearance_mismatch",
                "reason": "clearance_act_mismatch",
            }
        if consume:
            with _lock:
                if cid in _clearances:
                    _clearances[cid]["consumed"] = True
                    _clearances[cid]["consumed_at"] = _iso()
                    clr = dict(_clearances[cid])
            meter = {
                "event": "subject.clear_consume",
                "billable": True,
                "unit": "clearance_consume",
                "id": cid,
            }
        else:
            meter = {
                "event": "subject.clear_peek",
                "billable": False,
                "unit": "clearance_peek",
                "id": cid,
            }
        return {
            "ok": True,
            "required": True,
            "status": "clear",
            "reason": None,
            "clearance": clr,
            "meter": meter,
        }

    # Policy: subject present without clearance → fail closed (meter the deny).
    return {
        "ok": False,
        "required": True,
        "status": "clearance_required",
        "reason": "subject_clearance_required",
        "meter": {
            "event": "subject.clearance_required",
            "billable": True,
            "unit": "clearance_required",
            "id": sid,
        },
        "invariant": "Writing a subject requires living clearance — or a signed refusal.",
    }


def verify(certificate: dict | None = None, *, digest: str | None = None) -> dict:
    """Stranger-verify a subject refusal (meterable verify)."""
    import base64

    cert = dict(certificate) if isinstance(certificate, dict) else None
    dig = (digest or (cert or {}).get("refusal_digest") or "").strip()
    if not cert and dig:
        with _lock:
            rid = _by_digest.get(dig)
            cert = dict(_refusals[rid]) if rid and rid in _refusals else None
    if not cert:
        return {
            "spec": SPEC,
            "valid": False,
            "reason": "unknown_refusal",
            "meter": {"event": "subject.verify", "billable": True, "result": "unknown"},
        }

    body = {k: v for k, v in cert.items() if k not in ("refusal_digest", "signature")}
    expect = hashlib.sha256(_canonical(body).encode()).hexdigest()
    got = str(cert.get("refusal_digest") or "")
    if got != expect:
        return {
            "spec": SPEC,
            "valid": False,
            "reason": "digest_mismatch",
            "meter": {"event": "subject.verify", "billable": True, "result": "invalid"},
        }

    sig = cert.get("signature")
    if sig:
        pub = receipt_mod._ed25519_public_key_bytes()
        if pub:
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

            vk = Ed25519PublicKey.from_public_bytes(pub)
            raw = base64.urlsafe_b64decode(sig + "=" * (-len(sig) % 4))
            verified = False
            for msg in (bytes.fromhex(got), got.encode(), body and _canonical(body).encode()):
                try:
                    vk.verify(raw, msg)
                    verified = True
                    break
                except Exception:
                    continue
            if not verified:
                # Fallback: confirm against what sign_receipt_hash produces.
                again = _sign(got)
                if again != sig:
                    return {
                        "spec": SPEC,
                        "valid": False,
                        "reason": "bad_signature",
                        "meter": {
                            "event": "subject.verify",
                            "billable": True,
                            "result": "invalid",
                        },
                    }

    with _lock:
        known = got in _by_digest

    return {
        "spec": SPEC,
        "valid": True,
        "reason": None,
        "refusal": cert,
        "in_clearinghouse": known,
        "meter": {
            "event": "subject.verify",
            "billable": True,
            "unit": "verify",
            "id": cert.get("refusal_id"),
            "digest": got,
            "result": "valid",
        },
        "invariant": "Subject refusal is stranger-verifiable current-state truth.",
    }


def get_refusal(refusal_id: str) -> dict | None:
    with _lock:
        row = _refusals.get(refusal_id)
        return dict(row) if row else None


def get_refusal_by_digest(digest: str) -> dict | None:
    with _lock:
        rid = _by_digest.get((digest or "").strip())
        if not rid:
            return None
        row = _refusals.get(rid)
        return dict(row) if row else None


def list_for_subject(subject_id: str) -> dict:
    sid = (subject_id or "").strip()
    with _lock:
        refusals = [
            dict(v)
            for v in _refusals.values()
            if v.get("subject_id") == sid
        ]
        clearances = [
            dict(v)
            for v in _clearances.values()
            if v.get("subject_id") == sid
        ]
    refusals.sort(key=lambda r: int(r.get("refused_at_unix") or 0), reverse=True)
    clearances.sort(key=lambda r: int(r.get("cleared_at_unix") or 0), reverse=True)
    return {
        "subject_id": sid,
        "refusals": refusals,
        "clearances": clearances,
        "active_refusal": active_refusal(subject_id=sid),
    }


def manifest(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Gate Subject Sovereignty",
        "tagline": "The right not to be the object.",
        "description": (
            "First-class subject clearances and signed refusals. "
            "Actors need Right-to-Act; subjects need the power to deny the write. "
            "Clear, refuse, and verify are meterable events."
        ),
        "invariant": "No living subject clearance ⇒ no admittance against that subject.",
        "meterable": [
            "subject.clear",
            "subject.refuse",
            "subject.verify",
            "subject.clear_consume",
            "subject.refuse_hit",
        ],
        "register": f"{base}/v1/subject/register",
        "clear": f"{base}/v1/subject/clear",
        "refuse": f"{base}/v1/subject/refuse",
        "verify": f"{base}/v1/subject/verify",
        "well_known": f"{base}/.well-known/subject.json",
        "refusal_well_known": f"{base}/.well-known/subject-refusals/{{digest}}.json",
        "related": {
            "admittance": f"{base}/.well-known/admittance.json",
            "finder": f"{base}/.well-known/finder.json",
            "right_to_act": f"{base}/.well-known/right-to-act.json",
            "note": (
                "Right-to-Act gates the actor. Subject gates the target. "
                "Admittance requires both for irreversible writes."
            ),
        },
    }
