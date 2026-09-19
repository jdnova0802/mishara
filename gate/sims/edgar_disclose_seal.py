"""S7 EDGAR Disclose Seal — lab mouth: draft ≠ filed disclosure.

Lab only. their_production is always False.
Not Workiva / XBRL tag checkers — this gates SUBMIT.
"""

from __future__ import annotations

import hashlib
import json
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag
from gate.sims.logos import canonical


SPEC = "nisaba-edgar-disclose-seal-lab-v1"
THEIR_PRODUCTION = False

# Fixture financial facts — real-shaped keys vs planted hallucinations for proves.
FACT_STORE: dict[str, dict[str, Any]] = {
    "FY2025_REVENUE_USD": {"value": 1_250_000_000, "unit": "USD"},
    "FY2025_NET_INCOME_USD": {"value": 180_000_000, "unit": "USD"},
    "Q1_2026_CASH_USD": {"value": 420_000_000, "unit": "USD"},
}


def filing_hash(form: str, claims: list[dict[str, Any]]) -> str:
    return hashlib.sha256(canonical({"form": form, "claims": claims}).encode("utf-8")).hexdigest()


_NUMBER = re.compile(r"[\d,]+(?:\.\d+)?")


@dataclass
class Filing:
    filing_id: str
    form: str
    claims: list[dict[str, Any]]
    content_hash: str


@dataclass
class Seal:
    seal_id: str
    filing_id: str
    content_hash: str
    created_at: float


@dataclass
class Store:
    filings: dict[str, Filing] = field(default_factory=dict)
    seals: dict[str, Seal] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    submissions: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.filings.clear()
    STORE.seals.clear()
    STORE.receipts.clear()
    STORE.submissions.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    filing_id: str | None = None,
    seal_id: str | None = None,
    content_hash: str | None = None,
    failures: list[dict[str, Any]] | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",
        "decision": decision,
        "reason_code": reason_code,
        "filing_id": filing_id,
        "seal_id": seal_id,
        "content_hash": content_hash,
        "failures": failures or [],
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="edgar_disclose_seal"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/edgar-disclose/receipts/{rid}"}


def create_filing(form: str, claims: list[dict[str, Any]]) -> dict[str, Any]:
    if form not in ("10-K", "8-K", "10-Q"):
        return {
            "ok": False,
            "reason_code": "unsupported_form",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="edgar_disclose_seal"),
        }
    if not isinstance(claims, list) or not claims:
        return {
            "ok": False,
            "reason_code": "malformed_filing",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="edgar_disclose_seal"),
        }
    fid = str(uuid.uuid4())
    ch = filing_hash(form, claims)
    STORE.filings[fid] = Filing(filing_id=fid, form=form, claims=list(claims), content_hash=ch)
    return {
        "filing_id": fid,
        "content_hash": ch,
        "claim_count": len(claims),
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="edgar_disclose_seal"),
    }


def _claim_needs_ground(claim: dict[str, Any]) -> bool:
    if claim.get("fact_ref"):
        return True
    text = str(claim.get("text") or "")
    return bool(_NUMBER.search(text))


def seal_filing(filing_id: str) -> dict[str, Any]:
    f = STORE.filings.get(filing_id)
    if f is None:
        return _receipt("DENY", "no_filing", filing_id=filing_id)

    failures: list[dict[str, Any]] = []
    for claim in f.claims:
        cid = str(claim.get("claim_id") or "").strip()
        if not cid:
            failures.append({"claim_id": cid, "reason": "empty_claim_id"})
            continue
        if not _claim_needs_ground(claim):
            continue
        ref = claim.get("fact_ref")
        if not ref:
            failures.append({"claim_id": cid, "reason": "ungrounded_claim"})
            continue
        fact = FACT_STORE.get(str(ref))
        if fact is None:
            failures.append({"claim_id": cid, "reason": "unknown_fact_ref"})
            continue
        asserted = claim.get("asserted_value")
        if asserted is None:
            failures.append({"claim_id": cid, "reason": "missing_asserted_value"})
            continue
        try:
            asserted_n = float(asserted)
        except (TypeError, ValueError):
            failures.append({"claim_id": cid, "reason": "malformed_asserted_value"})
            continue
        if asserted_n != float(fact["value"]):
            failures.append({"claim_id": cid, "reason": "hallucinated_quantity"})

    if failures:
        return _receipt(
            "DENY",
            "seal_failed",
            filing_id=filing_id,
            content_hash=f.content_hash,
            failures=failures,
        )

    sid = str(uuid.uuid4())
    STORE.seals[sid] = Seal(
        seal_id=sid,
        filing_id=filing_id,
        content_hash=f.content_hash,
        created_at=time.time(),
    )
    return _receipt(
        "ALLOW",
        "sealed",
        filing_id=filing_id,
        seal_id=sid,
        content_hash=f.content_hash,
        result={"seal_id": sid, "status": "LIVE_SEAL"},
    )


