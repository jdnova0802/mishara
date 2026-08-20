"""Sandbox PAS — bind-check with receipts, no API key, no PII."""
from __future__ import annotations

from typing import Any

SPEC = "gate-sandbox-pas-v1"
DEFAULT_FUSE = "fuse_velaru_drill"


def bind_check(public_url: str, *, job_id: str, fuse_id: str | None = None) -> dict[str, Any]:
    """Reuse demo bind-check path — sandbox label for runbook."""
    fid = (fuse_id or DEFAULT_FUSE).strip()
    jid = (job_id or "SANDBOX-1").strip()
    return {
        "spec": SPEC,
        "sandbox": True,
        "job_id": jid,
        "fuse_id": fid,
        "endpoint": f"{(public_url or '').rstrip('/')}/sandbox/pas/bind-check",
        "note": "POST here from runbook step 4–8hr. Same receipt family as demo/pas/bind-check.",
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Sandbox PAS",
        "endpoint": f"{base}/sandbox/pas/bind-check",
        "method": "POST",
        "body_example": {"job_id": "SANDBOX-1", "fuse_id": DEFAULT_FUSE},
        "no_api_key": True,
        "no_pii": True,
        "proof": "Response includes verify_url on HALT/BLOCK",
        "runbook": f"{base}/.well-known/runbook.json",
    }
