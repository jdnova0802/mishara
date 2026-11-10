"""DFIR envelope helpers — taxonomy, handlers, public hash re-derive (69–74)."""
from __future__ import annotations

from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

SPEC = "gate-dfir-envelope-v1"
VERIFY_SPEC = "gate-public-verify-v1"

TAXONOMY = {
    "premium_exceeds_authority": ("LIMIT", "Premium is over the delegated authority."),
    "fuse_dead_or_halt": ("FUSE", "Fuse is DEAD or the hop halted."),
    "line_not_in_authority": ("LINE", "Line of business is outside the paper."),
    "state_not_in_authority": ("STATE", "State is outside the paper."),
    "model_225_30_day_commissioner_notice_missing": (
        "NOTICE",
        "MGA termination without the 30-day commissioner notice.",
    ),
    "job_id_required_for_ticket": ("JOB", "No job_id, so no bind ticket."),
}


def classify_reason(raw: str | None) -> dict[str, str | None]:
    try:
        from gate import sanitize as sanitize_mod
    except ImportError:
        import sanitize as sanitize_mod

    text = sanitize_mod.strip_agent(raw)
    if not text:
        return {"reason_code": "UNSPECIFIED", "reason_text": "No reason on the hop.", "raw": None}
    key = text
    if key in TAXONOMY:
        code, plain = TAXONOMY[key]
        return {"reason_code": code, "reason_text": plain, "raw": text}
    upper = text.upper()
    if "PREMIUM" in upper or "LIMIT" in upper:
        return {"reason_code": "LIMIT", "reason_text": text, "raw": text}
    if "FUSE" in upper or "DEAD" in upper or "HALT" in upper:
        return {"reason_code": "FUSE", "reason_text": text, "raw": text}
    return {"reason_code": "OTHER", "reason_text": text, "raw": text}


def chain_of_handlers(receipt_row: dict[str, Any]) -> list[dict[str, Any]]:
    hop = receipt_row.get("hop") if isinstance(receipt_row.get("hop"), dict) else {}
    gate_key = receipt_row.get("receipt_public_key_fingerprint")
    handlers = [
        {
            "role": "gate",
            "present": True,
            "key_id": gate_key,
            "responsible_identity": gate_key or "UNSIGNED",
            "signature": receipt_row.get("receipt_signature"),
        },
        {
            "role": "erra",
            "present": bool(hop.get("erra") or hop.get("pattern_grade")),
            "key_id": (hop.get("erra") or {}).get("key_id") if isinstance(hop.get("erra"), dict) else None,
            "responsible_identity": None,
            "signature": None,
            "plain": "Absent unless the hop carried an Erra grade.",
        },
        {
            "role": "velaru",
            "present": hop.get("verdict") is not None or hop.get("state") is not None,
            "key_id": None,
            "responsible_identity": "velaru_fuse_hop",
            "signature": None,
            "plain": "Hop state is present. Velaru does not countersign this envelope.",
        },
        {
            "role": "human",
            "present": bool(hop.get("human_signoff") or hop.get("two_person")),
            "key_id": None,
            "responsible_identity": None,
            "signature": None,
            "plain": "Absent unless a human sign-off is on the hop.",
        },
    ]
    return handlers


def durable_anchor(receipt_row: dict[str, Any], public_url: str) -> dict[str, Any]:
    eid = receipt_row.get("id")
    return {
        "ledger_position": {
            "prev_receipt_hash": receipt_row.get("prev_receipt_hash"),
            "receipt_hash": receipt_row.get("receipt_hash"),
        },
        "merkle_head": f"{public_url.rstrip('/')}/.well-known/evidence-head.json",
        "inclusion_proof": f"{public_url.rstrip('/')}/.well-known/receipt/{eid}/proof.json" if eid else None,
        "ots": f"{public_url.rstrip('/')}/.well-known/evidence-ots.json",
        "scitt": None,
        "plain": "Merkle evidence-head is the durable pointer. SCITT log URL is unset until one is welded.",
    }


def public_verify(receipt_row: dict[str, Any], *, public_url: str) -> dict[str, Any]:
    payload = receipt_mod.receipt_to_public_payload(receipt_row=receipt_row, public_url=public_url)
    canonical = payload.get("canonical_receipt")
    recomputed = None
    if isinstance(canonical, dict):
        recomputed = receipt_mod.compute_receipt_hash(receipt_mod._canonical_json(canonical))
    claimed = receipt_row.get("receipt_hash")
    hash_matches = bool(recomputed and claimed and recomputed == claimed)
    sig_ok = receipt_mod.verify_receipt_signature(
        receipt_hash=str(claimed or ""),
        signature_b64=receipt_row.get("receipt_signature"),
    )
    return {
        "spec": VERIFY_SPEC,
        "event_id": receipt_row.get("id"),
        "claimed_hash": claimed,
        "recomputed_hash": recomputed,
        "hash_matches": hash_matches,
        "signature_ok": sig_ok,
        "key_source": "gate_published_env",
        "receipt_does_not_name_the_key": True,
        "payload": payload,
        "plain": (
            "Hash is re-derived from the canonical object. Signature is checked with "
            "the published Gate key, not a key named inside the receipt."
        ),
    }
