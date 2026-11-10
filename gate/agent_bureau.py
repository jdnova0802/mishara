"""Items 50–55 + CDPI 75–79. No fake 100/100. No fake ZK. No fake adopters."""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SPEC_DID = "gate-agent-did-v1"
SPEC_CDPI = "gate-cdpi-v1"
SPEC_ZK = "gate-zk-linkage-v1"
SPEC_REG = "gate-agent-registration-v0.1"
HALF_LIFE_DAYS = 90.0
W_ACCURACY = 0.55
W_SEVERITY = 0.25
W_TREND = 0.20
PERCENTILE_MIN = 5


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _parse(ts: str | None) -> datetime | None:
    if not ts:
        return None
    s = ts.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        return None


def _path() -> Path:
    return Path(os.getenv("GATE_AGENTS_PATH") or Path(__file__).resolve().parent / "data" / "agents.json")


def _load() -> dict[str, Any]:
    p = _path()
    if not p.exists():
        return {"agents": {}, "disputes": []}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"agents": {}, "disputes": []}
    if not isinstance(data, dict):
        return {"agents": {}, "disputes": []}
    return {
        "agents": dict(data.get("agents") or {}),
        "disputes": list(data.get("disputes") or []),
    }


def _save(store: dict[str, Any]) -> None:
    p = _path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps({"spec": SPEC_DID, "agents": store["agents"], "disputes": store["disputes"]}, indent=2),
        encoding="utf-8",
    )


def fingerprint(public_key_b64: str) -> str:
    raw = (public_key_b64 or "").strip().encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:40]


def did_for(public_key_b64: str) -> str:
    return "did:gate:" + fingerprint(public_key_b64)


def register_agent(*, public_key_b64: str, fuse_id: str = "", label: str = "") -> dict[str, Any]:
    public_key_b64 = (public_key_b64 or "").strip()
    if len(public_key_b64) < 16:
        raise ValueError("public_key_required")
    did = did_for(public_key_b64)
    store = _load()
    existing = store["agents"].get(did)
    if existing:
        if fuse_id and not existing.get("fuse_id"):
            existing["fuse_id"] = fuse_id.strip()
            _save(store)
        return existing
    agent = {
        "spec": SPEC_DID,
        "did": did,
        "public_key_b64": public_key_b64,
        "fingerprint": fingerprint(public_key_b64),
        "fuse_id": (fuse_id or "").strip() or None,
        "label": (label or "").strip() or None,
        "created_at": _now().replace(microsecond=0).isoformat(),
        "session": False,
        "plain": "Key-bound identity. It survives a new session and a new company field.",
    }
    store["agents"][did] = agent
    _save(store)
    return agent


def get_agent(did: str) -> dict[str, Any] | None:
    did = (did or "").strip()
    return _load()["agents"].get(did)


def agent_by_fuse(fuse_id: str) -> dict[str, Any] | None:
    fuse_id = (fuse_id or "").strip()
    if not fuse_id:
        return None
    for agent in _load()["agents"].values():
        if agent.get("fuse_id") == fuse_id:
            return agent
    return None


def zk_stub() -> dict[str, Any]:
    return {
        "spec": SPEC_ZK,
        "item": 51,
        "built": False,
        "needs": "zero_knowledge_research",
        "plain": (
            "Cannot prove a CDPI threshold without revealing receipts yet. "
            "That is item 51, research — not a fake proof."
        ),
    }


def registration_spec() -> dict[str, Any]:
    return {
        "spec": SPEC_REG,
        "dated": "2026-11-10",
        "adopters": [],
        "plain": (
            "A registration standard nobody else joins is not a standard. "
            "Adopters list is empty on purpose."
        ),
        "did_method": "did:gate:<sha256-hex-40>",
        "register": "/v1/agents/register",
        "lookup": "/v1/trust-record",
    }


def decay_weight(age_days: float, *, disputed: bool) -> float:
    if disputed:
        return 1.0
    if age_days <= 0:
        return 1.0
    return 0.5 ** (age_days / HALF_LIFE_DAYS)


def _severity(row: dict[str, Any]) -> float:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    checks = hop.get("checks") if isinstance(hop.get("checks"), dict) else {}
    premium = hop.get("premium") if hop.get("premium") is not None else checks.get("premium")
    try:
        if premium is not None:
            return min(max(float(premium) / 100000.0, 0.0), 1.0)
    except (TypeError, ValueError):
        pass
    d = str(row.get("decision") or "").upper()
    if d == "HALT":
        return 0.7
    if d == "BLOCK":
        return 0.6
    if d == "HOLD":
        return 0.3
    return 0.0


def open_dispute_ids(disputes: list[dict[str, Any]]) -> set[str]:
    return {str(d.get("event_id")) for d in disputes if str(d.get("status") or "").upper() == "OPEN"}


