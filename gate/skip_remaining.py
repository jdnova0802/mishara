"""Skip remaining — D1 as an implementable type.

Ranked writes have offer / accept / execute. Skip is not a type in their
diaries. This module is the CUDA/yellow-paper object: a skip has identity,
an edition, and a stranger URL. A winner-only diary scores 0 at CASP.

Not a production weld. their_production stays false. No PII.
"""
from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any

SPEC = "gate-skip-remaining-v1"

try:
    from gate import db
except ImportError:
    import db  # type: ignore


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(obj: Any) -> str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


def _ensure(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS skip_editions (
            id TEXT PRIMARY KEY,
            kind TEXT NOT NULL,
            edition_hash TEXT NOT NULL,
            body_json TEXT NOT NULL,
            casp_score REAL,
            created_at TEXT NOT NULL
        )
        """
    )


def ensure_schema() -> None:
    with db.db() as conn:
        _ensure(conn)


def spec(public_url: str) -> dict:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Skip remaining",
        "atom": "D1 — skip is a conserved register, not a hole in the winner row",
        "yellow_paper": (
            "A ranked write that places one name and does not mint skip remaining "
            "for every jumped name did not happen as a public fact."
        ),
        "types": ["offer", "accept", "execute", "skip"],
        "edition_binds": ["sequence", "placed_id", "kind"],
        "casp": {
            "pass": 1.0,
            "winner_only": 0.0,
            "incomplete": "jumped_with_receipt / jumped",
        },
        "dated_writes_not_married": [
            "POST /job/v1/jobs/{job_id}/oos-conflicts/resolve",
            "POST /job/v1/jobs/{job_id}/handle-preemptions",
            "OPO leave-sequence / AOOS bypass 861-863, 887, 799",
        ],
        "mint": f"{base}/v1/skip/mint",
        "casp_url": f"{base}/v1/skip/casp",
        "page": f"{base}/skip",
        "stranger": f"{base}/.well-known/skip/{{id}}.json",
        "their_production": False,
        "not": [
            "authorization to transplant, bind, or pay",
            "a 26th S-number",
            "the VCS carbon registry",
            "Nisaba Verra the room — that brand exports dual-rail packs",
        ],
        "brands": {
            "gate": "skip cannot be 200-OK into the write",
            "velaru": "stranger URL of the discarded value",
            "erra": "HOLD as conserved skip of capital",
            "verra": "Bind Room closed without write is remaining",
            "mishara": "the customer is the jumped name",
        },
    }


def _index_of(sequence: list[dict], placed_id: str) -> int:
    for i, row in enumerate(sequence):
        if str(row.get("id") or "") == placed_id:
            return i
    return -1


def jumped_ids(sequence: list[dict], placed_id: str) -> list[str]:
    idx = _index_of(sequence, placed_id)
    if idx < 0:
        return []
    return [str(row.get("id") or "") for row in sequence[:idx] if row.get("id")]


def casp_score(*, sequence: list[dict], placed_id: str, skip_ids: list[str]) -> dict:
    if not sequence:
        return {"score": 0.0, "reason": "empty_sequence", "jumped": 0, "receipts": 0, "pass": False}
    if _index_of(sequence, placed_id) < 0:
        return {
            "score": 0.0,
            "reason": "placed_not_in_sequence",
            "jumped": 0,
            "receipts": 0,
            "pass": False,
        }
    jumped = jumped_ids(sequence, placed_id)
    have = set(skip_ids)
    covered = [j for j in jumped if j in have]
    extra = [s for s in skip_ids if s not in jumped]
    if not jumped:
        return {
            "score": 1.0,
            "reason": "in_sequence_head",
            "jumped": 0,
            "receipts": 0,
            "pass": True,
        }
    if not covered:
        return {
            "score": 0.0,
            "reason": "winner_only",
            "jumped": len(jumped),
            "receipts": 0,
            "pass": False,
        }
    ratio = len(covered) / len(jumped)
    reason = "complete" if ratio == 1.0 and not extra else "incomplete_skips"
    return {
        "score": round(ratio, 4),
        "reason": reason,
        "jumped": len(jumped),
        "receipts": len(covered),
        "pass": ratio == 1.0 and not extra,
        "missing": [j for j in jumped if j not in have],
        "extra": extra,
    }


def organ_fixture(*, mint_skips: bool = True) -> dict:
    sequence = [
        {"id": "syn-a", "label": "Synthetic A · sequence 1"},
        {"id": "syn-b", "label": "Synthetic B · sequence 2"},
        {"id": "syn-c", "label": "Synthetic C · sequence 3"},
        {"id": "syn-d", "label": "Synthetic D · sequence 4"},
        {"id": "syn-e", "label": "Synthetic E · sequence 5"},
        {"id": "syn-f", "label": "Synthetic F · sequence 6"},
        {"id": "syn-g", "label": "Synthetic G · sequence 7"},
    ]
    placed = "syn-e"
    return {
        "kind": "organ",
        "bypass": "861",
        "sequence": sequence,
        "placed_id": placed,
        "mint_skips": mint_skips,
    }


def policycenter_fixture(*, mint_skips: bool = True) -> dict:
    sequence = [
        {"id": "field-orig", "label": "dateOfBirthInternal originalValue"},
        {"id": "field-yours", "label": "dateOfBirthInternal yourValue (acceptYours)"},
    ]
    return {
        "kind": "policycenter",
        "bypass": "oos-conflicts/resolve",
        "sequence": sequence,
        "placed_id": "field-yours",
        "mint_skips": mint_skips,
    }


def _receipts_for(payload: dict) -> list[dict]:
    seq = list(payload.get("sequence") or [])
    placed = str(payload.get("placed_id") or "")
    if not payload.get("mint_skips", True):
        return []
    out = []
    for jid in jumped_ids(seq, placed):
        row = next((r for r in seq if str(r.get("id")) == jid), {"id": jid})
        out.append(
            {
                "id": jid,
                "label": row.get("label") or jid,
                "kind": "skip",
            }
        )
    return out


def mint(payload: dict, *, public_url: str) -> dict:
    seq = list(payload.get("sequence") or [])
    placed = str(payload.get("placed_id") or "").strip()
    kind = str(payload.get("kind") or "generic").strip() or "generic"
    bypass = str(payload.get("bypass") or "").strip()
    mint_skips = bool(payload.get("mint_skips", True))
    if not seq or not placed:
        return {"ok": False, "reason": "sequence_and_placed_required"}
    receipts = _receipts_for(
        {"sequence": seq, "placed_id": placed, "mint_skips": mint_skips}
    )
    skip_ids = [str(r["id"]) for r in receipts]
    casp = casp_score(sequence=seq, placed_id=placed, skip_ids=skip_ids)
    edition = {
        "kind": kind,
        "bypass": bypass,
        "sequence": seq,
        "placed_id": placed,
        "skips": receipts,
    }
    edition_hash = _hash(edition)
    eid = str(uuid.uuid4())
    body = {
        "ok": True,
        "spec": SPEC,
        "id": eid,
        "edition_hash": edition_hash,
        "kind": kind,
        "bypass": bypass,
        "sequence": seq,
        "placed_id": placed,
        "skips": receipts,
        "casp": casp,
        "verify_url": f"{public_url.rstrip('/')}/.well-known/skip/{eid}.json",
        "page": f"{public_url.rstrip('/')}/skip/{eid}",
        "their_production": False,
        "created_at": db.utc_now(),
    }
    with db.db() as conn:
        _ensure(conn)
        conn.execute(
            """
            INSERT INTO skip_editions (id, kind, edition_hash, body_json, casp_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (eid, kind, edition_hash, json.dumps(body), casp["score"], body["created_at"]),
        )
    return body


def get(eid: str) -> dict | None:
    with db.db() as conn:
        _ensure(conn)
        row = conn.execute("SELECT body_json FROM skip_editions WHERE id = ?", (eid,)).fetchone()
    if not row:
        return None
    return json.loads(row["body_json"])


def casp_body(payload: dict) -> dict:
    seq = list(payload.get("sequence") or [])
    placed = str(payload.get("placed_id") or "").strip()
    skip_ids = [str(x) for x in (payload.get("skip_ids") or [])]
    if payload.get("skips"):
        skip_ids = [str(s.get("id") or s) for s in payload["skips"]]
    casp = casp_score(sequence=seq, placed_id=placed, skip_ids=skip_ids)
    return {"ok": True, "spec": SPEC, "casp": casp, "their_production": False}
