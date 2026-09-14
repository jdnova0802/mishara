"""Signed Remaining Timestamp — authenticity of the non-event.

Chrome 2018 refused certs without an SCT. This is that trick on silence:
edition hash + jumped IDs + UTC + inclusion proof. No SRT → 403.

Also on this plant (bits, not products):
- P9 act-idempotency remaining: this irreversible write already happened.
- K3 mortmain bit: spendable false; CHARGE cannot resurrect into spend.

Seed, not civilization default. their_production stays false. Thesis unchanged.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import uuid
from typing import Any

SPEC = "gate-srt-v1"
REASON_MISSING = "srt_missing"
REASON_INVALID = "srt_invalid"
REASON_ALREADY = "already_written"
REASON_MORTMAIN = "mortmain_not_spendable"

try:
    from gate import db
    from gate import evidence_log
except ImportError:
    import db  # type: ignore
    import evidence_log  # type: ignore


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash(obj: Any) -> str:
    return hashlib.sha256(_canonical(obj).encode("utf-8")).hexdigest()


def _secret() -> bytes:
    raw = (os.getenv("GATE_SECRET_KEY") or os.getenv("GATE_CHARGE_SECRET") or "").strip()
    if not raw:
        raw = "gate-srt-unconfigured"
    return raw.encode("utf-8")


def _sign(unsigned: dict) -> str:
    return hmac.new(_secret(), _canonical(unsigned).encode("utf-8"), hashlib.sha256).hexdigest()


def _ensure(conn) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS srt_log (
            id TEXT PRIMARY KEY,
            edition_id TEXT,
            edition_hash TEXT NOT NULL,
            leaf_hash TEXT NOT NULL,
            body_json TEXT NOT NULL,
            log_index INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS act_remaining (
            fingerprint TEXT PRIMARY KEY,
            first_srt_id TEXT,
            first_edition_id TEXT,
            body_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS mortmain_remaining (
            id TEXT PRIMARY KEY,
            edition_id TEXT,
            spendable INTEGER NOT NULL DEFAULT 0,
            body_json TEXT NOT NULL,
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
        "name": "Signed Remaining Timestamp",
        "kind": "authenticity of the non-event",
        "yellow_paper": (
            "A dated irreversible write that 200-OKs a winner without a signed "
            "remaining timestamp of the jumped names did not happen as a public fact."
        ),
        "chrome_2018": "Client fail-closes if SRT is missing. Same muscle as refusing a cert without an SCT.",
        "atomic": ["edition_hash", "jumped_ids", "utc", "inclusion_proof", "hmac"],
        "present": f"{base}/v1/skip/srt",
        "stranger": f"{base}/.well-known/srt/{{id}}.json",
        "head": f"{base}/.well-known/srt-head.json",
        "act_remaining": f"{base}/.well-known/act/{{fingerprint}}.json",
        "mortmain_charge": f"{base}/v1/skip/mortmain/charge",
        "page": f"{base}/skip",
        "their_production": False,
        "civilization_default": False,
        "thesis_unchanged": True,
        "not": [
            "a certificate authority",
            "Certificate Transparency of issued certs",
            "a 10/10 padlock today",
            "outbound",
            "a thesis rewrite",
        ],
        "bits": {
            "P9": "act-idempotency remaining — this write already happened, stranger-openable",
            "K3": "mortmain — spendable false; CHARGE cannot make it spend",
        },
    }


def _leaf_hashes(conn) -> list[str]:
    rows = conn.execute("SELECT leaf_hash FROM srt_log ORDER BY log_index ASC, id ASC").fetchall()
    return [r["leaf_hash"] for r in rows]


def issue_srt(edition: dict, *, public_url: str) -> dict:
    jumped = [str(s.get("id") or s) for s in (edition.get("skips") or [])]
    if edition.get("casp", {}).get("missing"):
        jumped = jumped  # receipts only; missing names are why CASP failed
    issued_at = db.utc_now()
    sid = str(uuid.uuid4())
    core = {
        "spec": SPEC,
        "id": sid,
        "edition_id": edition.get("id"),
        "edition_hash": edition.get("edition_hash"),
        "jumped_ids": jumped,
        "issued_at": issued_at,
    }
    leaf_hash = _hash(core)
    with db.db() as conn:
        _ensure(conn)
        prior = _leaf_hashes(conn)
        log_index = len(prior)
        leaves = prior + [leaf_hash]
        proof = evidence_log.inclusion_proof(leaves, log_index)
        unsigned = {
            **core,
            "leaf_hash": leaf_hash,
            "log_index": log_index,
            "inclusion": proof,
        }
        signature = _sign(unsigned)
        body = {
            **unsigned,
            "signature": signature,
            "verify_url": f"{public_url.rstrip('/')}/.well-known/srt/{sid}.json",
            "their_production": False,
            "civilization_default": False,
        }
        conn.execute(
            """
            INSERT INTO srt_log (id, edition_id, edition_hash, leaf_hash, body_json, log_index, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                sid,
                edition.get("id"),
                edition.get("edition_hash"),
                leaf_hash,
                json.dumps(body),
                log_index,
                issued_at,
            ),
        )
    return body


