"""SSI Pre-Auth Path — authenticated settlement path before the trade date clock runs.

DTCC's #1 T+1 pain: stale SSIs, manual sharing, settlement fails. Gate's
equivalent on bind/payout: the exclusive door + license fuse + commit-auth
ticket is the pre-authenticated path — instruction must match the welded
identity before irreversible act. Not an ALERT clone. Same problem class:
wrong path, wrong entity, wrong account — caught before fail, not after.

Not cliche: we do not store SSIs. We refuse acts whose path is not pre-auth.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-ssi-preauth-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def path(
    *,
    ticket_ok: bool | None = None,
    license_fused: bool | None = None,
    parent_live: bool | None = None,
    exclusion_ok: bool | None = None,
) -> dict[str, Any]:
    t = bool(ticket_ok)
    fused = bool(license_fused)
    parent = bool(parent_live) if not fused else bool(parent_live)
    excl = True if exclusion_ok is None else bool(exclusion_ok)
    blockers = []
    if not t:
        blockers.append("ticket")
    if fused and not parent:
        blockers.append("license_parent")
    if not excl:
        blockers.append("exclusion")
    if blockers:
        posture = "unauthenticated_path"
        claim = "instruction_path_not_pre_auth_would_be_ssi_fail"
    else:
        posture = "pre_auth_path"
        claim = "welded_identity_matches_instruction"
    return {
        "spec": SPEC,
        "name": "SSI Pre-Auth Path",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "FMSB SSI standards · EU T+1 SSI task force — pre-populated authenticated paths",
            "Gate commit-auth + license fuse — path auth at hop, not email on trade date",
        ],
        "blockers": blockers,
        "posture": posture,
        "claim": claim,
        "thesis": "Settlement fails from wrong instructions. Pre-auth the path at the hop.",
        "gatekeep": "Proprietary SSI-preauth doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "SSI Pre-Auth Path",
        "inventor": INVENTOR,
        "example_ok": path(ticket_ok=True, license_fused=True, parent_live=True, exclusion_ok=True),
        "example_fail": path(ticket_ok=False, license_fused=True, parent_live=False),
        "live": f"{base}/.well-known/ssi-preauth.json",
        "commit_auth": f"{base}/.well-known/commit-auth.json",
        "their_production": False,
    }
