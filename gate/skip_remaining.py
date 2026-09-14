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
    from gate import signed_remaining as srt_mod
except ImportError:
    import db  # type: ignore
    import signed_remaining as srt_mod  # type: ignore


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
        "married_write": {
            "method": "POST",
            "path": "/job/v1/jobs/{job_id}/oos-conflicts/resolve",
            "spend_kind": "skip",
            "plant": "V2",
        },
        "also_in_protocol": [
            "POST /job/v1/jobs/{job_id}/handle-preemptions",
        ],
        "dated_writes_not_married": [
            "OPO leave-sequence / AOOS bypass 861-863, 887, 799",
        ],
        "mint": f"{base}/v1/skip/mint",
        "casp_url": f"{base}/v1/skip/casp",
        "dated_write": f"{base}/v1/skip/dated-write",
        "srt": f"{base}/.well-known/srt.json",
        "srt_present": f"{base}/v1/skip/srt",
        "page": f"{base}/skip",
        "stranger": f"{base}/.well-known/skip/{{id}}.json",
        "implementor": f"{base}/listings/cloudflare-worker-skip.js",
        "their_production": False,
        "srt_required_after_casp": True,
        "civilization_default": False,
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


def casp_score(
    *,
    sequence: list[dict],
    placed_id: str,
    skip_ids: list[str],
    jumped: list[str] | None = None,
) -> dict:
    if jumped is None:
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
    else:
        jumped = [str(j) for j in jumped if j]
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
            "missing": jumped,
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
    explicit = payload.get("jumped")
    ids = [str(j) for j in explicit] if explicit is not None else jumped_ids(seq, placed)
    out = []
    for jid in ids:
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
        {
            "sequence": seq,
            "placed_id": placed,
            "mint_skips": mint_skips,
            "jumped": payload.get("jumped"),
        }
    )
    skip_ids = [str(r["id"]) for r in receipts]
    casp = casp_score(
        sequence=seq,
        placed_id=placed,
        skip_ids=skip_ids,
        jumped=payload.get("jumped"),
    )
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
    casp = casp_score(
        sequence=seq,
        placed_id=placed,
        skip_ids=skip_ids,
        jumped=payload.get("jumped"),
    )
    return {"ok": True, "spec": SPEC, "casp": casp, "their_production": False}


SPEND_KIND_SKIP = "skip"
REASON_NOT_IN_PROTOCOL = "skip_write_not_in_protocol"
MARRIED_SUFFIX = "/oos-conflicts/resolve"
PREEMPT_SUFFIX = "/handle-preemptions"


def normalize_path(path: str | None) -> str:
    p = (path or "").strip()
    if len(p) > 1 and p.endswith("/"):
        p = p[:-1]
    return p


def oos_resolve_path(job_id: str) -> str:
    return f"/job/v1/jobs/{job_id}/oos-conflicts/resolve"


def preempt_path(job_id: str) -> str:
    return f"/job/v1/jobs/{job_id}/handle-preemptions"


def write_in_protocol(path: str | None) -> bool:
    p = normalize_path(path)
    return p.endswith(MARRIED_SUFFIX) or p.endswith(PREEMPT_SUFFIX)


def job_id_from_path(path: str | None) -> str:
    parts = [x for x in normalize_path(path).split("/") if x]
    try:
        i = parts.index("jobs")
        return parts[i + 1]
    except (ValueError, IndexError):
        return ""


def skip_write(*, job_id: str, path: str) -> dict:
    return {
        "method": "POST",
        "path": normalize_path(path),
        "job_id": job_id,
        "spend_kind": SPEND_KIND_SKIP,
    }


def skip_fingerprint(write_obj: dict) -> str:
    body = {
        "job_id": write_obj.get("job_id") or "",
        "method": write_obj.get("method") or "",
        "path": write_obj.get("path") or "",
        "spend_kind": write_obj.get("spend_kind") or "",
    }
    return hashlib.sha256(_canonical(body).encode("utf-8")).hexdigest()


