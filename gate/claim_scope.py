"""Claim scope — first-class boundary on every negative / Never / DENIED claim.

A stranger verifying a receipt must see *which* logs, time window, and
counterparties were checked — not infer them from which endpoint was called.

Scope is serialized into the signed payload (JWT claims, signed claim
envelopes, or tree-head-adjacent signed bodies).
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

try:
    from gate import receipt as receipt_mod
except ImportError:
    import receipt as receipt_mod

SPEC = "gate-claim-scope-v1"
CLAIM_SPEC = "gate-signed-claim-v1"

# Words that are negative / absence / deny claims and MUST carry signed scope.
NEGATIVE_WORDS = frozenset(
    {
        "NEVER",
        "NO",
        "NO GO",
        "NO_GO",
        "DENIED",
        "NOT DENIED",
        "DOES NOT MATCH",
        "MISSING",
        "BROKEN",
        "SPENT",  # positive presence, but still a scoped claim about the spend map
        "NOT THIS",
        "NOT UAPA",
        "NOT ADMT",
        "FRAD",
        "UNSIGNED",
    }
)


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def build(
    *,
    boundary: str,
    logs: list[str],
    plain: str,
    time_window: dict | None = None,
    counterparties: list[str] | None = None,
    keys_checked: dict | None = None,
    as_of: str | None = None,
    extra: dict | None = None,
) -> dict[str, Any]:
    """Structured scope object. Always not_global — Gate never claims metaphysics."""
    now = as_of or _utc_now_iso()
    tw = time_window or {
        "kind": "all_time_as_of",
        "from": None,
        "to": now,
    }
    out: dict[str, Any] = {
        "spec": SPEC,
        "boundary": boundary,
        "logs": list(logs),
        "as_of": now,
        "time_window": tw,
        "counterparties": counterparties,
        "keys_checked": keys_checked or {},
        "not_global": True,
        "plain": plain,
    }
    if extra:
        out.update(extra)
    return out


def for_never(*, job_id: str, tree_size: int, spend_phase: str, as_of: str | None = None) -> dict:
    return build(
        boundary="gate_redeemed_ticket_spend_map",
        logs=[
            "bind_tickets.consumed_at",
            "gate-spend-map-v1 (sorted Merkle over redeemed job_id leaves)",
            "bind_tickets.unconsumed (IN_FLIGHT probe)",
        ],
        plain=(
            f"Absence/presence checked only inside Gate's redeemed-ticket spend map "
            f"({tree_size} leaves) plus unconsumed IN_FLIGHT tickets for this job_id — "
            f"not their PAS, not other networks."
        ),
        keys_checked={"job_id": job_id, "spend_phase": spend_phase, "tree_size": tree_size},
        as_of=as_of,
        counterparties=None,
    )


def for_clear_deny(*, payout_hash: str, denied: bool, count: int, as_of: str | None = None) -> dict:
    return build(
        boundary="gate_deny_registry",
        logs=["deny_entries.payout_hash (gate-deny-registry-v1)"],
        plain=(
            "DENIED/NOT DENIED checked only against Gate's append-only deny registry "
            "of sha256 payout fingerprints — not bank rails, not card networks."
        ),
        keys_checked={
            "payout_hash": payout_hash,
            "denied": denied,
            "deny_count": count,
        },
        as_of=as_of,
        counterparties=None,
    )


def for_seal(*, event_id: str, word: str, as_of: str | None = None) -> dict:
    return build(
        boundary="gate_bind_events_evidence_log",
        logs=[
            "bind_events (receipt_hash, receipt_signature)",
            "gate-evidence-log-v1 Merkle inclusion vs published evidence head",
        ],
        plain=(
            f"Seal word {word!r} checked only against Gate's bind_events receipt "
            f"chain and evidence Merkle log for this event_id — not a global custody claim."
        ),
        keys_checked={"event_id": event_id, "word": word},
        as_of=as_of,
    )


def for_go(
    *,
    rail: str,
    decision: str,
    signals: list[str],
    fingerprint: str,
    as_of: str | None = None,
) -> dict:
    return build(
        boundary="gate_prefinality_evaluate",
        logs=[
            "prefinality policy signals (rail/transfer/mandate)",
            "optional fuse_hop state when fuse_id presented",
            "Ed25519 JWT receipt mint (gate-prefinality-v1)",
        ],
        plain=(
            f"GO/NO_GO/HOLD for rail={rail} checked only against the presented "
            f"transfer fingerprint + mandate + optional fuse hop — clearance only, "
            f"no money moved."
        ),
        keys_checked={
            "rail": rail,
            "decision": decision,
            "fingerprint": fingerprint,
            "signals": list(signals or []),
        },
        time_window={
            "kind": "evaluation_instant_plus_receipt_ttl",
            "from": None,
            "to": as_of or _utc_now_iso(),
        },
        as_of=as_of,
        counterparties=None,
    )


def for_mouth(
    *,
    mouth_id: str,
    word: str,
    inputs: dict,
    logs: list[str] | None = None,
    counterparties: list[str] | None = None,
    plain: str | None = None,
    as_of: str | None = None,
) -> dict:
    return build(
        boundary=f"gate_mouth_{mouth_id.replace('-', '_')}",
        logs=logs
        or [
            f"presented operator flags for mouth {mouth_id}",
            "no external ledger scanned — advisory classification only",
        ],
        plain=plain
        or (
            f"Word {word!r} from mouth {mouth_id} checked only against the presented "
            f"flags in this request — not a scan of bank/card/PAS logs."
        ),
        keys_checked={"mouth_id": mouth_id, "word": word, "inputs": inputs},
        counterparties=counterparties,
        as_of=as_of,
        time_window={
            "kind": "advisory_instant",
            "from": None,
            "to": as_of or _utc_now_iso(),
        },
    )


def is_negative_word(word: str | None) -> bool:
    w = (word or "").strip().upper().replace("_", " ")
    # Normalize NO_GO → NO GO already via replace; also accept raw.
    if (word or "").strip().upper() in NEGATIVE_WORDS:
        return True
    return w in {x.replace("_", " ") for x in NEGATIVE_WORDS}


def sign_claim(body: dict) -> dict[str, Any]:
    """Attach claim_hash + claim_signature over canonical body including claim_scope.

    Mutates a copy: returns body with signing fields. Signing uses Gate receipt key.
    When keys missing, still returns claim_hash so scope is content-addressed.
    """
    out = dict(body)
    scope = out.get("claim_scope")
    if not isinstance(scope, dict):
        return out
    # Signed surface: stable subset — word/decision + scope + identifying keys.
    signed_obj = {
        "spec": CLAIM_SPEC,
        "mouth_spec": out.get("spec"),
        "word": out.get("word") or out.get("decision"),
        "claim_scope": scope,
        "job_id": out.get("job_id"),
        "event_id": out.get("event_id"),
        "payout_hash": out.get("payout_hash"),
        "rail": out.get("rail"),
        "evaluation_id": out.get("evaluation_id") or out.get("restraint_id"),
        "spend_phase": out.get("spend_phase") or out.get("write_state"),
    }
    canonical = _canonical(signed_obj)
    claim_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    sig = receipt_mod.sign_receipt_hash(claim_hash)
    # Keep any existing string `claim` (e.g. exclusion claim kind) intact.
    out["signed_claim"] = {
        "spec": CLAIM_SPEC,
        "claim_hash": claim_hash,
        "claim_signature": sig,
        "claim_public_key_fingerprint": receipt_mod.receipt_public_key_fingerprint(),
        "signed_over": "sha256(canonical_claim_json including claim_scope)",
        "canonical_claim": signed_obj,
    }
    return out


def attach(
    body: dict,
    *,
    scope: dict,
    force: bool = False,
) -> dict:
    """Attach claim_scope and sign when word is negative (or force=True)."""
    out = dict(body)
    out["claim_scope"] = scope
    word = out.get("word") or out.get("decision")
    if force or is_negative_word(str(word) if word is not None else ""):
        out = sign_claim(out)
    return out
