"""S8 RON Attest Refuse — lab mouth: video presence ≠ notarial act.

Lab only. their_production is always False.
Not a notary marketplace — this gates ATTEST / refuse with stranger receipt.
"""

from __future__ import annotations

import hashlib
import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any


SPEC = "nisaba-ron-attest-refuse-lab-v1"
THEIR_PRODUCTION = False


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


@dataclass
class Session:
    session_id: str
    signatory_id: str
    doc_hash: str
    appearance: str


@dataclass
class Store:
    sessions: dict[str, Session] = field(default_factory=dict)
    receipts: dict[str, dict[str, Any]] = field(default_factory=dict)
    attestations: dict[str, dict[str, Any]] = field(default_factory=dict)


STORE = Store()


def reset() -> None:
    STORE.sessions.clear()
    STORE.receipts.clear()
    STORE.attestations.clear()


def _receipt(
    decision: str,
    reason_code: str,
    *,
    session_id: str | None = None,
    signatory_id: str | None = None,
    doc_hash: str | None = None,
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rid = str(uuid.uuid4())
    payload = {
        "spec": SPEC,
        "receipt_id": rid,
        "decision": decision,
        "reason_code": reason_code,
        "session_id": session_id,
        "signatory_id": signatory_id,
        "doc_hash": doc_hash,
        "result": result,
        "their_production": THEIR_PRODUCTION,
        "ts": time.time(),
    }
    payload["receipt_hash"] = hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()
    STORE.receipts[rid] = payload
    return {**payload, "receipt_url": f"/v1/ron-attest/receipts/{rid}"}


def open_session(
    *,
    signatory_id: str,
    doc_hash: str,
    appearance: str,
) -> dict[str, Any]:
    if not signatory_id or not doc_hash:
        return {
            "ok": False,
            "reason_code": "malformed_session",
            "their_production": THEIR_PRODUCTION,
        }
    sid = str(uuid.uuid4())
    STORE.sessions[sid] = Session(
        session_id=sid,
        signatory_id=signatory_id,
        doc_hash=doc_hash,
        appearance=appearance,
    )
    return {
        "session_id": sid,
        "signatory_id": signatory_id,
        "doc_hash": doc_hash,
        "appearance": appearance,
        "their_production": THEIR_PRODUCTION,
    }


def attest(session_id: str, *, expected_doc_hash: str | None = None) -> dict[str, Any]:
    s = STORE.sessions.get(session_id)
    if s is None:
        return _receipt("REFUSE", "no_session", session_id=session_id)

    if s.appearance in ("", "unknown") or s.appearance is None:
        return _receipt(
            "REFUSE",
            "appearance_unknown",
            session_id=session_id,
            signatory_id=s.signatory_id,
            doc_hash=s.doc_hash,
        )
    if s.appearance == "synthetic_suspect":
        return _receipt(
            "REFUSE",
            "appearance_synthetic_suspect",
            session_id=session_id,
            signatory_id=s.signatory_id,
            doc_hash=s.doc_hash,
        )
    if s.appearance != "live":
        return _receipt(
            "REFUSE",
            "appearance_not_live",
            session_id=session_id,
            signatory_id=s.signatory_id,
            doc_hash=s.doc_hash,
        )

    if expected_doc_hash is not None and expected_doc_hash != s.doc_hash:
        return _receipt(
            "REFUSE",
            "doc_hash_mismatch",
            session_id=session_id,
            signatory_id=s.signatory_id,
            doc_hash=s.doc_hash,
        )

    aid = str(uuid.uuid4())
    stub = {
        "attestation_id": aid,
        "session_id": session_id,
        "signatory_id": s.signatory_id,
        "doc_hash": s.doc_hash,
        "notarial_stub": f"SIM-RON-{aid[:8]}",
        "their_production": THEIR_PRODUCTION,
    }
    STORE.attestations[aid] = stub
    return _receipt(
        "ALLOW",
        "attested",
        session_id=session_id,
        signatory_id=s.signatory_id,
        doc_hash=s.doc_hash,
        result=stub,
    )


def get_receipt(receipt_id: str) -> dict[str, Any] | None:
    r = STORE.receipts.get(receipt_id)
    if r is None:
        return None
    return {**r, "receipt_url": f"/v1/ron-attest/receipts/{receipt_id}"}
