"""Human-facing GO / NO_GO / HOLD over pre-finality evaluate.

Apple-simple words. Prefinality JWT + fail-closed underneath.
"""

from __future__ import annotations

from typing import Any, Callable

try:
    from gate import prefinality as prefinality_mod
except ImportError:
    import prefinality as prefinality_mod

SPEC = "gate-go-v1"

WORD_MAP = {
    "GO": {
        "word": "GO",
        "plain": "Yes. You may send this — right now.",
    },
    "NO_GO": {
        "word": "NO GO",
        "plain": "No. Don't send.",
    },
    "HOLD": {
        "word": "HOLD",
        "plain": "Wait. A person has to look first.",
    },
}


def clear_decision(decision: str) -> dict[str, str]:
    key = (decision or "").strip().upper().replace(" ", "_")
    if key == "NOGO":
        key = "NO_GO"
    return WORD_MAP.get(
        key,
        {"word": "NO GO", "plain": "No. Don't send."},
    )


def evaluate_go(
    body: dict,
    *,
    public_url: str,
    fuse_hop: Callable[[str], dict | None] | None = None,
    account_id: str | None = None,
) -> dict[str, Any]:
    raw = prefinality_mod.evaluate(
        body if isinstance(body, dict) else {},
        account_id=account_id,
        public_url=public_url,
        fuse_hop=fuse_hop,
    )
    label = clear_decision(raw.get("decision") or "NO_GO")
    return {
        "spec": SPEC,
        "word": label["word"],
        "plain": label["plain"],
        "decision": raw.get("decision"),
        "rail": raw.get("rail"),
        "halt": bool(raw.get("halt")),
        "signals": raw.get("signals") or [],
        "fingerprint": raw.get("fingerprint"),
        "evaluation_id": raw.get("restraint_id") or raw.get("evaluation_id"),
        "receipt": raw.get("receipt"),
        "expires_in": raw.get("expires_in"),
        "message": raw.get("message"),
        "claim_scope": raw.get("claim_scope"),
        "signed_claim": raw.get("signed_claim"),
        "write_state": raw.get("write_state"),
        "atoms": {
            "evaluate": "/demo/prefinality/evaluate",
            "verify": "/v1/prefinality/verify",
            "manifest": "/.well-known/prefinality.json",
        },
        "their_production": False,
        "demo": True,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Go",
        "promise": "You're about to send money. One word: allowed or not?",
        "words": ["GO", "NO GO", "HOLD"],
        "page": f"{base}/go",
        "api": f"{base}/v1/go",
        "rails": list(prefinality_mod.RAILS),
        "atoms": [
            "Pre-finality evaluate (fail closed)",
            "Ed25519 JWT receipt bound to transfer fingerprint",
        ],
        "their_production": False,
    }