def parse_oos_conflicts(payload: dict) -> dict:
    job_id = str(payload.get("job_id") or job_id_from_path(payload.get("path")) or "pc:OOS-SYN")
    conflicts = list(payload.get("conflicts") or [])
    if not conflicts:
        conflicts = [{"id": "dateOfBirthInternal", "resolution": "acceptYours"}]
    sequence: list[dict] = []
    jumped: list[str] = []
    placed: list[str] = []
    for c in conflicts:
        fid = str(c.get("id") or c.get("path") or "field")
        orig_id = f"{fid}:original"
        yours_id = f"{fid}:yours"
        sequence.append({"id": orig_id, "label": f"{fid} originalValue"})
        sequence.append({"id": yours_id, "label": f"{fid} yourValue"})
        res = str(c.get("resolution") or "acceptYours").strip()
        if res.replace("_", "").lower() in {"acceptyours", "yours"}:
            jumped.append(orig_id)
            placed.append(yours_id)
        else:
            jumped.append(yours_id)
            placed.append(orig_id)
    return {
        "kind": "policycenter",
        "bypass": "oos-conflicts/resolve",
        "job_id": job_id,
        "path": normalize_path(payload.get("path")) or oos_resolve_path(job_id),
        "sequence": sequence,
        "placed_id": placed[-1] if placed else "",
        "jumped": jumped,
        "mint_skips": bool(payload.get("mint_skips", False)),
    }


def parse_preemption(payload: dict) -> dict:
    job_id = str(payload.get("job_id") or job_id_from_path(payload.get("path")) or "pc:PRE-SYN")
    loser = str(payload.get("preempted_job_id") or "pc:LOSER-SYN")
    winner = str(payload.get("preempting_job_id") or job_id)
    return {
        "kind": "policycenter",
        "bypass": "handle-preemptions",
        "job_id": job_id,
        "path": normalize_path(payload.get("path")) or preempt_path(job_id),
        "sequence": [
            {"id": loser, "label": f"preempted quote {loser}"},
            {"id": winner, "label": f"preempting job {winner}"},
        ],
        "placed_id": winner,
        "jumped": [loser],
        "mint_skips": bool(payload.get("mint_skips", False)),
    }


def oos_fixture(*, mint_skips: bool = False, resolution: str = "acceptYours", job_id: str = "pc:OOS-SYN") -> dict:
    return {
        "job_id": job_id,
        "method": "POST",
        "path": oos_resolve_path(job_id),
        "conflicts": [{"id": "dateOfBirthInternal", "resolution": resolution}],
        "mint_skips": mint_skips,
    }


def preempt_fixture(*, mint_skips: bool = False) -> dict:
    job_id = "pc:PRE-SYN"
    return {
        "job_id": job_id,
        "method": "POST",
        "path": preempt_path(job_id),
        "preempted_job_id": "pc:LOSER-SYN",
        "preempting_job_id": job_id,
        "mint_skips": mint_skips,
    }


def evaluate_dated_write(payload: dict, *, public_url: str) -> dict:
    path = normalize_path(payload.get("path"))
    job_id = str(payload.get("job_id") or job_id_from_path(path) or "")
    if not write_in_protocol(path):
        return {
            "ok": False,
            "halt": True,
            "allow": False,
            "reason": REASON_NOT_IN_PROTOCOL,
            "their_production": False,
            "casp": {"score": 0.0, "pass": False, "reason": REASON_NOT_IN_PROTOCOL},
        }
    parsed = parse_preemption(payload) if path.endswith(PREEMPT_SUFFIX) else parse_oos_conflicts(payload)
    minted = mint(parsed, public_url=public_url)
    write_obj = skip_write(job_id=parsed["job_id"] or job_id, path=parsed["path"])
    fp = skip_fingerprint(write_obj)
    casp = minted.get("casp") or {}
    casp_ok = bool(minted.get("ok") and casp.get("pass"))
    allow = casp_ok
    reason = None if allow else (casp.get("reason") or minted.get("reason") or "winner_only")
    out = {
        "ok": allow,
        "halt": not allow,
        "allow": allow,
        "reason": reason,
        "spec": SPEC,
        "plant": "V2",
        "married_write": oos_resolve_path("{job_id}"),
        "spend_write": write_obj,
        "spend_fingerprint": fp,
        "casp": casp,
        "skip": minted if minted.get("ok") else None,
        "verify_url": minted.get("verify_url") if allow else None,
        "their_production": False,
        "civilization_default": False,
        "not": "a production weld. Synthetic PolicyCenter Job API plant.",
    }
    extra = srt_mod.attach_to_dated_write(
        payload=payload,
        minted=minted if minted.get("ok") else {},
        write_obj=write_obj,
        fingerprint=fp,
        public_url=public_url,
        casp_ok=casp_ok,
    )
    out.update(extra)
    if extra.get("allow") is False:
        out["ok"] = False
        out["halt"] = True
        out["allow"] = False
        out["reason"] = extra.get("reason") or out["reason"]
        out["verify_url"] = None
    elif extra.get("allow") is True:
        out["ok"] = True
        out["halt"] = False
        out["allow"] = True
        if extra.get("reason") == srt_mod.REASON_ALREADY:
            out["reason"] = srt_mod.REASON_ALREADY
        out["verify_url"] = (extra.get("srt") or {}).get("verify_url") or out.get("verify_url")
    return out
