"""Items 112–116 — FRE 902 packet, 17a-4 identity, C2PA ingredients, redaction, binding."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

SPEC_902 = "gate-fre902-packet-v1"
SPEC_ING = "gate-ingredient-chain-v1"
SPEC_REDACT = "gate-redaction-v1"
SPEC_BIND = "gate-binding-audit-v1"

SYSTEM_DESCRIPTION = (
    "Gate produces a canonical JSON receipt (sorted keys, no whitespace), hashes it "
    "with SHA-256, and optionally signs the hash with the published Ed25519 key. "
    "Bind events chain via prev_receipt_hash. This description is how the record is "
    "produced (FRE 902(13) system description). It is not a live courtroom certification."
)

# Verdict and its timestamp may never be redacted (item 115).
FORBIDDEN_REDACT = frozenset(
    {
        "decision",
        "verdict",
        "acted",
        "created_at",
        "canonical_receipt.decision",
        "canonical_receipt.acted",
        "canonical_receipt.created_at",
    }
)

MAX_INGREDIENTS = 8

BINDING_AUDIT = (
    {
        "path": "receipt_hash",
        "binding": "hard",
        "mechanism": "sha256(canonical_receipt_json)",
        "plain": "Hash proof. Tamper-evident.",
    },
    {
        "path": "receipt_signature",
        "binding": "hard",
        "mechanism": "ed25519 over receipt_hash",
        "plain": "Signature proof. Tamper-evident when the published key verifies.",
    },
    {
        "path": "ingredients.ingredient_hash",
        "binding": "hard",
        "mechanism": "sha256 of carried canonical",
        "plain": "C2PA-style hard binding of an embedded upstream receipt.",
    },
    {
        "path": "cdpi.composite",
        "binding": "soft",
        "mechanism": "weighted accuracy/severity/trend",
        "plain": "Correlation score. Not a hash. Not interchangeable with receipt_hash.",
    },
    {
        "path": "atlas.classification_confidence",
        "binding": "soft",
        "mechanism": "rule label against MITRE ATLAS",
        "plain": "Soft taxonomy label. Hash-verify the receipt separately.",
    },
    {
        "path": "harm.fingerprint_cluster_id",
        "binding": "soft",
        "mechanism": "exact fingerprint string cluster",
        "plain": "Syndromic grouping. Not proof the harm occurred.",
    },
    {
        "path": "challenge.counter_case_score.engagement_score",
        "binding": "soft",
        "mechanism": "overlap of cited evidence vs hop fields",
        "plain": "Review flag. Not a signature.",
    },
)


def _iso(dt: datetime | None = None) -> str:
    return (dt or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0).isoformat()


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def responsible_identity(row: dict[str, Any] | None) -> str:
    """Item 113 — who created this record, not just that it happened."""
    row = row or {}
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    named = hop.get("responsible_identity") or hop.get("actor_id")
    if named:
        return str(named)
    fp = row.get("receipt_public_key_fingerprint")
    if fp:
        return str(fp)
    return "UNSIGNED"


def transitions(row: dict[str, Any]) -> list[dict[str, Any]]:
    """17a-4(f) wants a responsible_identity on each state transition."""
    hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
    identity = responsible_identity(row)
    rows = [
        {
            "action": "created",
            "at": row.get("created_at"),
            "responsible_identity": identity,
            "decision": row.get("decision"),
        }
    ]
    if hop.get("human_signoff") or hop.get("two_person"):
        rows.append(
            {
                "action": "human_signoff",
                "at": hop.get("signed_at") or row.get("created_at"),
                "responsible_identity": str(hop.get("human_signoff") or hop.get("two_person") or identity),
                "decision": row.get("decision"),
            }
        )
    return rows


def hash_proof(*, original_hash: str | None, copy_obj: Any) -> dict[str, Any]:
    copy_json = _canonical(copy_obj) if not isinstance(copy_obj, str) else copy_obj
    copy_hash = hashlib.sha256(copy_json.encode("utf-8")).hexdigest()
    original = (original_hash or "").strip() or None
    return {
        "original_hash": original,
        "copy_hash": copy_hash,
        "algorithm": "sha256",
        "match": bool(original and original == copy_hash),
    }


def certification_packet(
    row: dict[str, Any],
    *,
    copy_canonical: dict[str, Any] | str | None = None,
    certifier_identity: str | None = None,
    notice_served: bool = False,
) -> dict[str, Any]:
    """Item 112 — on-demand addendum. Does not mint a live FRE 902 certification."""
    if copy_canonical is None:
        hop = row.get("hop") if isinstance(row.get("hop"), dict) else {}
        copy_canonical = receipt_mod.build_canonical_receipt(
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
    proof = hash_proof(original_hash=row.get("receipt_hash"), copy_obj=copy_canonical)
    named = (certifier_identity or "").strip()
    return {
        "spec": SPEC_902,
        "receipt_id": row.get("id") or row.get("receipt_hash"),
        "hash_proof": proof,
        "system_description": SYSTEM_DESCRIPTION,
        "qualified_person_cert": {
            "certifier_identity": named or None,
            "cert_statement": (
                "I certify this system produces an accurate result of the canonical receipt hash."
                if named
                else None
            ),
            "certified_at": _iso() if named else None,
            "present": bool(named),
        },
        "opposing_party_notice_ready": bool(notice_served),
        "live_fre_902_cert": False,
        "legal_advice": False,
        "plain": (
            "Hash match is computed here. A live FRE 902(13)/(14) certification and "
            "opposing-party notice are not minted from this packet."
        ),
        "responsible_identity": responsible_identity(row),
        "transitions": transitions(row),
    }


def _parent_manifest(parent: dict[str, Any]) -> dict[str, Any]:
    hop = parent.get("hop") if isinstance(parent.get("hop"), dict) else {}
    canonical = receipt_mod.build_canonical_receipt(
        event_id=parent.get("id"),
        fuse_id=parent.get("fuse_id"),
        job_id=parent.get("job_id"),
        decision=parent.get("decision"),
        acted=parent.get("acted"),
        verify_url=parent.get("verify_url"),
        created_at=parent.get("created_at"),
        hop=hop,
        prev_receipt_hash=parent.get("prev_receipt_hash"),
    )
    return {
        "receipt_id": parent.get("id"),
        "receipt_hash": parent.get("receipt_hash"),
        "decision": parent.get("decision"),
        "created_at": parent.get("created_at"),
        "responsible_identity": responsible_identity(parent),
        "canonical_receipt": canonical,
    }


def ingredients(row: dict[str, Any], rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Item 114 — embed the upstream receipt, not an ID-only pointer."""
    by_hash = {str(r.get("receipt_hash")): r for r in rows if r.get("receipt_hash")}
    chain = []
    seen: set[str] = set()
    cur = row
    while cur and len(chain) < MAX_INGREDIENTS:
        prev = str(cur.get("prev_receipt_hash") or "").strip()
        if not prev or prev in seen:
            break
        seen.add(prev)
        parent = by_hash.get(prev)
        if not parent:
            chain.append(
                {
                    "ingredient_receipt_id": None,
                    "ingredient_hash": prev,
                    "carried_manifest": None,
                    "hard_binding": False,
                    "plain": "Pointer only — parent bytes are not on this mouth.",
                }
            )
            break
        manifest = _parent_manifest(parent)
        carried_hash = hashlib.sha256(_canonical(manifest["canonical_receipt"]).encode("utf-8")).hexdigest()
        stored = str(parent.get("receipt_hash") or "")
        chain.append(
            {
                "ingredient_receipt_id": parent.get("id"),
                "ingredient_hash": stored or carried_hash,
                "carried_manifest": manifest,
                "hard_binding": bool(stored and stored == carried_hash),
                "plain": "Embedded upstream canonical. Hard binding if hash matches.",
            }
        )
        cur = parent
    return {
        "spec": SPEC_ING,
        "receipt_id": row.get("id"),
        "ingredients": chain,
        "plain": "A stranger opening the last receipt gets the ancestry without trusting a party's database.",
    }


