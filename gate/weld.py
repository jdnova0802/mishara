"""PolicyCenter production capture — every Cloud API spend write.

Guidewire has no pre-bind hook. Binding is the spent world (legally bound contract).
Issuance is documents. Wrapping only bind-and-issue leaks:

  POST /job/v1/jobs/{jobId}/bind-only
  → status Bound. The contract already exists.

UW issue type UWManagerReviewBlocksQuoteRelease blocks quoting, not bind.
The issue type in their admin data must have blocking point Binding (blocksBind).

Remaining Cloud API-invisible doors: PolicyCenter UI bind, renewal auto-bind workflow.
Those get paste artifacts (Gosu checking set + RenewalWF step). Worker still wraps bind-only.
"""
from __future__ import annotations

PC_BIND_AND_ISSUE = "/job/v1/jobs/{job_id}/bind-and-issue"
PC_BIND_ONLY = "/job/v1/jobs/{job_id}/bind-only"
PC_POLICY_ISSUE = "/policy/v1/policies/{policy_id}/issue"
PC_UW = "/job/v1/jobs/{job_id}/uw-issues"
# Base-config type. Blocks QUOTE RELEASE — not sufficient to stop bind.
DEFAULT_ISSUE_TYPE = "UWManagerReviewBlocksQuoteRelease"
BINDING_POINT = "Binding"
DEFAULT_VERIFY = "https://velaru.xyz/verify"
GOSU_PREBIND = "guidewire-gosu-prebind.gs"
GOSU_RENEWAL = "guidewire-renewal-prebind.gs"


def spend_writes(job_id: str, policy_id: str | None = None) -> list[dict]:
    jid = (job_id or "").strip() or "JOB_ID"
    pid = (policy_id or "").strip() or "POLICY_ID"
    return [
        {
            "method": "POST",
            "path": PC_BIND_ONLY.format(job_id=jid),
            "spend": "bind",
            "note": "Legally Bound with no documents. This is already a spent world.",
        },
        {
            "method": "POST",
            "path": PC_BIND_AND_ISSUE.format(job_id=jid),
            "spend": "bind_and_issue",
            "note": "Bind + issue in one call. Typical portal/automation write.",
        },
        {
            "method": "POST",
            "path": PC_POLICY_ISSUE.format(policy_id=pid),
            "spend": "issue_after_bind_only",
            "note": "Issues a policy that was already Bound via bind-only.",
        },
    ]


def verify_url(hop: dict | None) -> str:
    if isinstance(hop, dict):
        url = hop.get("verify_url") or hop.get("restraint_permalink")
        if url:
            return str(url)
    return DEFAULT_VERIFY


def listing_url(public_url: str | None, name: str) -> str:
    base = (public_url or "").rstrip("/")
    return f"{base}/listings/{name}" if base else f"/listings/{name}"


def other_doors(public_url: str | None = None) -> list[dict]:
    return [
        {
            "door": "PolicyCenter UI Bind",
            "why": "Console Bind never hits Cloud API. The worker cannot see it.",
            "close": "Paste guidewire-gosu-prebind.gs into the Bind checking set and Bind PCF button before JobProcess.bind().",
            "file": listing_url(public_url, GOSU_PREBIND),
        },
        {
            "door": "Renewal workflow auto-bind",
            "why": "Some renewals bind at midnight with no API call and no UI click.",
            "close": "Paste guidewire-renewal-prebind.gs as a RenewalWF step before Bind. continue-on-error off.",
            "file": listing_url(public_url, GOSU_RENEWAL),
        },
    ]


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


