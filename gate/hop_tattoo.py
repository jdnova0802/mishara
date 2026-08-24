"""Hop Tattoo — every pre-bind hop burns a stranger verify_url into the job.

Invention (NORTH_STAR foothill): examiner opens the no without trusting the
carrier. Each job_id carries a permanent stranger verify_url tattoo from the
first Gate hop — officer appendix material, not operator narrative.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

try:
    from gate import db
except ImportError:
    import db

SPEC = "gate-hop-tattoo-v1"
INVENTION = "Hop Tattoo"
FAMILY = "foothill"
DEFAULT_VERIFY = "https://velaru.xyz/verify"


def _canonical(*, job_id: str, verify_url: str, fuse_id: str, event_id: str) -> str:
    body = {
        "job_id": job_id,
        "verify_url": verify_url,
        "fuse_id": fuse_id,
        "event_id": event_id,
    }
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def resolve_verify_url(*, hop: dict | None = None, plan: dict | None = None) -> str:
    hop_d = hop if isinstance(hop, dict) else {}
    plan_d = plan if isinstance(plan, dict) else {}
    for src in (hop_d, plan_d):
        url = (src.get("verify_url") or src.get("restraint_permalink") or "").strip()
        if url:
            return url
    nested = plan_d.get("hop") if isinstance(plan_d.get("hop"), dict) else {}
    url = (nested.get("verify_url") or nested.get("restraint_permalink") or "").strip()
    return url or DEFAULT_VERIFY


def burn(
    *,
    job_id: str | None,
    verify_url: str | None = None,
    event_id: str | None = None,
    fuse_id: str | None = None,
    decision: str | None = None,
    hop: dict | None = None,
    plan: dict | None = None,
) -> dict[str, Any]:
    """Mint a hop tattoo — stranger verify_url burned into job_id."""
    jid = (job_id or "").strip() or None
    url = (verify_url or "").strip() or resolve_verify_url(hop=hop, plan=plan)
    eid = (event_id or "").strip() or None
    fid = (fuse_id or "").strip() or None
    digest = None
    if jid and url and eid:
        digest = hashlib.sha256(_canonical(job_id=jid, verify_url=url, fuse_id=fid or "", event_id=eid).encode()).hexdigest()
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "job_id": jid,
        "verify_url": url,
        "event_id": eid,
        "fuse_id": fid,
        "decision": decision,
        "tattoo_hash": digest,
        "burned": bool(jid and url),
        "stranger": True,
        "rule": "Every pre-bind hop burns verify_url into the job. Examiner opens the no without trusting the carrier.",
        "not": ["operator dashboard link", "PII", "club-only narrative"],
    }


def lookup(job_id: str | None) -> dict[str, Any]:
    """Return latest tattoo for job_id from bind events."""
    jid = (job_id or "").strip() or None
    if not jid:
        return {"spec": SPEC, "found": False, "reason": "job_id_required"}
    row = db.latest_bind_event_for_job(jid)
    if not row:
        return {"spec": SPEC, "found": False, "job_id": jid, "reason": "no_hop_yet"}
    url = (row.get("verify_url") or DEFAULT_VERIFY).strip()
    tattoo = burn(
        job_id=jid,
        verify_url=url,
        event_id=row.get("id"),
        fuse_id=row.get("fuse_id"),
        decision=row.get("decision"),
    )
    tattoo["found"] = True
    tattoo["created_at"] = row.get("created_at")
    tattoo["acted"] = row.get("acted")
    return tattoo


def attach(
    plan: dict,
    *,
    job_id: str | None = None,
    verify_url: str | None = None,
    event_id: str | None = None,
    fuse_id: str | None = None,
    hop: dict | None = None,
) -> dict:
    """Burn tattoo onto plan; ensure halt responses always carry verify_url."""
    url = (verify_url or "").strip() or resolve_verify_url(hop=hop, plan=plan)
    plan["verify_url"] = url
    if isinstance(hop, dict):
        hop.setdefault("verify_url", url)
        plan["hop"] = hop
    tattoo = burn(
        job_id=job_id or plan.get("job_id"),
        verify_url=url,
        event_id=event_id or plan.get("event_id"),
        fuse_id=fuse_id or plan.get("fuse_id"),
        decision=plan.get("decision"),
        hop=hop,
        plan=plan,
    )
    plan["hop_tattoo"] = tattoo
    return plan


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "invention": INVENTION,
        "family": FAMILY,
        "one_liner": "Every pre-bind hop burns a stranger verify_url into the job.",
        "lookup": f"GET {base}/demo/pas/hop-tattoo/{{job_id}}",
        "demo": f"POST {base}/demo/pas/hop-tattoo",
        "well_known": f"{base}/.well-known/hop-tattoo.json",
        "appendix": f"{base}/v1/pas/bind-appendix",
        "pairs_with": "Receipt Stone foothill — verify_url is the stranger anchor",
        "bind_room": f"{base}/bind-room",
        "north_star": "gate/NORTH_STAR.md#inventions-forge-catalog",
        "posture": "Under coordinators. Officer appendix invention.",
    }
