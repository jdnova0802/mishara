"""Intercept the one Guidewire write that already binds.

POST /job/v1/jobs/{jobId}/bind-only
https://docs.guidewire.com/cloud/is/202603/cloudapibf/cloudAPI/PolicyCenter/job-types/submissions/c_binding_a_submission_without_issuing.html

The request body is empty. A successful call changes the submission status to Bound.
Issuance is a later write. This module does not forward bind-and-issue or policy issue.

A bind-only ticket must redeem before any forward. No ticket, a failed redeem, or an
unreachable PolicyCenter host means the write did not happen. their_production stays
false: a configured upstream is not a recorded third-party weld.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import requests

try:
    from gate import spend_protocol
    from gate import ticket as ticket_mod
except ImportError:
    import spend_protocol
    import ticket as ticket_mod

SPEC = "gate-bind-only-intercept-v1"
UPSTREAM_ENV = "GATE_POLICYCENTER_BASE_URL"


def _job_id(raw: str) -> str | None:
    job_id = (raw or "").strip()
    if not job_id or len(job_id) > 80:
        return None
    if any(ch in job_id for ch in "/\\?# \t\r\n"):
        return None
    return job_id


def _upstream_base() -> str:
    return (os.getenv(UPSTREAM_ENV) or "").strip().rstrip("/")


def _halt(job_id: str, reason: str, **extra: Any) -> dict[str, Any]:
    body = {
        "spec": SPEC,
        "method": "POST",
        "path": spend_protocol.bind_only_path(job_id) if job_id else None,
        "job_id": job_id or None,
        "halt": True,
        "allow_bind": False,
        "forwarded": False,
        "bound": False,
        "their_production": False,
        "reason": reason,
        "write": "bind-only",
        "not_forwarded": ["bind-and-issue", "policy issue"],
    }
    body.update(extra)
    return body


def reject_other_write(path: str) -> tuple[dict[str, Any], int]:
    return (
        {
            "spec": SPEC,
            "halt": True,
            "allow_bind": False,
            "forwarded": False,
            "bound": False,
            "their_production": False,
            "reason": "not_this_write",
            "path": path,
            "write": "bind-only",
            "note": "bind-only is the single write this intercept gates. bind-and-issue and issue are not forwarded.",
        },
        403,
    )


def _header(headers: Any, name: str) -> str:
    if headers is None:
        return ""
    getter = getattr(headers, "get", None)
    if not callable(getter):
        return ""
    return str(getter(name) or "").strip()


def intercept(job_id_raw: str, headers: Any) -> tuple[dict[str, Any], int]:
    job_id = _job_id(job_id_raw)
    if not job_id:
        return _halt("", "job_id_rejected"), 400
    path = spend_protocol.bind_only_path(job_id)
    base = _upstream_base()
    if not base:
        return _halt(job_id, "policycenter_upstream_unset"), 409

    ticket_id = _header(headers, "X-Gate-Ticket-Id")
    token = _header(headers, "X-Gate-Ticket-Token")
    fingerprint = _header(headers, "X-Gate-Spend-Fingerprint")
    now = _header(headers, "X-Gate-Now") or datetime.now(timezone.utc).isoformat()
    if not ticket_id or not token:
        return _halt(job_id, "ticket_required"), 403

    redeemed = ticket_mod.redeem(
        ticket_id=ticket_id,
        token=token,
        job_id=job_id,
        method="POST",
        path=path,
        spend_fingerprint=fingerprint or None,
        now=now or None,
    )
    if not redeemed.get("ok") or not redeemed.get("allow_bind"):
        return _halt(
            job_id,
            str(redeemed.get("reason") or "ticket_refused"),
            ticket_consumed=False,
        ), 403

    url = base + path
    forward_headers = {"Accept": "application/json"}
    authorization = _header(headers, "Authorization")
    if authorization:
        forward_headers["Authorization"] = authorization
    try:
        timeout = float(os.getenv("GATE_POLICYCENTER_TIMEOUT") or "8")
    except ValueError:
        timeout = 8.0
    try:
        upstream = requests.post(url, data=b"", headers=forward_headers, timeout=timeout)
    except requests.Timeout:
        return _halt(job_id, "policycenter_timeout", ticket_consumed=True), 503
    except requests.RequestException:
        return _halt(job_id, "policycenter_unreachable", ticket_consumed=True), 503

    bound = 200 <= upstream.status_code < 300
    body = _halt(job_id, "upstream_status" if not bound else "forwarded")
    body["halt"] = not bound
    body["allow_bind"] = True
    body["forwarded"] = True
    body["bound"] = bound
    body["upstream_status"] = upstream.status_code
    body["ticket_consumed"] = True
    body["their_production"] = False
    return body, (200 if bound else 502)
