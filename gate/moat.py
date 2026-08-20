"""Moat Fingerprint — combinatorial uncopyability of the invention stack.

Copying one borrowed lens is easy. Copying the welded catalog — specs,
receipt attachments, well-known surfaces, inventor stamps, and cross-links —
is a different act. This module hashes the invention identity set so the
moat is machine-checkable: a fork missing pieces fails the fingerprint.
"""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any

SPEC = "gate-moat-v1"
INVENTOR = "Nisaba LLC / Gate"

try:
    from gate import inventions as inventions_mod
except ImportError:
    import inventions as inventions_mod


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def fingerprint(public_url: str = "") -> dict[str, Any]:
    man = inventions_mod.manifest(public_url or "https://gate.local")
    # Stable identity string: sorted spec ids
    specs = sorted(i["spec"] for i in man.get("inventions") or [])
    ids = sorted(i["id"] for i in man.get("inventions") or [])
    blob = "\n".join(specs) + "\n---\n" + "\n".join(ids) + f"\ninventor:{INVENTOR}"
    digest = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    return {
        "spec": SPEC,
        "name": "Moat Fingerprint",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "invention_count": man.get("count"),
        "specs": specs,
        "fingerprint_sha256": digest,
        "fingerprint_short": digest[:16],
        "claim": (
            "Combinatorial doctrine moat: partial clones fail fingerprint; "
            "full clone still lacks weld/CHARGE/production skin."
        ),
        "uncopyable_because": [
            "Welded combinations across Pearl/Searle/STIT/Innes/Ashby/Taleb/Schelling/…",
            "Machine artifacts on every receipt — not slide-deck philosophy",
            "Inventor stamp + gatekeep on every layer",
            "Operational coupling to CHARGE, epoch, license grip, exclusive door",
            "Fingerprint of the full catalog — missing one spec breaks the hash",
        ],
        "thesis": "Impossible to copy means: fingerprint mismatch OR skinless fork.",
        "gatekeep": "Meta-moat. The catalog is the product surface. Ours.",
        "their_production": False,
        "live_index": man.get("live"),
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    body = fingerprint(base)
    body["live"] = f"{base}/.well-known/moat.json"
    body["inventions"] = f"{base}/.well-known/inventions.json"
    return body