def get_srt(sid: str) -> dict | None:
    with db.db() as conn:
        _ensure(conn)
        row = conn.execute("SELECT body_json FROM srt_log WHERE id = ?", (sid,)).fetchone()
    if not row:
        return None
    return json.loads(row["body_json"])


def tree_head() -> dict:
    with db.db() as conn:
        _ensure(conn)
        leaves = _leaf_hashes(conn)
    return {
        "spec": SPEC,
        "tree_size": len(leaves),
        "root_hash": evidence_log.merkle_root(leaves),
        "their_production": False,
    }


def verify_srt(srt: dict | None) -> dict:
    if not isinstance(srt, dict) or not srt:
        return {"ok": False, "allow": False, "halt": True, "reason": REASON_MISSING, "their_production": False}
    signature = str(srt.get("signature") or "")
    unsigned = {k: v for k, v in srt.items() if k not in {"signature", "verify_url", "their_production", "civilization_default"}}
    expect = _sign(unsigned)
    if not signature or not hmac.compare_digest(signature, expect):
        return {"ok": False, "allow": False, "halt": True, "reason": REASON_INVALID, "their_production": False}
    core = {
        "spec": srt.get("spec"),
        "id": srt.get("id"),
        "edition_id": srt.get("edition_id"),
        "edition_hash": srt.get("edition_hash"),
        "jumped_ids": srt.get("jumped_ids"),
        "issued_at": srt.get("issued_at"),
    }
    if _hash(core) != srt.get("leaf_hash"):
        return {"ok": False, "allow": False, "halt": True, "reason": REASON_INVALID, "their_production": False}
    proof = srt.get("inclusion") or {}
    if not evidence_log.verify_inclusion(
        leaf_hash=str(srt.get("leaf_hash") or ""),
        root_hash=str(proof.get("root_hash") or ""),
        proof=proof,
    ):
        return {"ok": False, "allow": False, "halt": True, "reason": REASON_INVALID, "their_production": False}
    return {
        "ok": True,
        "allow": True,
        "halt": False,
        "reason": None,
        "srt": srt,
        "their_production": False,
    }


def present(payload: dict) -> dict:
    raw = payload.get("srt")
    sid = str(payload.get("srt_id") or "").strip()
    if not raw and sid:
        raw = get_srt(sid)
    return verify_srt(raw if isinstance(raw, dict) else None)


def get_act(fingerprint: str) -> dict | None:
    with db.db() as conn:
        _ensure(conn)
        row = conn.execute(
            "SELECT body_json FROM act_remaining WHERE fingerprint = ?",
            (fingerprint,),
        ).fetchone()
    if not row:
        return None
    return json.loads(row["body_json"])