def file_dispute(*, event_id: str, reason: str, did: str = "") -> dict[str, Any]:
    event_id = (event_id or "").strip()
    reason = (reason or "").strip()
    if not event_id or not reason:
        raise ValueError("event_id_and_reason_required")
    store = _load()
    rec = {
        "id": "dsp_" + uuid.uuid4().hex[:12],
        "event_id": event_id,
        "did": (did or "").strip() or None,
        "reason": reason[:500],
        "status": "OPEN",
        "created_at": _now().replace(microsecond=0).isoformat(),
        "resolved_at": None,
        "history_erased": False,
        "plain": "Logged. The BLOCK row stays. Decay is frozen while OPEN.",
    }
    store["disputes"].append(rec)
    _save(store)
    return rec


def resolve_dispute(dispute_id: str, status: str) -> dict[str, Any]:
    status = (status or "").strip().upper()
    if status not in {"OVERTURNED", "UPHELD"}:
        raise ValueError("status_must_be_overturned_or_upheld")
    store = _load()
    for rec in store["disputes"]:
        if rec.get("id") == dispute_id:
            rec["status"] = status
            rec["resolved_at"] = _now().replace(microsecond=0).isoformat()
            rec["history_erased"] = False
            _save(store)
            return rec
    raise ValueError("not_found")


def list_disputes() -> list[dict[str, Any]]:
    return list(_load()["disputes"])


def score_agent(
    events: list[dict[str, Any]],
    disputes: list[dict[str, Any]] | None = None,
    *,
    now: datetime | None = None,
    peer_composites: list[float] | None = None,
) -> dict[str, Any]:
    now = now or _now()
    disputes = disputes or []
    open_ids = open_dispute_ids(disputes)
    closed = [d for d in disputes if str(d.get("status") or "").upper() in {"OVERTURNED", "UPHELD"}]
    overturned = {str(d.get("event_id")) for d in closed if str(d.get("status")).upper() == "OVERTURNED"}
    closed_ids = {str(d.get("event_id")) for d in closed}

    hot = [e for e in events if str(e.get("decision") or "").upper() in {"BLOCK", "HOLD", "HALT"}]
    resolved_hot = [e for e in hot if str(e.get("id")) in closed_ids]
    if not resolved_hot:
        accuracy = None
        accuracy_note = "Unscored until a BLOCK/HOLD dispute closes. Not 100/100."
    else:
        kept = sum(1 for e in resolved_hot if str(e.get("id")) not in overturned)
        accuracy = kept / len(resolved_hot)
        accuracy_note = "Proxy: closed disputes that did not overturn the mark."

    sev_load = 0.0
    for e in hot:
        when = _parse(str(e.get("created_at") or ""))
        age = max((now - when).total_seconds() / 86400.0, 0.0) if when else 0.0
        disputed = str(e.get("id")) in open_ids
        chain = 1.0 + (0.15 if e.get("prev_receipt_hash") else 0.0)
        sev_load += _severity(e) * decay_weight(age, disputed=disputed) * chain
    severity_term = 1.0 / (1.0 + sev_load)

    recent = [e for e in events if str(e.get("decision") or "").upper() in {"BLOCK", "HALT"}]
    trend = 1.0 if not recent else max(0.0, 1.0 - min(len(recent) / max(len(events), 1), 1.0))

    composite = None
    if accuracy is not None:
        composite = round(100.0 * (W_ACCURACY * accuracy + W_SEVERITY * severity_term + W_TREND * trend), 2)

    percentile = None
    if composite is not None and peer_composites and len(peer_composites) >= PERCENTILE_MIN:
        below = sum(1 for p in peer_composites if p <= composite)
        percentile = round(100.0 * below / len(peer_composites), 1)

    return {
        "spec": SPEC_CDPI,
        "weights": {"accuracy": W_ACCURACY, "severity": W_SEVERITY, "trend": W_TREND},
        "half_life_days": HALF_LIFE_DAYS,
        "accuracy": accuracy,
        "accuracy_note": accuracy_note,
        "severity_term": severity_term,
        "severity_load": sev_load,
        "trend": trend,
        "composite": composite,
        "percentile": percentile,
        "static_100": False,
        "hard_binding": False,
        "binding": "soft",
        "not_tamper_evident_proof": True,
        "event_count": len(events),
        "open_disputes": len(open_ids),
        "plain": (
            "CDPI composite is null until a dispute closes so we do not mint a fake 100. "
            "Open disputes freeze decay. History is never erased. "
            "This score is a soft correlation, not a receipt hash."
        ),
    }


def trust_record(
    *,
    agent: dict[str, Any] | None,
    events: list[dict[str, Any]],
    disputes: list[dict[str, Any]],
    metered: bool,
) -> dict[str, Any]:
    cdpi = score_agent(events, disputes)
    return {
        "spec": "gate-trust-record-v1",
        "pay_per_query": True,
        "metered": metered,
        "demo": not metered,
        "agent": agent,
        "cdpi": cdpi,
        "zk_linkage": zk_stub(),
        "plain": (
            "Keyed lookups increment hop usage. Unkeyed lookups are demo. "
            "This is not a sold bureau file."
        ),
    }
