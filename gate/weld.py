"""First foreign hop — PolicyCenter bind-and-issue wrap + MGA authority.

Guidewire has no pre-bind hook. Sequence:
  hop/act → if halt/DEAD raise Manual UW issue (blocks bind) → do NOT call bind-and-issue
  LIVE + verdict true → POST /job/v1/jobs/{jobId}/bind-and-issue
UW approve without CHARGE does not resurrect the fuse.
"""
from __future__ import annotations


PC_BIND = "/job/v1/jobs/{job_id}/bind-and-issue"
PC_UW = "/job/v1/jobs/{job_id}/uw-issues"
DEFAULT_ISSUE_TYPE = "UWManagerReviewBlocksQuoteRelease"


def hop_allows_bind(hop: dict | None, status: int) -> bool:
    if status >= 500:
        return False
    if not isinstance(hop, dict):
        return False
    if hop.get("halt") or hop.get("fail_closed"):
        return False
    if hop.get("acted") is False:
        return False
    return hop.get("verdict") is True


def policycenter_plan(job_id: str, hop: dict | None, status: int, issue_type: str | None = None) -> dict:
    jid = (job_id or "").strip() or "JOB_ID"
    issue = (issue_type or DEFAULT_ISSUE_TYPE).strip()
    bind_path = PC_BIND.format(job_id=jid)
    if hop_allows_bind(hop, status):
        return {
            "spec": "gate-policycenter-weld-v1",
            "allow_bind": True,
            "halt": False,
            "job_id": jid,
            "next": {"method": "POST", "path": bind_path, "body": None},
            "do_not_call": None,
            "raise_uw_issue": None,
            "charge": "LIVE hop only. CHARGE webhook is the only DEAD→LIVE path.",
            "hop": hop,
        }
    return {
        "spec": "gate-policycenter-weld-v1",
        "allow_bind": False,
        "halt": True,
        "job_id": jid,
        "next": None,
        "do_not_call": {"method": "POST", "path": bind_path},
        "raise_uw_issue": {
            "method": "POST",
            "path": PC_UW.format(job_id=jid),
            "body": {"data": {"attributes": {"issueType": {"code": issue}}}},
            "note": "Manual checking-set only. Approve without CHARGE does not resurrect.",
        },
        "charge": "Approving the UW issue is not DEAD→LIVE. CHARGE webhook only.",
        "hop": hop,
    }


def duckcreek_plan(job_id: str, hop: dict | None, status: int) -> dict:
    """Same fail-closed shape. Their issue API name varies; do not call issue if halt."""
    jid = (job_id or "").strip() or "JOB_ID"
    allowed = hop_allows_bind(hop, status)
    return {
        "spec": "gate-duckcreek-weld-v1",
        "allow_bind": allowed,
        "halt": not allowed,
        "job_id": jid,
        "next": {"method": "POST", "path": f"/api/issue/{jid}"} if allowed else None,
        "do_not_call": None if allowed else {"method": "POST", "path": f"/api/issue/{jid}"},
        "note": "Mirror of PolicyCenter. Paymentus is pay ≠ allowed — not this weld.",
        "charge": "CHARGE webhook is the only DEAD→LIVE path.",
        "hop": hop,
    }


def mga_authority(
    hop: dict | None,
    status: int,
    *,
    premium: float | None,
    authority_limit: float | None,
    line: str | None,
    state: str | None,
    allowed_lines: list | None,
    allowed_states: list | None,
) -> dict:
    reasons = []
    if not hop_allows_bind(hop, status):
        reasons.append("fuse_dead_or_halt")
    if premium is not None and authority_limit is not None and premium > authority_limit:
        reasons.append("premium_exceeds_authority")
    if allowed_lines:
        allowed = {str(x).lower() for x in allowed_lines}
        if line and str(line).lower() not in allowed:
            reasons.append("line_not_in_authority")
    if allowed_states:
        allowed = {str(x).upper() for x in allowed_states}
        if state and str(state).upper() not in allowed:
            reasons.append("state_not_in_authority")
    allowed = len(reasons) == 0
    return {
        "spec": "gate-mga-authority-v1",
        "bind_allowed": allowed,
        "result": "ALLOW" if allowed else "BLOCK",
        "reasons": reasons,
        "halt": not allowed,
        "charge": "CHARGE webhook is the only DEAD→LIVE path. Authority approve is not CHARGE.",
        "hop": hop,
        "checks": {
            "premium": premium,
            "authority_limit": authority_limit,
            "line": line,
            "state": state,
        },
    }


TWO_YESES = [
    "1. Bind-path owner with a live job API this quarter (MGA pen or PolicyCenter bind-and-issue)",
    "2. Else CUO / named Colorado 10-1-1 owner or NAIC 12-state pilot domestic",
    "3. Else GC Exhibit / Bind Room pack (cash, not a weld)",
    "4. MCP / listings never win a slot",
]

REFUSE = [
    "inventory / bias-audit SaaS",
    "appetite extraction",
    "free workshops",
    "PII / ACORD / ECDIS on Gate PAS paths",
    "L12 / admin CHARGE / Google-Palantir partnerships",
    "price $0",
    "filing Gate as a rating/UW model on the NAIC third-party docket",
]