def record_act(*, fingerprint: str, srt: dict, edition: dict, public_url: str) -> dict:
    prior = get_act(fingerprint)
    if prior:
        return prior
    created = db.utc_now()
    body = {
        "ok": True,
        "kind": "act_idempotency_remaining",
        "atom": "P9",
        "fingerprint": fingerprint,
        "already_written": True,
        "first_srt_id": srt.get("id"),
        "first_edition_id": edition.get("id"),
        "verify_url": f"{public_url.rstrip('/')}/.well-known/act/{fingerprint}.json",
        "srt_url": srt.get("verify_url"),
        "created_at": created,
        "their_production": False,
        "not": "Stripe 24h idempotency on charges",
    }
    with db.db() as conn:
        _ensure(conn)
        conn.execute(
            """
            INSERT OR IGNORE INTO act_remaining
            (fingerprint, first_srt_id, first_edition_id, body_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (fingerprint, srt.get("id"), edition.get("id"), json.dumps(body), created),
        )
    return get_act(fingerprint) or body


def mint_mortmain(*, edition: dict, srt: dict, public_url: str) -> dict:
    mid = str(uuid.uuid4())
    created = db.utc_now()
    body = {
        "ok": True,
        "kind": "mortmain",
        "atom": "K3",
        "id": mid,
        "spendable": False,
        "edition_id": edition.get("id"),
        "srt_id": srt.get("id"),
        "verify_url": f"{public_url.rstrip('/')}/.well-known/mortmain/{mid}.json",
        "created_at": created,
        "charge": "CHARGE cannot resurrect this remaining into spend",
        "their_production": False,
        "not": ["a Waqf Board", "the VCS carbon registry"],
    }
    with db.db() as conn:
        _ensure(conn)
        conn.execute(
            """
            INSERT INTO mortmain_remaining (id, edition_id, spendable, body_json, created_at)
            VALUES (?, ?, 0, ?, ?)
            """,
            (mid, edition.get("id"), json.dumps(body), created),
        )
    return body


def get_mortmain(mid: str) -> dict | None:
    with db.db() as conn:
        _ensure(conn)
        row = conn.execute("SELECT body_json FROM mortmain_remaining WHERE id = ?", (mid,)).fetchone()
    if not row:
        return None
    return json.loads(row["body_json"])


def charge_mortmain(payload: dict) -> dict:
    """CHARGE is accepted as a payment instrument and still cannot spend this remaining."""
    mid = str(payload.get("remaining_id") or payload.get("id") or "").strip()
    row = get_mortmain(mid) if mid else None
    if not row:
        return {
            "ok": False,
            "halt": True,
            "allow": False,
            "spendable": False,
            "reason": "mortmain_not_found",
            "their_production": False,
        }
    return {
        "ok": False,
        "halt": True,
        "allow": False,
        "spendable": False,
        "reason": REASON_MORTMAIN,
        "remaining": row,
        "charge_id": payload.get("charge_id"),
        "their_production": False,
        "note": "A valid CHARGE does not flip spendable. Park, not payout.",
    }


def attach_to_dated_write(
    *,
    payload: dict,
    minted: dict,
    write_obj: dict,
    fingerprint: str,
    public_url: str,
    casp_ok: bool,
) -> dict:
    """Fail-close on missing SRT after CASP would otherwise pass. Replay is remaining, not a second act."""
    extra: dict[str, Any] = {"srt_spec": SPEC, "civilization_default": False}
    if not casp_ok:
        extra["srt"] = None
        extra["reason_if_casp_passed"] = "srt still required"
        return extra
    if payload.get("omit_srt") is True or payload.get("issue_srt") is False:
        extra.update(
            {
                "ok": False,
                "halt": True,
                "allow": False,
                "reason": REASON_MISSING,
                "srt": None,
                "casp_passed": True,
            }
        )
        return extra
    presented = payload.get("srt") or payload.get("srt_id")
    if presented:
        checked = present(payload)
        if not checked.get("allow"):
            extra.update(
                {
                    "ok": False,
                    "halt": True,
                    "allow": False,
                    "reason": checked.get("reason") or REASON_INVALID,
                    "srt": None,
                    "casp_passed": True,
                }
            )
            return extra
        srt = checked["srt"]
        if srt.get("edition_hash") != minted.get("edition_hash"):
            extra.update(
                {
                    "ok": False,
                    "halt": True,
                    "allow": False,
                    "reason": REASON_INVALID,
                    "srt": None,
                    "casp_passed": True,
                }
            )
            return extra
    else:
        srt = issue_srt(minted, public_url=public_url)

    prior = get_act(fingerprint)
    if prior:
        extra.update(
            {
                "ok": True,
                "halt": False,
                "allow": True,
                "reason": REASON_ALREADY,
                "already_written": True,
                "re_act": False,
                "srt": get_srt(prior.get("first_srt_id") or "") or srt,
                "act_remaining": prior,
            }
        )
        return extra

    act = record_act(fingerprint=fingerprint, srt=srt, edition=minted, public_url=public_url)
    extra.update(
        {
            "srt": srt,
            "already_written": False,
            "re_act": True,
            "act_remaining": act,
        }
    )
    if payload.get("mortmain") is True:
        extra["mortmain"] = mint_mortmain(edition=minted, srt=srt, public_url=public_url)
    return extra
