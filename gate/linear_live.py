"""Linear LIVE — LIVE is a linear resource: use once, cannot copy-paste permission.

Linear logic: some resources cannot be duplicated. Gate: a CHARGE-won
LIVE is not a screenshot you copy onto the next bind. Each irreversible
act needs its own mouth passage. Copycats treat LIVE like a boolean
they clone across jobs.

Gatekeep only to ourselves: Girard linear logic → non-copyable LIVE token.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

SPEC = "gate-linear-live-v1"
INVENTOR = "Nisaba LLC / Gate"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def consume(
    *,
    reuse_prior_live: bool | None = None,
    new_hop: bool | None = None,
    charge_id: str | None = None,
) -> dict[str, Any]:
    reuse = bool(reuse_prior_live)
    hop = True if new_hop is None else bool(new_hop)
    charge = bool((charge_id or "").strip())
    if reuse and hop and not charge:
        posture = "nonlinear_copy"
        claim = "live_token_cannot_be_duplicated_onto_next_hop"
    elif hop and charge:
        posture = "linear_consume"
        claim = "fresh_charge_for_this_act"
    else:
        posture = "no_token"
        claim = "dead_or_unevaluated"
    return {
        "spec": SPEC,
        "name": "Linear LIVE",
        "inventor": INVENTOR,
        "evaluated_at": _now(),
        "lineage": [
            "Jean-Yves Girard — linear logic (resources you cannot copy)",
            "Gate one married write per irreversible act",
        ],
        "reuse_prior_live": reuse,
        "new_hop": hop,
        "charge_present": charge,
        "posture": posture,
        "claim": claim,
        "thesis": "LIVE is linear. Screenshots of LIVE are not LIVE.",
        "gatekeep": "Proprietary linear-LIVE doctrine. Ours.",
        "their_production": False,
    }


def manifest(public_url: str) -> dict[str, Any]:
    base = (public_url or "").rstrip("/")
    return {
        "spec": SPEC,
        "name": "Linear LIVE",
        "inventor": INVENTOR,
        "example_copy": consume(reuse_prior_live=True, new_hop=True),
        "example_linear": consume(new_hop=True, charge_id="chg_1"),
        "live": f"{base}/.well-known/linear-live.json",
        "costliness": f"{base}/.well-known/costliness.json",
        "their_production": False,
    }
