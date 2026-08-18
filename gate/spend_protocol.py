"""Spend protocol — the scanner.

A LIVE hop is not a print. The print is a ticket bound to one write:

  POST /job/v1/jobs/{job_id}/bind-only

Fingerprint is SHA-256 over canonical JSON of method + path + job_id + spend_kind.
Redeem must present that same write. A ticket for bind-only cannot authorize
bind-and-issue. Missing write → fail closed.

This is the object others implement (Cloudflare, Gosu is a different door).
Not a church. The only scanner that can print a YES on this spend.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

SPEC = "gate-spend-protocol-v1"
SPEND_KIND = "bind"
METHOD = "POST"
PATH_TEMPLATE = "/job/v1/jobs/{job_id}/bind-only"
MGA_PATH = "/v1/pas/mga-authority"
REASON_NOT_IN_PROTOCOL = "spend_write_not_in_protocol"
REASON_REQUIRED = "spend_write_required"
REASON_MISMATCH = "ticket_spend_mismatch"


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def normalize_job_id(job_id: str | None) -> str:
    return (job_id or "").strip()


def bind_only_path(job_id: str) -> str:
    jid = normalize_job_id(job_id) or "JOB_ID"
    return PATH_TEMPLATE.format(job_id=jid)


def normalize_path(path: str | None) -> str:
    p = (path or "").strip()
    if len(p) > 1 and p.endswith("/"):
        p = p[:-1]
    return p


def write(
    *,
    job_id: str,
    method: str | None = None,
    path: str | None = None,
    spend_kind: str | None = None,
) -> dict:
    jid = normalize_job_id(job_id)
    return {
        "method": (method or METHOD).strip().upper(),
        "path": normalize_path(path) or bind_only_path(jid),
        "job_id": jid,
        "spend_kind": (spend_kind or SPEND_KIND).strip(),
    }


def fingerprint(write_obj: dict | None) -> str | None:
    if not isinstance(write_obj, dict):
        return None
    body = {
        "job_id": write_obj.get("job_id") or "",
        "method": write_obj.get("method") or "",
        "path": write_obj.get("path") or "",
        "spend_kind": write_obj.get("spend_kind") or "",
    }
    if not body["job_id"] or not body["method"] or not body["path"] or not body["spend_kind"]:
        return None
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


def is_bind_only_path(path: str | None, job_id: str) -> bool:
    return normalize_path(path) == normalize_path(bind_only_path(job_id))


def _action_token(action: str | None) -> str:
    return (action or "").strip().lower().replace("_", "-")


def intended_policycenter(
    *,
    job_id: str | None,
    action: str | None = None,
    method: str | None = None,
    path: str | None = None,
    bind_path: str | None = None,
) -> dict | None:
    """Married PolicyCenter write, or None if they asked for a door this scanner does not print."""
    jid = normalize_job_id(job_id)
    if not jid:
        return None
    meth = (method or METHOD).strip().upper()
    if meth != METHOD:
        return None
    p = normalize_path(path or bind_path)
    act = _action_token(action)
    married = write(job_id=jid)
    if p:
        return married if is_bind_only_path(p, jid) else None
    if act:
        if act in {"bind-only", "bind"}:
            return married
        return None
    return married


def intended_mga(*, job_id: str | None) -> dict | None:
    jid = normalize_job_id(job_id)
    if not jid:
        return None
    return write(job_id=jid, path=MGA_PATH, spend_kind=SPEND_KIND)


def intended_duckcreek(*, job_id: str | None) -> dict | None:
    jid = normalize_job_id(job_id)
    if not jid:
        return None
    return write(job_id=jid, path=f"/api/issue/{jid}", spend_kind=SPEND_KIND)


def presented_write(
    *,
    job_id: str | None,
    method: str | None,
    path: str | None,
    spend_kind: str | None = None,
) -> dict | None:
    jid = normalize_job_id(job_id)
    meth = (method or "").strip().upper()
    p = normalize_path(path)
    if not jid or not meth or not p:
        return None
    return write(job_id=jid, method=meth, path=p, spend_kind=spend_kind)


def fingerprints_match(issued: str | None, presented: str | None) -> bool:
    a = (issued or "").strip().lower()
    b = (presented or "").strip().lower()
    return bool(a) and a == b


def spec(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Spend protocol",
        "what": "The only scanner that can print a YES on this irreversible spend.",
        "not": [
            "a hop receipt",
            "a second source for the same YES",
            "authorization for bind-and-issue or issue",
        ],
        "married_write": {
            "method": METHOD,
            "path": PATH_TEMPLATE,
            "spend_kind": SPEND_KIND,
        },
        "fingerprint": {
            "alg": "sha256",
            "over": ["method", "path", "job_id", "spend_kind"],
            "canonical_json": "sort_keys, separators=(',', ':')",
        },
        "ticket": {
            "binds_to": "spend_fingerprint",
            "single_use": True,
            "stale_hop_cannot_spend": True,
        },
        "redeem": {
            "path": f"{base}/v1/pas/bind-ticket/redeem",
            "required": ["ticket_id", "token", "job_id", "method", "path", "now"],
            "optional": ["spend_fingerprint"],
            "now": "UTC. Missing or skewed now is radiation_abort; the ticket is not consumed.",
            "mismatch": REASON_MISMATCH,
            "missing_write": REASON_REQUIRED,
            "not_in_protocol": REASON_NOT_IN_PROTOCOL,
            "fail_closed": True,
            "recompute": "Hash the write being forwarded, not the fingerprint copied off the ticket.",
        },
        "command_radiation": f"{base}/.well-known/command-radiation.json",
        "refused_writes": [
            "POST /job/v1/jobs/{job_id}/bind-and-issue",
            "POST /policy/v1/policies/{policy_id}/issue",
        ],
        "implementor": f"{base}/listings/cloudflare-worker-bind.js",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
        "their_production": False,
        "page": f"{base}/scanner",
    }