def _require_live_seal(
    filing_id: str,
    seal_id: str | None,
    *,
    no_seal_reason: str,
) -> tuple[Filing | None, Seal | None, dict[str, Any] | None]:
    f = STORE.filings.get(filing_id)
    if f is None:
        return None, None, _receipt("DENY", "no_filing", filing_id=filing_id)

    if not seal_id:
        return f, None, _receipt(
            "DENY",
            no_seal_reason,
            filing_id=filing_id,
            content_hash=f.content_hash,
            result={"edgar_block": no_seal_reason == "edgar_block_no_seal"},
        )

    s = STORE.seals.get(seal_id)
    if s is None:
        return f, None, _receipt(
            "DENY",
            no_seal_reason,
            filing_id=filing_id,
            seal_id=seal_id,
            content_hash=f.content_hash,
            result={"edgar_block": no_seal_reason == "edgar_block_no_seal"},
        )
    if s.filing_id != filing_id:
        return f, None, _receipt(
            "DENY",
            "seal_filing_mismatch",
            filing_id=filing_id,
            seal_id=seal_id,
            content_hash=f.content_hash,
        )
    if s.content_hash != f.content_hash:
        return f, None, _receipt(
            "DENY",
            "seal_stale",
            filing_id=filing_id,
            seal_id=seal_id,
            content_hash=f.content_hash,
        )
    return f, s, None


def submit_filing(filing_id: str, seal_id: str | None = None) -> dict[str, Any]:
    f, s, denied = _require_live_seal(filing_id, seal_id, no_seal_reason="no_seal")
    if denied is not None:
        return denied
    assert f is not None and s is not None

    sid = str(uuid.uuid4())
    submission = {
        "submission_id": sid,
        "filing_id": filing_id,
        "seal_id": seal_id,
        "form": f.form,
        "content_hash": f.content_hash,
        "edgar_sim": f"SIM-EDGAR-{sid[:8]}",
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="edgar_disclose_seal"),
    }
    STORE.submissions[sid] = submission
    return _receipt(
        "ALLOW",
        "submitted",
        filing_id=filing_id,
        seal_id=seal_id,
        content_hash=f.content_hash,
        result=submission,
    )


def submit_edgar_gateway(filing_id: str, seal_id: str | None = None) -> dict[str, Any]:
    """EDGAR gateway weld-shape — no LIVE seal ⇒ cannot submit (lab fixture)."""
    f, s, denied = _require_live_seal(
        filing_id, seal_id, no_seal_reason="edgar_block_no_seal"
    )
    if denied is not None:
        return denied
    assert f is not None and s is not None

    sid = str(uuid.uuid4())
    submission = {
        "submission_id": sid,
        "filing_id": filing_id,
        "seal_id": seal_id,
        "form": f.form,
        "content_hash": f.content_hash,
        "edgar_gateway": "lab_fixture",
        "real_edgar": False,
        "edgar_sim": f"SIM-EDGAR-GW-{sid[:8]}",
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="edgar_disclose_seal"),
    }
    STORE.submissions[sid] = submission
    return _receipt(
        "ALLOW",
        "edgar_submitted",
        filing_id=filing_id,
        seal_id=seal_id,
        content_hash=f.content_hash,
        result=submission,
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/edgar-disclose/receipts/{receipt_id}"}
