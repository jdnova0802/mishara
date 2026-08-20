"""FMI P17 Receipt — operational risk proof at decision time, not quarterly attestation.

PFMI Principle 17: identify and mitigate operational risk. FMIs publish
resilience; participants hide failures in email. Gate publishes HALT/BLOCK
inventory and fetchable receipts at the decision — KRI before settlement fail,
not after. DTCC peers care because your exception becomes their KRI.

Not cliche SOC2 badge. Decision-time operational evidence.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

SPEC = "gate-fmi-p17-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def evidence(
    *,
    decision: str | None = None,
    receipt_hash: str | None = None,
    verify_url: str | None = None,
    quarterly_pdf_only: bool | None = None,
) -> dict[str, Any]:
    d = (decision or "").upper()
    rh = bool((receipt_hash or "").strip())
    url = bool((verify_url or "").strip())
    pdf = bool(quarterly_pdf_only)
    if pdf and not (rh and url):
        posture = "attestation_without_ops_evidence"
        claim = "p17_violation_pdf_is_not_decision_proof"
    elif rh and url and d:
        posture = "p17_satisfied"
        claim = "operational_risk_visible_at_decision"
    else:
        posture = "insufficient"
        claim = "no_fetchable_decision_artifact"
    return {
        "spec": SPEC,
        "name": "FMI P17 Receipt",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "PFMI Principle 17 — operational risk identification and mitigation",
            "Gate restraint inventory + receipt antenna",
        ],
        "decision": d or None,
        "receipt_hash_present": rh,
        "verify_present": url,
        "quarterly_pdf_only": pdf,
        "posture": posture,
        "claim": claim,
        "thesis": "Your FMI cannot see your ops risk at quarter-end. We publish it at the hop.",
        "gatekeep": "Proprietary FMI-P17 receipt doctrine. Ours.",
        "their_production": False,
    }


def attach_to_receipt_payload(payload: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out["fmi_p17"] = evidence(
        decision=row.get("decision"),
        receipt_hash=row.get("receipt_hash"),
        verify_url=row.get("verify_url"),
        quarterly_pdf_only=False,
    )
    return out


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "FMI P17 Receipt",
        "inventor": INVENTOR,
        "example_ok": evidence(decision="HALT", receipt_hash="abc", verify_url="https://x"),
        "example_bad": evidence(quarterly_pdf_only=True),
        "live": f"{base}/.well-known/fmi-p17.json",
        "restraint": f"{base}/.well-known/restraint.json",
        "their_production": False,
    }