def validate_redaction(fields: list[str]) -> dict[str, Any]:
    """Item 115 — reject any write that tries to redact verdict or its timestamp."""
    asked = [str(f).strip() for f in fields if str(f).strip()]
    forbidden = [f for f in asked if f in FORBIDDEN_REDACT or f.split(".")[-1] in {"decision", "verdict", "created_at", "acted"}]
    ok = not forbidden
    return {
        "spec": SPEC_REDACT,
        "ok": ok,
        "fields": asked,
        "forbidden": forbidden,
        "plain": (
            "Verdict and its timestamp are never redacted. A redaction is its own receipt line."
            if ok
            else "Rejected. ACT/HOLD/BLOCK and created_at cannot be redacted."
        ),
    }


def redaction_event(*, event_id: str, fields: list[str], actor: str | None = None) -> dict[str, Any]:
    check = validate_redaction(fields)
    if not check["ok"]:
        return {**check, "logged": False}
    rec = {
        "spec": SPEC_REDACT,
        "ok": True,
        "logged": True,
        "action": "redaction",
        "event_id": event_id,
        "fields": check["fields"],
        "responsible_identity": actor or "UNSIGNED",
        "at": _iso(),
        "plain": "Something was removed; the removal is visible. The verdict line stays.",
    }
    issued = receipt_mod.issue_receipt(
        event_id="redact:" + (event_id or "unknown"),
        fuse_id="gate-redaction",
        job_id=None,
        decision="HOLD",
        acted=False,
        verify_url=None,
        created_at=rec["at"],
        hop={"kind": "redaction", "fields": check["fields"], "target": event_id},
        prev_receipt_hash=None,
    )
    rec["receipt_hash"] = issued.get("receipt_hash")
    rec["decision"] = "HOLD"
    rec["created_at"] = rec["at"]
    return rec


def binding_audit() -> dict[str, Any]:
    """Item 116 — fuzzy/CDPI paths stay soft; hashes stay hard. Never interchangeable."""
    hard = [x for x in BINDING_AUDIT if x["binding"] == "hard"]
    soft = [x for x in BINDING_AUDIT if x["binding"] == "soft"]
    return {
        "spec": SPEC_BIND,
        "hard": hard,
        "soft": soft,
        "interchangeable": False,
        "plain": (
            "CDPI, ATLAS labels, and fingerprint clusters are soft correlation. "
            "receipt_hash and ingredient_hash are hard bindings. They are not the same kind of proof."
        ),
    }


def attach(row: dict[str, Any], rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    rows = rows or [row]
    packet = certification_packet(row)
    ings = ingredients(row, rows)
    return {
        "certification_packet": packet,
        "responsible_identity": packet["responsible_identity"],
        "transitions": packet["transitions"],
        "ingredients": ings["ingredients"],
        "binding": binding_audit(),
        "in_signed_canonical": False,
        "live_fre_902_cert": False,
    }
