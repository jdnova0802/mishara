"""Proof of Restraint — PoR-shaped attestation of published nos.

Proof of Reserves: Merkle commitment to liabilities + asset coverage.
Gate inverse: Proof of Restraint — commitment to the inventory of nos
(HALT/BLOCK) this mouth actually printed. Partners verify inclusion of a
restraint event; observers see the head count — without PII.

Honest limit: proves published restraint events, not that every possible
door was covered (exclusive-door coverage is a separate claim).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-proof-restraint-v1"
INVENTOR = "Nisaba LLC / Gate"

try:
    from gate import restraint as restraint_mod
except ImportError:
    import restraint as restraint_mod


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def attest(public_url: str, *, limit: int = 200) -> dict[str, Any]:
    inv = restraint_mod.inventory(public_url, limit=limit)
    events = inv.get("events") or []
    # Lightweight commitment: hash-like fingerprint of event ids + receipt hashes
    import hashlib

    leaves = []
    for e in events:
        leaf = f"{e.get('event_id')}|{e.get('decision')}|{e.get('receipt_hash') or ''}"
        leaves.append(hashlib.sha256(leaf.encode()).hexdigest())
    root_input = "|".join(leaves) if leaves else "empty"
    root = hashlib.sha256(root_input.encode()).hexdigest()

    return {
        "spec": SPEC,
        "name": "Proof of Restraint",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Proof of Reserves — Merkle commitment to liabilities + coverage",
            "Gate restraint inventory — production HALT/BLOCK, no PII",
            "Certificate Transparency — public append-only evidence",
        ],
        "liabilities_analog": {
            "meaning": "Published nos are the 'liabilities' of restraint — promises that the write did not occur",
            "count": inv.get("count", 0),
            "commitment_root": root,
            "leaf_count": len(leaves),
        },
        "assets_analog": {
            "meaning": "Coverage = exclusive door + LIVE fuse path that can still print nos",
            "note": "This attestation does not by itself prove exclusive-door coverage of all bypasses.",
        },
        "restraint": inv.get("license_fuse") and f"{(public_url or '').rstrip('/')}/.well-known/restraint.json",
        "honest_limits": [
            "Proves published restraint events in this inventory snapshot",
            "Does not prove metaphysical absence of all spends elsewhere",
            "Does not prove every production door is welded",
        ],
        "thesis": "Show the nos like PoR shows the bags — citeable restraint, not vibes.",
        "gatekeep": "Proprietary PoR-inverse for mouth restraint. Ours.",
        "their_production": False,
        "pii": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = attest(base)
    body["live"] = f"{base}/.well-known/proof-restraint.json"
    body["restraint_inventory"] = f"{base}/.well-known/restraint.json"
    return body
