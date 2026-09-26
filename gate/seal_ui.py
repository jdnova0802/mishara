"""Human-facing seal check over signed receipts + Merkle inclusion.

Apple-simple words. Custody + evidence log underneath.
"""

from __future__ import annotations

import json
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

try:
    from gate import evidence_log as evidence_log_mod
except ImportError:
    import evidence_log as evidence_log_mod

try:
    from gate import claim_scope as claim_scope_mod
except ImportError:
    import claim_scope as claim_scope_mod

try:
    from gate import write_state as write_state_mod
except ImportError:
    import write_state as write_state_mod

SPEC = "gate-seal-v1"


def _canonical_hash(row: dict) -> str | None:
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else None
    if hop is None:
        hop_json = row.get("hop_json")
        if hop_json:
            try:
                hop = json.loads(hop_json)
            except Exception:
                hop = {}
    hop = hop or {}
    try:
        canonical = receipt_mod.build_canonical_receipt(
            event_id=row.get("id"),
            fuse_id=row.get("fuse_id"),
            job_id=row.get("job_id"),
            decision=row.get("decision"),
            acted=row.get("acted"),
            verify_url=row.get("verify_url"),
            created_at=row.get("created_at"),
            hop=hop,
            prev_receipt_hash=row.get("prev_receipt_hash"),
        )
        canonical_json = json.dumps(
            canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        return receipt_mod.compute_receipt_hash(canonical_json)
    except Exception:
        return None


def seal_event(event_id: str, *, rows: list[dict] | None = None) -> dict[str, Any]:
    """One-word seal for a bind event id."""
    try:
        from gate import db
    except ImportError:
        import db

    eid = (event_id or "").strip()
    if not eid:
        return {
            "spec": SPEC,
            "word": "MISSING",
            "plain": "Paste an event id.",
            "their_production": False,
        }

    row = db.get_bind_event(eid)
    if not row:
        body = {
            "spec": SPEC,
            "event_id": eid,
            "word": "MISSING",
            "plain": "No receipt for this id.",
            "write_state": write_state_mod.for_seal_verify(),
            "their_production": False,
        }
        scope = claim_scope_mod.for_seal(event_id=eid, word="MISSING")
        return claim_scope_mod.attach(body, scope=scope, force=True)

    stored_hash = (row.get("receipt_hash") or "").strip()
    recomputed = _canonical_hash(row)
    hash_ok = bool(stored_hash and recomputed and stored_hash == recomputed)

    sig = row.get("receipt_signature")
    sig_present = bool(sig)
    sig_ok = (
        receipt_mod.verify_receipt_signature(
            receipt_hash=stored_hash, signature_b64=sig
        )
        if sig_present and stored_hash
        else False
    )

    if rows is None:
        rows = db.list_bind_events_chronological()
    bundle = evidence_log_mod.proof_bundle(rows, eid)
    inclusion_ok = False
    root_hash = None
    if bundle and stored_hash:
        inclusion = bundle.get("inclusion") or {}
        root_hash = (bundle.get("tree_head") or {}).get("root_hash")
        try:
            inclusion_ok = evidence_log_mod.verify_inclusion(
                leaf_hash=stored_hash,
                root_hash=root_hash or inclusion.get("root_hash") or "",
                proof=inclusion,
            )
        except Exception:
            inclusion_ok = False

    checks = {
        "hash": hash_ok,
        "signature": sig_ok if sig_present else None,
        "inclusion": inclusion_ok,
    }

    if not hash_ok or not inclusion_ok or (sig_present and not sig_ok):
        word = "BROKEN"
        plain = "Something does not check — hash, signature, or log inclusion failed."
    elif not sig_present:
        word = "UNSIGNED"
        plain = "Hash and log hold, but this receipt has no signature yet."
    else:
        word = "HOLDS"
        plain = "Signed receipt. Hash matches. In the evidence log."

    body = {
        "spec": SPEC,
        "event_id": eid,
        "word": word,
        "plain": plain,
        "decision": row.get("decision"),
        "fuse_id": row.get("fuse_id"),
        "job_id": row.get("job_id"),
        "receipt_hash": stored_hash or None,
        "root_hash": root_hash,
        "checks": checks,
        "write_state": write_state_mod.for_seal_verify(),
        "atoms": {
            "receipt": f"/.well-known/receipt/{eid}.json",
            "proof": f"/.well-known/receipt/{eid}/proof.json",
            "packet": f"/.well-known/evidence-packet/{eid}.json",
        },
        "their_production": False,
    }
    # MISSING / BROKEN / UNSIGNED are negative or degraded custody claims — scope them.
    scope = claim_scope_mod.for_seal(event_id=eid, word=word)
    return claim_scope_mod.attach(body, scope=scope, force=word != "HOLDS")


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Seal",
        "promise": "Paste an event. Does the halt still hold for a stranger?",
        "words": ["HOLDS", "BROKEN", "UNSIGNED", "MISSING"],
        "page": f"{base}/seal",
        "api": f"{base}/v1/seal",
        "public_key_b64": receipt_mod.public_key_b64(),
        "public_key_fingerprint": receipt_mod.receipt_public_key_fingerprint(),
        "atoms": [
            "Ed25519 signed receipt hash",
            "Merkle inclusion against published evidence head",
        ],
        "their_production": False,
    }
