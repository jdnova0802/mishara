"""S3 Performative Seal — lab mouth: draft ≠ filed speech-act.

Lab only. their_production is always False.
Not Westlaw/Lexis Quick Check — those check. This gates FILE / EFSP transmit.
Weld-shape: EFSP block-transmit — no LIVE seal ⇒ cannot transmit.
"""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from gate.sims.lab_invariant import stamp_lab_flag
from gate.sims.logos import canonical


SPEC = "nisaba-performative-seal-lab-v1"
THEIR_PRODUCTION = False


def brief_hash(citations: list[dict[str, Any]]) -> str:
    return hashlib.sha256(canonical({"citations": citations}).encode("utf-8")).hexdigest()


# Fixture grounding store — real-shaped keys vs planted fakes for proves.
GROUNDING_STORE: dict[str, dict[str, str]] = {
    "Mata v. Avianca, Inc., 678 F. Supp. 3d 443": {
        "holding": "sanctions for fabricated citations",
        "quote": "The Court therefore imposes sanctions",
    },
    "Fed. R. Civ. P. 11": {
        "holding": "attorney certifications",
        "quote": "By presenting to the court a pleading",
    },
    "28 U.S.C. § 1927": {
        "holding": "counsel liability for unreasonable multiplication",
        "quote": "Any attorney or other person admitted",
    },
}


@dataclass
class Brief:
    brief_id: str
    citations: list[dict[str, Any]]
    content_hash: str


@dataclass
class Seal:
    seal_id: str
    brief_id: str
    content_hash: str
    created_at: float


@dataclass
class Store:
    briefs: dict[str, Brief] = field(default_factory=dict)
    seals: dict[str, Seal] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    filings: dict[str, dict[str, Any]] = field(default_factory=dict)
    transmits: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.briefs.clear()
    STORE.seals.clear()
    STORE.receipts.clear()
    STORE.filings.clear()
    STORE.transmits.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    brief_id: str | None = None,
    seal_id: str | None = None,
    content_hash: str | None = None,
    failures: list[dict[str, Any]] | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "receipt_class": "clearance",  # file/transmit mouth decision
        "decision": decision,
        "reason_code": reason_code,
        "brief_id": brief_id,
        "seal_id": seal_id,
        "content_hash": content_hash,
        "failures": failures or [],
        "result": result,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="performative_seal"),
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/performative/receipts/{rid}"}


def create_brief(citations: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(citations, list) or not citations:
        return {
            "ok": False,
            "reason_code": "malformed_brief",
            "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="performative_seal"),
        }
    bid = str(uuid.uuid4())
    ch = brief_hash(citations)
    STORE.briefs[bid] = Brief(brief_id=bid, citations=list(citations), content_hash=ch)
    return {
        "brief_id": bid,
        "content_hash": ch,
        "citation_count": len(citations),
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="performative_seal"),
    }


def seal_brief(brief_id: str) -> dict[str, Any]:
    b = STORE.briefs.get(brief_id)
    if b is None:
        return _receipt("DENY", "no_brief", brief_id=brief_id)

    failures: list[dict[str, Any]] = []
    for cite in b.citations:
        key = str(cite.get("cite_key") or "").strip()
        quoted = cite.get("quoted_text")
        if not key:
            failures.append({"cite_key": key, "reason": "empty_cite"})
            continue
        grounded = GROUNDING_STORE.get(key)
        if grounded is None:
            failures.append({"cite_key": key, "reason": "ungrounded_citation"})
            continue
        if quoted is not None and str(quoted) != grounded["quote"]:
            failures.append({"cite_key": key, "reason": "hallucinated_quote"})

    if failures:
        return _receipt(
            "DENY",
            "seal_failed",
            brief_id=brief_id,
            content_hash=b.content_hash,
            failures=failures,
        )

    sid = str(uuid.uuid4())
    STORE.seals[sid] = Seal(
        seal_id=sid,
        brief_id=brief_id,
        content_hash=b.content_hash,
        created_at=time.time(),
    )
    return _receipt(
        "ALLOW",
        "sealed",
        brief_id=brief_id,
        seal_id=sid,
        content_hash=b.content_hash,
        result={"seal_id": sid, "status": "LIVE_SEAL"},
    )


def _require_live_seal(
    brief_id: str,
    seal_id: str | None,
    *,
    no_seal_reason: str,
) -> tuple[Brief | None, Seal | None, dict[str, Any] | None]:
    """Shared LIVE-seal gate for file and EFSP transmit. Third value = DENY receipt."""
    b = STORE.briefs.get(brief_id)
    if b is None:
        return None, None, _receipt("DENY", "no_brief", brief_id=brief_id)

    if not seal_id:
        return b, None, _receipt(
            "DENY",
            no_seal_reason,
            brief_id=brief_id,
            content_hash=b.content_hash,
            result={"efsp_block": no_seal_reason == "efsp_block_no_seal"},
        )

    s = STORE.seals.get(seal_id)
    if s is None:
        return b, None, _receipt(
            "DENY",
            no_seal_reason,
            brief_id=brief_id,
            seal_id=seal_id,
            content_hash=b.content_hash,
            result={"efsp_block": no_seal_reason == "efsp_block_no_seal"},
        )
    if s.brief_id != brief_id:
        return b, None, _receipt(
            "DENY",
            "seal_brief_mismatch",
            brief_id=brief_id,
            seal_id=seal_id,
            content_hash=b.content_hash,
        )
    if s.content_hash != b.content_hash:
        return b, None, _receipt(
            "DENY",
            "seal_stale",
            brief_id=brief_id,
            seal_id=seal_id,
            content_hash=b.content_hash,
        )
    return b, s, None


def file_brief(brief_id: str, seal_id: str | None = None) -> dict[str, Any]:
    b, s, denied = _require_live_seal(brief_id, seal_id, no_seal_reason="no_seal")
    if denied is not None:
        return denied
    assert b is not None and s is not None

    fid = str(uuid.uuid4())
    filing = {
        "filing_id": fid,
        "brief_id": brief_id,
        "seal_id": seal_id,
        "content_hash": b.content_hash,
        "docket_sim": f"SIM-DOCKET-{fid[:8]}",
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="performative_seal"),
    }
    STORE.filings[fid] = filing
    return _receipt(
        "ALLOW",
        "filed",
        brief_id=brief_id,
        seal_id=seal_id,
        content_hash=b.content_hash,
        result=filing,
    )


def transmit_efsp(
    brief_id: str,
    seal_id: str | None = None,
    *,
    court_id: str = "US-SDNY",
    case_number: str = "1:26-cv-0001",
) -> dict[str, Any]:
    """EFSP-shaped block-transmit mouth.

    No LIVE seal ⇒ cannot transmit. Lab fixture only — no real CM/ECF.
    """
    b, s, denied = _require_live_seal(brief_id, seal_id, no_seal_reason="efsp_block_no_seal")
    if denied is not None:
        return denied
    assert b is not None and s is not None

    tid = str(uuid.uuid4())
    transmit = {
        "transmit_id": tid,
        "brief_id": brief_id,
        "seal_id": seal_id,
        "content_hash": b.content_hash,
        "court_id": court_id,
        "case_number": case_number,
        "efsp": "lab_fixture",
        "real_cm_ecf": False,
        "their_production": stamp_lab_flag(THEIR_PRODUCTION, module="performative_seal"),
    }
    STORE.transmits[tid] = transmit
    return _receipt(
        "ALLOW",
        "efsp_transmitted",
        brief_id=brief_id,
        seal_id=seal_id,
        content_hash=b.content_hash,
        result=transmit,
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/performative/receipts/{receipt_id}"}