def policycenter_plan(
    job_id: str, hop: dict | None, status: int, issue_type: str | None = None, policy_id: str | None = None
) -> dict:
    jid = (job_id or "").strip() or "JOB_ID"
    issue = (issue_type or DEFAULT_ISSUE_TYPE).strip()
    writes = spend_writes(jid, policy_id)
    bind_only = writes[0]["path"]
    bind_and_issue = writes[1]["path"]
    receipt = verify_url(hop)
    if hop_allows_bind(hop, status):
        return {
            "spec": "gate-policycenter-weld-v1",
            "allow_bind": True,
            "halt": False,
            "job_id": jid,
            "verify_url": receipt,
            "next": {"method": "POST", "path": bind_only, "body": None},
            "spend_write": {"method": "POST", "path": bind_only, "spend_kind": "bind"},
            "also_allowed": writes,
            "not_granted": [bind_and_issue, writes[2]["path"]],
            "do_not_call": None,
            "do_not_call_all": None,
            "raise_uw_issue": None,
            "charge": "LIVE hop only. CHARGE webhook is the only DEAD→LIVE path. Ticket prints bind-only.",
            "hop": hop,
        }
    return {
        "spec": "gate-policycenter-weld-v1",
        "allow_bind": False,
        "halt": True,
        "job_id": jid,
        "verify_url": receipt,
        "next": None,
        "do_not_call": {"method": "POST", "path": bind_only},
        "do_not_call_all": writes,
        "leak": "If you only wrap bind-and-issue, bind-only already Bound the policy.",
        "raise_uw_issue": {
            "method": "POST",
            "path": PC_UW.format(job_id=jid),
            "body": {"data": {"attributes": {"issueType": {"code": issue}}}},
            "blocking_point_required": BINDING_POINT,
            "note": (
                "Issue type in PolicyCenter admin must block Binding (blocksBind), not only Quote. "
                f"{DEFAULT_ISSUE_TYPE} blocks quote release — insufficient. "
                "Approve without CHARGE does not resurrect."
            ),
        },
        "other_doors": other_doors(),
        "charge": "Approving the UW issue is not DEAD→LIVE. CHARGE webhook only.",
        "hop": hop,
    }


def duckcreek_plan(job_id: str, hop: dict | None, status: int) -> dict:
    jid = (job_id or "").strip() or "JOB_ID"
    allowed = hop_allows_bind(hop, status)
    return {
        "spec": "gate-duckcreek-weld-v1",
        "allow_bind": allowed,
        "halt": not allowed,
        "job_id": jid,
        "verify_url": verify_url(hop),
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
        "verify_url": verify_url(hop),
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
    "1. Bind-path owner with a live job API this quarter (MGA pen or PolicyCenter bind-and-issue AND bind-only)",
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


def capture_manifest(public_url: str) -> dict:
    writes = spend_writes("JOB_ID", "POLICY_ID")
    return {
        "spec": "gate-policycenter-capture-v1",
        "source": [
            "https://docs.guidewire.com/cloud/is/202603/cloudapibf/cloudAPI/PolicyCenter/job-types/submissions/c_binding_and_issuing_a_submission_at_the_same_time.html",
            "https://docs.guidewire.com/cloud/is/202603/cloudapibf/cloudAPI/PolicyCenter/job-types/submissions/c_binding_a_submission_without_issuing.html",
            "https://docs.guidewire.com/cloud/is/202603/cloudapibf/cloudAPI/PolicyCenter/job-support/underwriting-issues/c_underwriting_issues_in_policycenter.html",
        ],
        "spent_world": "POST bind-only sets job status Bound. That is a legally binding contract without documents.",
        "cloud_api_spend_writes": writes,
        "uw_issue": {
            "create": "POST /job/v1/jobs/{jobId}/uw-issues",
            "blocking_point_required": BINDING_POINT,
            "not_sufficient": DEFAULT_ISSUE_TYPE,
            "not_sufficient_why": "Blocks quote release. Bind-only and bind-and-issue can still fire.",
            "open_issue_with_blocksBind": "Cloud API bind returns 422 rule-violation until approved. Approve is not CHARGE.",
        },
        "other_doors": other_doors(public_url),
        "in_house_paste": {
            "ui_bind": listing_url(public_url, GOSU_PREBIND),
            "renewal_auto_bind": listing_url(public_url, GOSU_RENEWAL),
        },
        "worker": f"{public_url}/listings/cloudflare-worker-bind.js",
        "pre_bind": f"POST {public_url}/v1/pas/policycenter/pre-bind",
        "halt_always_includes": ["verify_url", "inhabitant_url"],
        "their_production": False,
        "later": {
            "tpm_hsm": "After first invoice. Do not stall the weld for a root of trust nobody asked for yet.",
            "claims_pay": "Second spend. Marry bind first.",
            "org_tree": "Parent DEAD kills child is a Velaru engine fact. Gate will not fake an org tree.",
        },
        "page": f"{public_url}/capture",
    }
